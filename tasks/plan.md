# Implementation Plan: Duewright

## Overview

Duewright is a task manager with one tested core and two thin interfaces: an interactive
CLI and a FastAPI REST API over the same `TaskManager`, persisted to JSON behind a
repository protocol. Built with uv, tested with pytest, shipped with Docker, CI, and one
free-tier deploy.

## Capability Map

| Module | Responsibility | Depends on |
|---|---|---|
| `core` | `Task`, `Priority`, exceptions, pure validators | — |
| `storage` | `TaskRepository` protocol, InMemory + JSON repos, atomic writes | core |
| `service` | `TaskManager`: CRUD, filter, sort, stats | core, storage |
| `cli` | Interactive menu, input helpers, display | service |
| `api` | FastAPI routes, Pydantic schemas, DI | service |
| `delivery` | uv project, tests, CI, Docker, deploy | all |

Build order: core → storage → service → cli/api (in either order) → delivery.
Dependency arrows point one way; nothing in the core imports cli or api.

## Architecture Decisions

- Layered design: core never does I/O and never imports web libraries (ADR-002).
- JSON file with `version` and `next_id`, written atomically (ADR-003).
- uv for project, environment, and lockfile management (ADR-004).
- API versioned under `/api/v1`, thin Pydantic boundary (ADR-005).
- Name and identifiers: `duewright` everywhere (ADR-001).

## Task List

### Phase 0: Foundation and design (this deliverable)

- [x] Task 0.1: Scaffold uv package — `uv init --package --python 3.12`; set metadata
  (name, description, `requires-python = ">=3.11"`), `[project.scripts]
  duewright = "duewright.cli:main"`.
  - Acceptance: `pyproject.toml` carries the four metadata items.
  - Verify: `uv sync --locked` succeeds.
  - Files: `pyproject.toml`, `.python-version`, `src/duewright/__init__.py`.
- [x] Task 0.2: Dependencies — `uv add fastapi "uvicorn[standard]"`;
  `uv add --dev pytest pytest-cov httpx ruff radon`.
  - Acceptance: both groups present; `uv.lock` refreshed.
  - Verify: `uv sync --locked` succeeds; `uv run python -c "import fastapi"` works.
  - Files: `pyproject.toml`, `uv.lock`.
- [x] Task 0.3: Layout — create `exceptions.py`, `validation.py`, `models.py`,
  `storage.py`, `service.py`, `cli.py`, `api/` with docstring stubs; `tests/` with
  `conftest.py` and a placeholder test.
  - Acceptance: every module from the guide's structure exists.
  - Verify: `uv run pytest` passes; `uv run ruff check .` passes.
  - Files: `src/duewright/**`, `tests/**`.
- [x] Task 0.4: Design docs — ADR-001..005 and `docs/ideas/duewright.md`.
  - Acceptance: each ADR states decision, why, trade-off.
  - Verify: files exist and cross-reference the spec.
  - Files: `docs/decisions/*.md`, `docs/ideas/duewright.md`.
- [x] Task 0.5: CI — `.github/workflows/ci.yml` with `uv sync --locked`,
  `uv run ruff check .`, `uv run pytest`; plus `.gitignore` and README.
  - Acceptance: workflow steps mirror the guide.
  - Verify: the same three commands pass locally.
  - Files: `.github/workflows/ci.yml`, `.gitignore`, `README.md`.

### Checkpoint: Foundation (Phase 0 exit)

- [x] `uv run pytest` green; `uv run ruff check .` clean.
- [x] `uv sync --locked` works from a fresh state (delete `.venv/`, re-sync).
- [x] Design recorded in ADRs; user informed; no agent commits.

### Phase 1: In-memory core

- [x] Task 1.1: `exceptions.py` — `TodoError` base; `ValidationError`,
  `TaskNotFoundError`, `StorageError` subclasses.
  - Verify: import test asserts the hierarchy.
- [x] Task 1.2: `models.py` — `Priority` enum, `Task` dataclass with injectable
  `is_overdue(today)`, `to_dict`/`from_dict` with ISO round-trips.
  - Verify: `test_models.py` covers overdue edge cases and serialization round-trips.
- [x] Task 1.3: `validation.py` — `validate_title` (1-200 chars, stripped),
  `normalize_tags` (lowercase, dedupe, drop empties, cap length), `parse_due_date`.
  - Verify: `test_validation.py` (or folded into `test_models.py`) covers rejects.
- [x] Task 1.4: `storage.py` — `TaskRepository` protocol; `InMemoryTaskRepository`.
  - Verify: `test_storage.py::test_inmemory_*` passes.
