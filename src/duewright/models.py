"""Domain model: the `Task` dataclass and `Priority` enum.

Implemented in Phase 1 (tasks/plan.md, Task 1.2). `Task.is_overdue(today)` takes
`today` as an injectable parameter so tests never freeze the clock. Dict
conversion (`to_dict`/`from_dict`) serializes dates and datetimes as ISO strings
and priorities as their string values — the on-disk shape in ADR-003.

Stdlib only: dataclasses, enum, datetime. No web imports in the core (ADR-002).
"""
