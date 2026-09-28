# ADR-002: Layered architecture — dataclasses in the core, adapters at the edges

## Status
Accepted

## Date
2026-09-28

## Context
The same CRUD operations must be reachable from a CLI and a REST API. Both interfaces
need the same validation, sorting, filtering, and stats. The classic failure mode is
logic leaking into the interface: `print()` inside the model, or FastAPI types inside
the service, after which testing the core needs a web server.

## Decision
Strict three-layer design with one-way imports:

```
cli / api   →   TaskManager (service)   →   TaskRepository (storage)  →  models
```

- The core (`models.py`, `validation.py`, `service.py`, `storage.py`) uses stdlib only:
  `dataclasses`, `enum`, `datetime`, `json`. It never imports FastAPI or Pydantic and
  never calls `print()` or `input()`. It returns values or raises exceptions.
- Interfaces are thin adapters. `cli.py` owns prompts and printing; `api/` owns Pydantic
  schemas, HTTP status codes, and exception handlers.
- The repository is a `typing.Protocol`, so `InMemoryTaskRepository` (tests, fast) and
  `JsonTaskRepository` (production) are interchangeable, and a later SQLite class can
  slot in without touching `service.py`.
- The manager re-validates everything. Callers are never trusted, so a bad API payload
  and a bad CLI input hit the same rules.

## Alternatives Considered

### Pydantic models everywhere
- Pros: one model library; less conversion code.
- Cons: couples the core to a web library; date/enum handling at the edge is already
  small; dataclasses keep the core honest and framework-free.
- Rejected: Pydantic stays in `api/schemas.py` only.

### One module, procedural functions
- Pros: fewer files for a small app.
- Cons: no seam for the repository; swapping storage or testing without I/O becomes
  surgery; the project's stated goal is practicing modular design.
- Rejected.

## Consequences
- Two serialization boundaries exist: `Task.to_dict/from_dict` for JSON storage, Pydantic
  schemas for the API. The mapping helper for `TaskRead` lives in one place.
- Tests run the service against the in-memory repo with no disk and no server; the same
  tests are later parametrized over the JSON repo.
- Slightly more code (protocol + adapters). Accepted; the abstraction is the portfolio
  point and is proven by the parametrized tests.
