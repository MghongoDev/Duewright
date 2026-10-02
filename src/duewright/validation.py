"""Pure validation helpers for task input.

Every function returns a cleaned value or raises `ValidationError` — no
printing, no prompting (ADR-002). The CLI re-prompts around these; the API
maps `ValidationError` to 422 (ADR-005).

Naming: `validate_*` checks a value and returns it typed; `parse_due_date`
turns a string into a date. String cleanup (title, tags) is also done here so
every entry point cleans identically.
"""

from __future__ import annotations

from datetime import date, datetime

from duewright.exceptions import ValidationError
from duewright.models import Priority

MAX_TITLE_LENGTH = 200
MAX_TAG_LENGTH = 50


def validate_title(raw: str) -> str:
    """Strip surrounding whitespace and enforce 1-200 characters."""
    title = raw.strip()
    if not title:
        raise ValidationError("Title cannot be empty.")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError(f"Title cannot exceed {MAX_TITLE_LENGTH} characters.")
    return title


def normalize_tags(tags: list[str]) -> list[str]:
    """Lowercase, strip, drop empties, and de-duplicate, keeping first-seen order.

    A tag longer than `MAX_TAG_LENGTH` characters is rejected rather than
    silently truncated — truncation would change what the user asked for.
    """
    cleaned: list[str] = []
    for raw in tags:
        tag = raw.strip().lower()
        if not tag:
            continue
        if len(tag) > MAX_TAG_LENGTH:
            raise ValidationError(f"Tag {tag!r} cannot exceed {MAX_TAG_LENGTH} characters.")
        if tag not in cleaned:
            cleaned.append(tag)
    return cleaned


def parse_due_date(raw: str) -> date:
    """Parse an ISO date string (YYYY-MM-DD); raise a friendly error otherwise."""
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise ValidationError(
            f"Invalid due date {raw!r}; use YYYY-MM-DD (for example 2026-10-01)."
        ) from exc


def validate_priority(value: object) -> Priority:
    """Require a Priority member. Coercion from strings happens at the interfaces."""
    if not isinstance(value, Priority):
        raise ValidationError("priority must be a Priority value (low, medium, or high).")
    return value


def validate_due_date(value: object) -> date | None:
    """Require None or a plain calendar date; reject datetime and strings."""
    if value is None:
        return None
    if isinstance(value, datetime) or not isinstance(value, date):
        raise ValidationError("due_date must be a datetime.date or None.")
    return value


def validate_completed(value: object) -> bool:
    """Require a real bool; 1 and 0 are not accepted."""
    if not isinstance(value, bool):
        raise ValidationError("completed must be true or false.")
    return value
