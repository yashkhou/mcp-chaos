> [!IMPORTANT]
> **This project now lives in [agent-reliability-lab](https://github.com/yashkhou/agent-reliability-lab/tree/main/packages/mcp-chaos).** Its full history was moved there and this repository is archived.
>
> `pip install "git+https://github.com/yashkhou/agent-reliability-lab#subdirectory=packages/mcp-chaos"`


# mcp-chaos

Fault-injection middleware for JSON-RPC/MCP-style tool transports so clients can be tested against ugly network and protocol behavior.

## What it does

- injects deterministic dropped, malformed, truncated and retryable responses
- supports per-Nth-call fault profiles
- wraps a synchronous JSON-RPC handler without changing its business logic
- keeps faults explicit and reproducible for regression tests

## Quick start

```bash
PYTHONPATH=src python -m mcp_chaos examples/scenario.json
```

No model API, network service, or third-party package is required.

## Architecture

The chaos layer sits between a client request and a normal handler. A profile decides which deterministic fault applies to each call index; otherwise the request passes through untouched.

See [`docs/architecture.md`](docs/architecture.md) for the data model and trade-offs.

## V1 boundary

V1 models synchronous request/response behavior only; streaming and real socket faults belong in transport adapters.

## Development

```bash
python -m unittest discover -s tests -v
```

MIT licensed.


## v0.1.1

**Method-scoped deterministic fault plans.** Fault rules can target MCP method globs with independent call counters, delayed starts, deterministic cadence, and a trace of injected faults.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
