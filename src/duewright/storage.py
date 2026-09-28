"""Storage: the `TaskRepository` protocol and its implementations.

Implemented across Phases 1-2 (tasks/plan.md, Tasks 1.4 and 2.1):

- `TaskRepository` — `typing.Protocol` contract: `all`, `get`, `add`, `update`, `delete`.
- `InMemoryTaskRepository` — dict plus counter; the fast test double.
- `JsonTaskRepository` — JSON file persistence (ADR-003): atomic writes via a
  temp file and `os.replace`, a `threading.RLock` around each read-modify-write,
  a `version` check on load, refusal to overwrite unparseable files, and a path
  overridable through `DUEWRIGHT_DATA_FILE`.
"""
