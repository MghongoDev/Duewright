# ADR-005: REST API design

## Status
Accepted

## Date
2026-09-28

## Context
Phase 4 exposes the core over HTTP. The API is the portfolio differentiator, so its
shape must be predictable: versioned paths, one error shape, honest status codes, and
docs generated from the code itself.

## Decision
FastAPI + Uvicorn, app at `duewright.api.main:app`, all task routes under an
`APIRouter` with `prefix="/api/v1"` and tag `tasks`:

| Method and path | Behavior | Success |
|---|---|---|
| `GET /health` | Liveness for CI and hosts | 200 |
| `GET /api/v1/tasks` | List; query params `status`, `priority`, `tag`, `q`, `sort`, `limit` (1-100, default 20), `offset` | 200 |
| `POST /api/v1/tasks` | Create from `TaskCreate` | 201 |
| `GET /api/v1/tasks/stats` | Summary counts | 200 |
| `GET /api/v1/tasks/{task_id}` | One task | 200 |
| `PATCH /api/v1/tasks/{task_id}` | Partial update (`exclude_unset`; explicit `null` clears due date) | 200 |
| `POST /api/v1/tasks/{task_id}/complete` | Mark done, set `completed_at` | 200 |
| `DELETE /api/v1/tasks/{task_id}` | Remove | 204 |

- **Versioning** — `/api/v1` in the path. A future breaking change gets `/api/v2`
  beside it instead of surprising clients.
- **Route order** — `/stats` is declared before `/{task_id}`; otherwise FastAPI parses
  `"stats"` as an ID and returns a confusing 422.
- **Errors** — every failure returns one JSON shape, `{"detail": "..."}`:
  `TaskNotFoundError` → 404, `ValidationError` → 422, `StorageError` → 500 with a
  generic message (details go to `logging`, never to the client; no file paths leak).
- **Pagination** — applied in the route after the manager returns the filtered, sorted
  list; `total` reflects the pre-slice count. Bounds: `limit` 1-100, default 20.
- **Schemas** — Pydantic v2 at the boundary only (`api/schemas.py`): `TaskCreate`,
  `TaskUpdate`, `TaskRead` (adds computed `is_overdue`), `TaskList`, `Stats`, with
  `Field(examples=...)` so `/docs` shows realistic payloads.
- **Sync endpoints** — routes are plain `def` (not `async def`) because file I/O is
  blocking; FastAPI runs them in a thread pool, which is what the repository lock
  (ADR-003) protects.
- **Dependency injection** — `deps.get_manager` (cached) provides the one manager;
  tests override it via `app.dependency_overrides` — no monkeypatching.
- **Security (optional, deferred to 4.6)** — if enabled, writes require `X-API-Key`
  compared with `secrets.compare_digest`, read from `DUEWRIGHT_API_KEY`; when unset,
  the gate is skipped for frictionless local dev. Reads stay public so reviewers can
  browse the demo. That trade-off will be recorded here when implemented.

## Alternatives Considered

### Unversioned paths (`/tasks`)
- Pros: shorter URLs.
- Cons: no escape hatch for a breaking change; the guide's whole point is a versioned,
  documented API.
- Rejected.

### HTTPException raised in every route
- Pros: no custom handlers.
- Cons: core exceptions (`TaskNotFoundError` et al.) would be caught (or leaked) in
  every route; handlers in `main.py` map them once.
- Rejected: central exception handlers.

### `async def` routes
- Pros: reads as modern.
- Cons: blocking file I/O inside the event loop stalls all requests — the exact bug the
  guide warns about.
- Rejected.

## Consequences
- `/docs` and `/openapi.json` come free and stay correct as schemas evolve.
- The route table above doubles as the test checklist for `test_api.py`.
- Error behavior is defined once and exercised by handler tests, not per route.
