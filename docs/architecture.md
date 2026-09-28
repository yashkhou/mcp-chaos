# Architecture

The chaos layer sits between a client request and a normal handler. A profile decides which deterministic fault applies to each call index; otherwise the request passes through untouched.

## Design constraints

- deterministic offline behavior
- explicit machine-readable inputs and outputs
- small standard-library surface area
- failures are surfaced rather than hidden

## V1 limitation

V1 models synchronous request/response behavior only; streaming and real socket faults belong in transport adapters.
