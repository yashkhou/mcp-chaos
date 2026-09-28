import unittest
from mcp_chaos.core import FaultRule,Profile,echo_handler,wrap
class FaultPlanTests(unittest.TestCase):
    def test_method_scoped_rule(self):
        p=wrap(echo_handler,Profile(rules=(FaultRule('retryable',every=2,method='tools/*'),)))
        self.assertIn('result',p({'id':1,'method':'ping'})); self.assertIn('result',p({'id':2,'method':'tools/call'}))
        self.assertTrue(p({'id':3,'method':'tools/call'})['error']['retryable']); self.assertEqual(p.events[-1].method_call,2)
    def test_delayed_start_and_trace(self):
        p=wrap(echo_handler,Profile(rules=(FaultRule('truncate',method='x',start=3),)))
        self.assertIsInstance(p({'id':1,'method':'x'}),dict); self.assertIsInstance(p({'id':2,'method':'x'}),dict); self.assertIsInstance(p({'id':3,'method':'x'}),str)
        self.assertEqual(p.events[-1].as_dict()['action'],'truncate')
    def test_invalid_rule(self):
        with self.assertRaises(ValueError): FaultRule('corrupt')
if __name__=='__main__': unittest.main()
