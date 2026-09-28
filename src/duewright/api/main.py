"""FastAPI application factory: app, exception handlers, and the health check.

Implemented in Phase 4 (tasks/plan.md, Tasks 4.1 and 4.4). The app registers
central exception handlers mapping core exceptions to one JSON error shape:
`TaskNotFoundError` to 404, `ValidationError` to 422, `StorageError` to 500
with a generic message (details go to `logging`; file paths never reach the
client). Serves interactive docs at `/docs` (ADR-005).
"""
