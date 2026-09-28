import io, json, unittest
from mcp_chaos.core import FaultRule, Profile, echo_handler, run_stdio

class StdioIntegrationTests(unittest.TestCase):
    def test_faults_real_ndjson_stream(self):
        reader=io.StringIO('\n'.join(json.dumps({'jsonrpc':'2.0','id':i,'method':'tools/call','params':{'n':i}}) for i in range(1,4))+'\n')
        writer=io.StringIO()
        report=run_stdio(reader, writer, echo_handler, Profile(rules=(FaultRule('retryable', every=2, method='tools/*'),)))
        rows=[json.loads(x) for x in writer.getvalue().splitlines()]
        self.assertEqual(len(rows),3)
        self.assertIn('result',rows[0]); self.assertIn('error',rows[1]); self.assertIn('result',rows[2])
        self.assertEqual(report['events'][0]['method_call'],2)

    def test_drop_suppresses_wire_response(self):
        reader=io.StringIO(json.dumps({'id':1,'method':'x'})+'\n')
        writer=io.StringIO()
        report=run_stdio(reader,writer,echo_handler,Profile(rules=(FaultRule('drop',method='x'),)))
        self.assertEqual(writer.getvalue(),'')
        self.assertEqual(report['emitted'],0)

if __name__=='__main__': unittest.main()
