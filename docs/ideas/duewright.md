# Duewright

*One-pager from the idea-refine pass. The source brief is the implementation guide;
the spec that carries the decisions forward is `SPEC.md` at the repo root.*

## Problem Statement

How might we turn the plain to-do exercise every portfolio has into proof of layered
design — one tested core that drives both a CLI and a documented REST API?

## Recommended Direction

Build a small task manager in strict layers and expose it twice. A pure-Python core
holds the model, the rules, and the storage contract. A JSON file persists tasks
behind a repository interface. A CLI menu and a FastAPI app each adapt that core,
and neither one holds business logic. The layers are the point: the same `TaskManager`
powers both, tests run against the repository abstraction, and the import direction
never reverses.

The name is **Duewright** — a tool that puts due dates to work. It sorts by due date
first, flags what is overdue, and keeps the list honest. The command and the package
are both `duewright`, so the project reads as one thing from README to import.

Why this direction and not another: a CLI alone proves nothing a tutorial hasn't
proved. A web app alone hides the design under frameworks. One core with two thin
interfaces shows judgment — protocol-based storage, validation at the edge,
re-validation in the core, atomic writes — in about 30 hours of free-tier work.

## Key Assumptions to Validate

- [ ] Solo builder, beginner-to-intermediate Python, 25-40 hours part-time — the guide's
      own framing; revisit if a phase runs double its estimate.
- [ ] A JSON file is enough persistence for the MVP, and single-process locking is an
      honest limitation to state, not hide. Test: can two threads write 100 tasks
      without loss? If yes, the design holds through v1.0.0.
- [ ] Free-tier hosting with ephemeral storage is acceptable for a demo if it is labeled.
      Test: deploy in Phase 5 and check what a restart costs.
- [ ] FastAPI's auto-docs and typed endpoints carry real weight with reviewers. Test:
      the Phase 4 checkpoint — a stranger creates a task from `/docs` unaided.

## MVP Scope

In: task fields (title, priority, optional due date, tags, completed flag, timestamps);
CRUD; the "smart" part (due-then-priority sort, filters, keyword search, overdue
detection, stats); JSON persistence with atomic writes and a schema version; the
interactive CLI; the FastAPI API with pagination and consistent errors; uv-managed
project; pytest, ruff, CI, Docker, one deploy.

Out: everything in the Not-Doing list below.

## Not Doing (and Why)

- **User accounts and auth** — no multi-user story exists to protect yet; it would add
  sessions, hashing, and per-user storage before one user exists. Returns after SQLite.
- **A database (SQLite/Postgres)** — the repository protocol already isolates storage;
  swapping backends later is a phase of work, not a rewrite. Adding it now would slow
  the first deploy without teaching anything new.
- **A web front end** — Swagger UI at `/docs` already shows the API visually. Building
  templates or a SPA would double the surface before the core is proven.
- **Recurring tasks and reminders** — scheduling and notification are separate systems
  with their own failure modes. Cut from the guide; revisit after v1.0.0.
- **Natural-language dates ("next Friday")** — friendly, but parser edge cases eat days.
  ISO dates (`2026-10-01`) are unambiguous and testable.
- **Sub-tasks and sharing** — they complicate the model and the API for features no
  early user has asked for.
- **Optional extras (rich tables, API-key gate)** — noted in the guide as polish and
  security tracks; deferred until the mandatory path is green and tagged.

## Open Questions

- Which free-tier host (Render, Fly.io, other) — decide in Phase 5 against current terms.
- Do the optional extras earn their place once v1.0.0 ships? Judge then, not now.
