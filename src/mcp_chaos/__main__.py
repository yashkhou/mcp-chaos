import json,sys
from .core import *
s=json.load(open(sys.argv[1])); call=wrap(echo_handler,Profile(**s.get('profile',{})))
for req in s['requests']:
 try: print(json.dumps({'ok':True,'output':call(req)},default=str))
 except DroppedResponse as e: print(json.dumps({'ok':False,'error':str(e)}))
