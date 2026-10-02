"""Tests for the pure validators (Phase 1, Task 1.3)."""

from datetime import date, datetime, timezone

import pytest

from duewright.exceptions import ValidationError
from duewright.models import Priority
from duewright.validation import (
    MAX_TAG_LENGTH,
    MAX_TITLE_LENGTH,
    normalize_tags,
    parse_due_date,
    validate_completed,
    validate_due_date,
    validate_priority,
    validate_title,
)


def test_validate_title_strips_surrounding_whitespace() -> None:
    assert validate_title("  Buy milk  ") == "Buy milk"


def test_validate_title_accepts_the_maximum_length() -> None:
    assert len(validate_title("a" * MAX_TITLE_LENGTH)) == MAX_TITLE_LENGTH


@pytest.mark.parametrize("bad", ["", "   ", "\n\t", "a" * (MAX_TITLE_LENGTH + 1)])
def test_validate_title_rejects_blank_and_overlong(bad: str) -> None:
    with pytest.raises(ValidationError):
        validate_title(bad)


def test_normalize_tags_lowercases_strips_and_dedupes_in_order() -> None:
    assert normalize_tags([" Home ", "HOME", "", "work", "  "]) == ["home", "work"]


def test_normalize_tags_rejects_an_overlong_tag() -> None:
    with pytest.raises(ValidationError):
        normalize_tags(["x" * (MAX_TAG_LENGTH + 1)])


def test_parse_due_date_accepts_iso_dates() -> None:
    assert parse_due_date("2026-10-01") == date(2026, 10, 1)


@pytest.mark.parametrize("bad", ["", "not-a-date", "2026-13-01", "01-10-2026", "2026/10/01"])
def test_parse_due_date_rejects_junk_with_a_friendly_message(bad: str) -> None:
    with pytest.raises(ValidationError, match="YYYY-MM-DD"):
        parse_due_date(bad)


def test_validate_priority_requires_the_enum() -> None:
    assert validate_priority(Priority.HIGH) is Priority.HIGH
    with pytest.raises(ValidationError):
        validate_priority("high")


def test_validate_due_date_requires_a_plain_date() -> None:
    assert validate_due_date(None) is None
    assert validate_due_date(date(2026, 10, 1)) == date(2026, 10, 1)
    with pytest.raises(ValidationError):
        validate_due_date(datetime(2026, 10, 1, tzinfo=timezone.utc))  # datetime, not date
    with pytest.raises(ValidationError):
        validate_due_date("2026-10-01")  # strings go through parse_due_date


def test_validate_completed_requires_a_bool() -> None:
    assert validate_completed(True) is True
    assert validate_completed(False) is False
    with pytest.raises(ValidationError):
        validate_completed(1)
