# Contributing to MCP Chaos

Prefer small, evidence-backed changes tied to a concrete failure mode or developer workflow. Behavioral changes need regression tests.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src tests
```

Prefer inspectable core logic over unnecessary dependencies.