- [x] Task 1.5: `service.py` — `TaskManager` with `add`, `get`, `list` (smart sort:
  dated first by due date, then undated, ties by priority high-first), `update`,
  `complete`, `delete`, `stats`.
  - Verify: `test_service.py` covers sort order, filters, search, overdue, unknown-ID
    error, title limits. REPL checkpoint per the guide.

### Checkpoint: Core

- [x] Full CRUD works from a REPL; `uv run pytest` green.

### Phase 2: Persistence

- [ ] Task 2.1: `JsonTaskRepository` — missing file = empty store; invalid JSON raises
  `StorageError` without touching the file; unknown `version` rejected; atomic write
  via temp file + `os.replace`; `RLock` around every public method; path overridable
  by `DUEWRIGHT_DATA_FILE`.
  - Verify: `test_storage.py` on `tmp_path` — restart round-trip, corrupt-file refusal,
    ID reuse prevention, two-thread hammering.
- [ ] Task 2.2: Parametrize the existing service tests over both repositories.
  - Verify: same tests pass against InMemory and JSON repos.

### Checkpoint: Persistence

- [ ] Script creates tasks, new process reads them back; corrupted file fails loudly.

### Phase 3: CLI

- [ ] Task 3.1: `cli.py` — menu loop (1 Add, 2 List, 3 Update, 4 Complete, 5 Delete,
  6 Search, 7 Stats, 0 Quit); `ask()` re-prompt helper; aligned `print_tasks()` with
  overdue flags; top-level error handling for `TaskNotFoundError`, `StorageError`,
  `KeyboardInterrupt`/`EOFError`.
  - Verify: `test_cli.py` via `monkeypatch` on `builtins.input` + `capsys` — happy path,
    bad-then-good date, delete of unknown ID.
- [ ] Checkpoint: tag `v0.1.0` (user commits/tags).

### Phase 4: FastAPI

- [ ] Task 4.1: App skeleton + `/health`; `deps.py` cached `get_manager`.
- [ ] Task 4.2: `schemas.py` — `TaskCreate`, `TaskUpdate`, `TaskRead` (+computed
  `is_overdue`), `TaskList`, `Stats` with examples.
- [ ] Task 4.3: `routes.py` — `GET/POST /api/v1/tasks`, `GET /stats` (declared before
  `/{task_id}`), `GET/PATCH /{task_id}`, `POST /{task_id}/complete`,
  `DELETE /{task_id}` (204); pagination applied post-filter with true `total`.
- [ ] Task 4.4: Exception handlers — 404/422/500 with one JSON shape; `logging`, no
  path leaks.
- [ ] Task 4.5: `test_api.py` via `TestClient` + `dependency_overrides`; coverage 85%+.
- [ ] Task 4.6 (optional): API-key gate on writes via `X-API-Key`,
  `secrets.compare_digest`, skipped when unset.
- [ ] Checkpoint: curl end-to-end per the guide; tag `v0.2.0` (user commits/tags).

### Phase 5: Ship

- [ ] Task 5.1: Dockerfile — uv-based, cached dependency layer, non-root user, single
  worker, `DUEWRIGHT_DATA_FILE=/data/tasks.json`.
- [ ] Task 5.2: CI matrix (3.11 + 3.12), coverage, optional image build.
- [ ] Task 5.3: Deploy to free-tier host; decide storage story; seed sample tasks.
- [ ] Checkpoint: public `/health` OK; tag `v1.0.0` (user commits/tags).

### Phase 6: Portfolio polish

- [ ] Task 6.1: README (pitch, demo links, badges, quickstarts, curl examples,
  limitations); consolidate decisions into ADR updates.
- [ ] Task 6.2: Stranger test — clone and run both interfaces from README alone.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Half-written file on crash | High — user data lost | Atomic writes (`os.replace`); never overwrite unparseable files; multi-thread tests |
| API requests interleave | High — lost updates | `RLock` in repository; `def` endpoints run in FastAPI's thread pool |
| Lockfile drift | Med — "works on my machine" | `uv add` only; commit `uv.lock`; `--locked` in CI and Docker |
| CLI and API share one file | Med — write conflicts | Document "don't run both on the same file"; separate dev paths |
| Time flakiness | Med — tests fail tomorrow | Inject `today`; UTC-aware datetimes; plain calendar `due_date` |
| Layer bleed | Med — the story collapses | Core never prints/inputs; api/cli import service, never reverse; ruff + review |
| Scope creep | High — 80% graveyard | Not-Doing list in `docs/ideas/duewright.md`; ship tagged versions |
| Ephemeral host storage | Low — demo resets | Label the demo; seed data on startup; revisit in Phase 5 |

## Open Questions

- Hosting choice (Phase 5) — check current free-tier terms before deciding.
- Optional extras (`rich`, API-key gate) — decide after the mandatory path is green.
