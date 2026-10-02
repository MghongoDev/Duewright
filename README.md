# Duewright

A task manager with one tested core and two interfaces: an interactive CLI and a
documented REST API, over the same business logic. Tasks sort by due date first,
priority second; overdue work is flagged; everything survives restarts.

**Status: Phase 1 - in-memory core.** The domain model, validators, repository
contract, and `TaskManager` are implemented and tested; persistence (Phase 2), the
CLI (Phase 3), and the API (Phase 4) build on them. See [tasks/plan.md](tasks/plan.md)
for the build order.

## Quick start

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
uv sync                # creates .venv and installs everything from uv.lock
uv run duewright       # CLI (placeholder until Phase 3)
uv run pytest          # run the tests
```

No manual virtualenv steps: `uv run` keeps the environment current before every command.

## Commands

| Command | Description |
|---------|-------------|
| `uv sync` | Install dependencies from the lockfile |
| `uv run duewright` | Run the CLI |
| `uv run pytest` | Run the test suite |
| `uv run pytest --cov=duewright` | Tests with coverage (target: 85%+) |
| `uv run ruff check .` | Lint |
| `uv run ruff format .` | Format |
| `uv run uvicorn duewright.api.main:app --reload` | Serve the API at `http://127.0.0.1:8000` (docs at `/docs`, Phase 4) |

## Architecture

One core, two thin adapters:

```
CLI (cli.py)      FastAPI routes (api/)
       \              /
        TaskManager (service.py)
                |
        TaskRepository (storage.py)  — protocol; JSON file today, SQLite later
                |
             Task (models.py)
```

The core is stdlib-only: no web imports, no printing. Validation happens at the
edges and again in the core. Data lives in `data/tasks.json` (override with
`DUEWRIGHT_DATA_FILE`), written atomically with a schema version.

Design decisions and their trade-offs live in [docs/decisions/](docs/decisions/) and 
the idea one-pager in [docs/ideas/duewright.md](docs/ideas/duewright.md).

## Known limitations

Deliberate MVP limits, named up front: single-process JSON storage (the CLI and API
should not write the same file at the same time), no user accounts, no recurring
tasks. The repository protocol exists so the storage answer can change without
touching business logic. See [docs/ideas/duewright.md](docs/ideas/duewright.md)
for the full not-doing list.
