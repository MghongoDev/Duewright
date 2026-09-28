"""Business logic: the `TaskManager` service.

Implemented in Phase 1 (tasks/plan.md, Task 1.5). `TaskManager(repo)` owns the
rules: validation on every mutation (callers are never trusted), the "smart"
sort (dated tasks first by due date, then undated, ties broken by priority,
high first), filtering by status/priority/tag, case-insensitive search,
completion timestamps, and summary stats.

Rule (ADR-002): no `print()` or `input()` here. The CLI and API adapters own I/O.
"""
