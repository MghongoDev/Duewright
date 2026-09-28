# ADR-001: Name and identifiers

## Status
Accepted

## Date
2026-09-28

## Context
The source brief calls the project "Smart To-Do Manager" with package `smart_todo` and
`SMART_TODO_*` environment variables. The name is generic: dozens of tutorial repos use
it, the import name says nothing, and every generated identifier reads as boilerplate.

## Decision
The project is named **Duewright**. Identifiers follow from it:

- Distribution and import name: `duewright`
- Console command: `duewright` (`[project.scripts] duewright = "duewright.cli:main"`)
- Environment variables: `DUEWRIGHT_DATA_FILE`, `DUEWRIGHT_API_KEY`
- Docker image and repo name: `duewright`

The name is one word, lowercase-safe, and free of hyphens, so the import name, the
command, and the repo name never disagree.

## Alternatives Considered

### Keep "smart-todo" / `smart_todo`
- Pros: matches the brief literally; no rename cost.
- Cons: generic; the "smart" claim outruns what v1.0.0 does (sort, filter, overdue
  flags); identifiers read as tutorial scaffolding.
- Rejected.

### Shorter command (`todo`)
- Pros: two syllables; the guide's own suggestion.
- Cons: collides with countless other `todo` commands and shadows nothing memorable;
  a portfolio reviewer typing `uv run todo` learns nothing about the project.
- Rejected in favor of the name that matches the project.

## Consequences
- Every file the brief names with a `smart_todo` prefix is created as `duewright`
  instead; the mapping is mechanical.
- If the GitHub repo is created later, it should be named `duewright` so clone URLs,
  the image name, and the package agree.
