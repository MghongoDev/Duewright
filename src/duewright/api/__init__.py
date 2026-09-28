"""FastAPI REST API layer.

Implemented in Phase 4 (tasks/plan.md, Tasks 4.1-4.6). The API is a thin adapter
over the same `TaskManager` the CLI uses (ADR-002). See `duewright.api.main`
for the app, `duewright.api.schemas` for Pydantic boundary models, and
`duewright.api.routes` for the `/api/v1` endpoints (ADR-005).
"""
