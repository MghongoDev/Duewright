# Task List: Duewright

*Index and checklist. Details, acceptance criteria, and verification live in
`tasks/plan.md`.*

## Phase 0: Foundation and design

- [x] 0.1 Scaffold uv package (`pyproject.toml` metadata, script entry)
- [x] 0.2 Dependencies (`uv add` runtime + dev groups, lockfile refreshed)
- [x] 0.3 Source layout + test scaffolding (all modules, placeholder test green)
- [x] 0.4 Design docs (ADR-001..005, idea one-pager)
- [x] 0.5 CI, `.gitignore`, README

### Checkpoint: Foundation

- [x] `uv run pytest` green, `uv run ruff check .` clean
- [x] `uv sync --locked` from a fresh state works
- [x] Design recorded in ADRs; no agent commits

## Phase 1: In-memory core

- [x] 1.1 Exceptions (`TodoError` hierarchy)
- [x] 1.2 Models (`Priority`, `Task`, injectable `is_overdue`, dict round-trips)
- [x] 1.3 Validation (title, tags, due date)
- [x] 1.4 Repository protocol + `InMemoryTaskRepository`
- [x] 1.5 `TaskManager` (CRUD, smart sort, filters, stats)

### Checkpoint: Core

- [x] REPL walkthrough passes; `uv run pytest` green

## Phase 2: Persistence

- [ ] 2.1 `JsonTaskRepository` (atomic writes, lock, version check, env override)
- [ ] 2.2 Service tests parametrized over both repositories

### Checkpoint: Persistence

- [ ] Restart round-trip works; corrupt file fails loudly, file untouched

## Phase 3: CLI

- [ ] 3.1 Menu loop, `ask()` helper, `print_tasks()`, top-level error handling
- [ ] CLI tests via monkeypatch + capsys

### Checkpoint: CLI (v0.1.0)

- [ ] Full flowchart loop works end to end; tag `v0.1.0`

## Phase 4: FastAPI

- [ ] 4.1 App skeleton, `/health`, `get_manager` DI
- [ ] 4.2 Pydantic schemas with examples
- [ ] 4.3 Routes (CRUD, `/stats` before `/{task_id}`, pagination)
- [ ] 4.4 Exception handlers, consistent JSON errors, logging
- [ ] 4.5 `TestClient` tests; 85%+ coverage
- [ ] 4.6 (optional) API-key gate on writes

### Checkpoint: API (v0.2.0)

- [ ] curl end-to-end works; coverage gate met; tag `v0.2.0`

## Phase 5: Ship

- [ ] 5.1 Dockerfile (uv, cached layers, non-root, single worker)
- [ ] 5.2 CI matrix + coverage + image build
- [ ] 5.3 Deploy, storage story, sample seed

### Checkpoint: Shipped (v1.0.0)

- [ ] Public `/health` OK; tag `v1.0.0`

## Phase 6: Portfolio polish

- [ ] 6.1 README, badges, screenshots, limitations
- [ ] 6.2 Stranger test from README alone
