from dataclasses import asdict, dataclass
from collections import Counter
from fnmatch import fnmatch
import json,time
class DroppedResponse(RuntimeError): pass
@dataclass(frozen=True)
class FaultRule:
    action:str; every:int=1; method:str='*'; start:int=1
    def __post_init__(self):
        if self.action not in {'drop','retryable','malformed','truncate'}: raise ValueError(f'unsupported chaos action: {self.action}')
        if self.every<1 or self.start<1: raise ValueError('every and start must be positive')
@dataclass(frozen=True)
class Profile:
    drop_every:int=0; malformed_every:int=0; truncate_every:int=0; retryable_every:int=0; latency_ms:int=0; rules:tuple[FaultRule,...]=()
@dataclass(frozen=True)
class ChaosEvent:
    call:int; method:str; method_call:int; action:str
    def as_dict(self): return asdict(self)
class ChaosProxy:
    def __init__(self,handler,profile): self.handler=handler; self.profile=profile; self.calls=0; self.method_calls=Counter(); self.events=[]
    def _action(self,method,method_call):
        for rule in self.profile.rules:
            if fnmatch(method,rule.method) and method_call>=rule.start and (method_call-rule.start+1)%rule.every==0: return rule.action
        for action,every in (('drop',self.profile.drop_every),('retryable',self.profile.retryable_every),('malformed',self.profile.malformed_every),('truncate',self.profile.truncate_every)):
            if every and self.calls%every==0:return action
        return None
    def __call__(self,req):
        self.calls+=1; method=str(req.get('method','')); self.method_calls[method]+=1; method_call=self.method_calls[method]
        if self.profile.latency_ms: time.sleep(self.profile.latency_ms/1000)
        action=self._action(method,method_call)
        if action:self.events.append(ChaosEvent(self.calls,method,method_call,action))
        if action=='drop': raise DroppedResponse(f'dropped call {self.calls} ({method})')
        if action=='retryable': return {'jsonrpc':'2.0','id':req.get('id'),'error':{'code':-32001,'message':'temporary chaos fault','retryable':True}}
        result=self.handler(req); wire=json.dumps(result,separators=(',',':'))
        if action=='malformed': return wire[:-1]+',BROKEN}'
        if action=='truncate': return wire[:max(1,len(wire)//2)]
        return result
def wrap(handler,profile): return ChaosProxy(handler,profile)
def echo_handler(req): return {'jsonrpc':'2.0','id':req.get('id'),'result':{'echo':req.get('params')}}


def run_stdio(reader, writer, handler, profile: Profile):
    """Proxy newline-delimited JSON-RPC requests through the chaos engine.

    This is intentionally transport-small: it can sit between an MCP stdio client
    and any callable server adapter without owning either process lifecycle.
    """
    proxy = wrap(handler, profile)
    processed = 0
    for raw in reader:
        line = raw.decode() if isinstance(raw, bytes) else raw
        if not line.strip():
            continue
        processed += 1
        try:
            request = json.loads(line)
            response = proxy(request)
            if isinstance(response, str):
                wire = response
            else:
                wire = json.dumps(response, separators=(",", ":"))
        except DroppedResponse:
            continue
        except Exception as exc:
            wire = json.dumps({"jsonrpc":"2.0","id":None,"error":{"code":-32700,"message":f"chaos proxy parse/error: {exc}"}}, separators=(",", ":"))
        writer.write(wire + "\n")
    return {"processed": processed, "emitted": processed - sum(1 for event in proxy.events if event.action == "drop"), "events": [event.__dict__ for event in proxy.events]}
