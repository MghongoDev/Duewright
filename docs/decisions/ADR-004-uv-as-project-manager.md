# ADR-004: uv as project manager

## Status
Accepted

## Date
2026-09-28

## Context
The project needs a Python version pin, a virtual environment, runtime and dev
dependencies, a lockfile, a console-script install, and CI that reproduces the laptop
setup exactly. The guide names uv as the tool; the choice needs a recorded why.

## Decision
Use **uv** for everything project-related, and only uv:

- `uv init --package` created the `src`-layout package and `pyproject.toml`.
- `uv add` / `uv add --dev` are the only ways dependencies change. Dependencies are
  never hand-edited in `pyproject.toml`, and `uv.lock` is never hand-edited.
- `uv sync` creates `.venv` and installs the project in editable mode; no manual
  venv activation exists.
- `uv run <cmd>` prefixes every command (pytest, ruff, uvicorn, duewright) so the
  environment is verified first.
- `uv.lock` and `.python-version` are committed; `.venv/` is not.
- CI runs `uv sync --locked` so a lockfile that disagrees with `pyproject.toml` fails
  the build loudly.

## Alternatives Considered

### pip + requirements.txt + venv
- Pros: universal knowledge; zero new tools.
- Cons: no lockfile (or a hand-frozen one that rots); separate tools for versions,
  envs, and running; slow CI installs.
- Rejected.

### Poetry
- Pros: mature lockfile workflow.
- Cons: slower; another config dialect (`poetry` sections) next to standard
  `pyproject.toml` metadata; the guide and the learning roadmap standardize on uv.
- Rejected for consistency with the roadmap.

### Hand-managed `pyproject.toml` without a lockfile
- Pros: fewest files.
- Cons: CI, Docker, and clones resolve different versions — the classic "works on my
  machine" trap the brief explicitly calls out.
- Rejected.

## Consequences
- Reproducibility: a fresh clone runs `uv sync` and gets identical versions on laptop,
  CI, and Docker.
- Discipline: dependency changes go through `uv add` so the lockfile updates in the
  same action; `--locked` in CI and Docker catches drift.
- uv's release pace is fast; CI pins the action major (`astral-sh/setup-uv@v10`) but
  lets uv itself float with known checksums.
