import unittest

from mcp_chaos.core import FaultRule, Profile, echo_handler, wrap


class FaultPlanTests(unittest.TestCase):
    def test_method_scoped_rule_does_not_fault_other_methods(self):
        proxy = wrap(echo_handler, Profile(rules=(FaultRule("retryable", every=2, method="tools/*"),)))
        ok = proxy({"jsonrpc": "2.0", "id": 1, "method": "ping"})
        self.assertIn("result", ok)
        first = proxy({"jsonrpc": "2.0", "id": 2, "method": "tools/call"})
        self.assertIn("result", first)
        second = proxy({"jsonrpc": "2.0", "id": 3, "method": "tools/call"})
        self.assertTrue(second["error"]["retryable"])
        self.assertEqual(proxy.events[-1].method, "tools/call")
        self.assertEqual(proxy.events[-1].method_call, 2)

    def test_rule_start_delays_fault(self):
        proxy = wrap(echo_handler, Profile(rules=(FaultRule("truncate", every=1, method="x", start=3),)))
        self.assertIsInstance(proxy({"id": 1, "method": "x"}), dict)
        self.assertIsInstance(proxy({"id": 2, "method": "x"}), dict)
        self.assertIsInstance(proxy({"id": 3, "method": "x"}), str)
        self.assertEqual([e.action for e in proxy.events], ["truncate"])

    def test_invalid_rule_is_rejected(self):
        with self.assertRaises(ValueError):
            FaultRule("corrupt-everything")


if __name__ == "__main__":
    unittest.main()
