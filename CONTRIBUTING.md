# Contributing

Chaos behavior must remain deterministic under a fixed request sequence. Add regression tests for new fault modes or scheduling semantics.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
