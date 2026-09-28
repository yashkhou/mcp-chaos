# Implementation note

Working V1 scope: Fault-injection middleware for JSON-RPC/MCP-style tool transports so clients can be tested against ugly network and protocol behavior.

Verified with `python -m unittest discover -s tests -v`.

Known boundary: V1 models synchronous request/response behavior only; streaming and real socket faults belong in transport adapters.
