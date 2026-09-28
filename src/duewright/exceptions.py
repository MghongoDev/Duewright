"""Exception hierarchy for Duewright.

Implemented in Phase 1 (tasks/plan.md, Task 1.1): a `TodoError` base class so
callers can catch every application error in one place, with `ValidationError`,
`TaskNotFoundError`, and `StorageError` subclasses.

The core raises these; interfaces map them to output (CLI messages, API 404/422/500).
"""
