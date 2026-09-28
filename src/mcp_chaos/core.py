from dataclasses import dataclass
import json,time
class DroppedResponse(RuntimeError): pass
@dataclass(frozen=True)
class Profile:
    drop_every:int=0; malformed_every:int=0; truncate_every:int=0; retryable_every:int=0; latency_ms:int=0

def wrap(handler,profile):
    state={'n':0}
    def call(req):
        state['n']+=1; n=state['n']
        if profile.latency_ms: time.sleep(profile.latency_ms/1000)
        if profile.drop_every and n%profile.drop_every==0: raise DroppedResponse(f'dropped call {n}')
        if profile.retryable_every and n%profile.retryable_every==0: return {'jsonrpc':'2.0','id':req.get('id'),'error':{'code':-32001,'message':'temporary chaos fault','retryable':True}}
        result=handler(req); wire=json.dumps(result,separators=(',',':'))
        if profile.malformed_every and n%profile.malformed_every==0: return wire[:-1]+',BROKEN}'
        if profile.truncate_every and n%profile.truncate_every==0: return wire[:max(1,len(wire)//2)]
        return result
    return call

def echo_handler(req): return {'jsonrpc':'2.0','id':req.get('id'),'result':{'echo':req.get('params')}}
