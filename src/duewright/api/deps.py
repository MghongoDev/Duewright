"""FastAPI dependencies: the cached `get_manager` provider.

Implemented in Phase 4 (tasks/plan.md, Task 4.1). One manager (and one
repository lock) is shared across requests; the data path comes from
`DUEWRIGHT_DATA_FILE`, defaulting to `data/tasks.json`. Tests replace it via
`app.dependency_overrides` — no monkeypatching.
"""
