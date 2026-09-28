import unittest,sys; sys.path.insert(0,'src')
from mcp_chaos.core import *
REQ={'jsonrpc':'2.0','id':1,'params':{'x':1}}
class T(unittest.TestCase):
 def test_pass(self): self.assertEqual(wrap(echo_handler,Profile())(REQ)['result']['echo'],{'x':1})
 def test_drop(self):
  with self.assertRaises(DroppedResponse): wrap(echo_handler,Profile(drop_every=1))(REQ)
 def test_retryable(self): self.assertTrue(wrap(echo_handler,Profile(retryable_every=1))(REQ)['error']['retryable'])
