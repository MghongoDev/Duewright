"""Pydantic v2 request/response schemas — the API boundary only.

Implemented in Phase 4 (tasks/plan.md, Task 4.2): `TaskCreate`, `TaskUpdate`,
`TaskRead` (with computed `is_overdue`), `TaskList`, and `Stats`, each with
`Field(examples=...)` so the auto-generated docs show realistic payloads.

Pydantic never crosses into the core; `Task` dataclasses and Pydantic models
are converted in one mapping helper.
"""
