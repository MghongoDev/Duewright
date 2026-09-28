"""Pure validation helpers for task input.

Implemented in Phase 1 (tasks/plan.md, Task 1.3): `validate_title` (strip, 1-200
characters), `normalize_tags` (lowercase, strip, de-duplicate, drop empties, cap
length), and `parse_due_date` (ISO dates only, friendly `ValidationError`).

Rule (ADR-002): this module never calls `print()` or `input()`; it returns
values or raises exceptions.
"""
