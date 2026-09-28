"""REST endpoints under `/api/v1` (ADR-005).

Implemented in Phase 4 (tasks/plan.md, Task 4.3): list with filters, sort,
and pagination; create; get; patch; complete; delete; and stats. `/stats` is
declared before `/{task_id}` so the literal path wins over the ID converter.
Endpoints are plain `def` (blocking file I/O runs in FastAPI's thread pool,
where the repository lock protects read-modify-write cycles).
"""
