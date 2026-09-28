# ADR-003: JSON data file shape, versioning, and atomic writes

## Status
Accepted

## Date
2026-09-28

## Context
Tasks must survive restarts. The store is a single file read and written by both the CLI
and the API, in a process that can die at any moment, and it will be replaced by a
database only after the MVP ships. Three failure modes must be designed against:
half-written files, silently overwritten data, and reused IDs.

## Decision
One JSON file (default `data/tasks.json`, overridable by `DUEWRIGHT_DATA_FILE`):

```json
{
  "version": 1,
  "next_id": 3,
  "tasks": [
    {
      "id": 1,
      "title": "Buy milk",
      "priority": "low",
      "due_date": "2026-10-01",
      "tags": ["home"],
      "completed": false,
      "created_at": "2026-09-28T09:00:00+00:00",
      "completed_at": null
    }
  ]
}
```

- **`version`** — every load checks it; an unknown value raises `StorageError`. No
  migration runs today, but the hook exists, so a schema change later is a new version
  plus a migration branch instead of a break.
- **`next_id`** — a stored counter handed out by the repository. IDs are never reused,
  even after deleting the newest task, because API clients and external links hold IDs.
- **Types on disk** — dates as `YYYY-MM-DD` (`date.isoformat`), timestamps as
  timezone-aware ISO strings in UTC, priority as the enum's string value. `completed_at`
  is `null` until completion.
- **Atomic writes** — write a temp file in the same directory, then `os.replace` it over
  the target. A crash mid-write leaves the old file intact, never a truncated one.
- **Refuse to destroy** — if the existing file cannot be parsed, raise `StorageError`
  (with the path in the message) and touch nothing. Never overwrite data the program
  could not read.
- **Locking** — a `threading.RLock` held across each public method, because every method
  is read-modify-write and FastAPI runs `def` endpoints in a thread pool.
- **Single process** — the lock protects threads within one process only. Running the
  CLI and API against the same file at the same time is unsupported and will be
  documented as a limitation. This constraint is also the future case for SQLite.

## Alternatives Considered

### SQLite from the start
- Pros: real transactions; solves multi-process access; no serialization code.
- Cons: hides file handling (a stated learning goal); heavier for a first deploy;
  the repository protocol makes it a later phase, not a rewrite.
- Deferred — `SqliteTaskRepository` is the first post-MVP item.

### Per-ID files or append-only log
- Pros: simpler writes.
- Cons: listing needs a directory scan or compaction; no atomic whole-store snapshot;
  more failure states.
- Rejected.

### Assign IDs as `max(existing) + 1`
- Pros: no counter field.
- Cons: reuses IDs after deleting the highest task — breaks external references.
- Rejected.

## Consequences
- The whole store loads on each access; fine for MVP scale (hundreds of tasks), a
  documented limit that motivates the database upgrade.
- Writers must hold the lock across the full read-modify-write cycle, not just the write.
- The corrupt-file test (bad JSON in, `StorageError` out, file untouched) is a standing
  regression test.
