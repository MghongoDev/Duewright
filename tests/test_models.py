"""Tests for the Task model and Priority enum (Phase 1, Task 1.2)."""

from datetime import date, datetime, timezone
from typing import Any

import pytest

from duewright.models import Priority, Task


def make_task(**overrides: Any) -> Task:
    """A fully specified Task so tests compare against known values."""
    values: dict[str, Any] = {
        "id": 1,
        "title": "Write the spec",
        "priority": Priority.MEDIUM,
        "due_date": date(2026, 10, 1),
        "tags": ["docs"],
        "completed": False,
        "created_at": datetime(2026, 9, 28, 9, 0, tzinfo=timezone.utc),
        "completed_at": None,
    }
    values.update(overrides)
    return Task(**values)


def test_new_task_defaults() -> None:
    task = Task(id=1, title="Buy milk")
    assert task.priority is Priority.MEDIUM
    assert task.due_date is None
    assert task.tags == []
    assert task.completed is False
    assert task.completed_at is None
    assert task.created_at.tzinfo is not None  # timestamps are timezone-aware


def test_priority_values_are_the_strings_stored_on_disk() -> None:
    assert Priority.HIGH.value == "high"
    assert Priority("medium") is Priority.MEDIUM


@pytest.mark.parametrize(
    ("due_date", "completed", "expected"),
    [
        (date(2026, 10, 1), False, True),  # due date has passed
        (date(2026, 10, 2), False, False),  # due today is not overdue
        (date(2026, 10, 3), False, False),  # due in the future
        (date(2026, 10, 1), True, False),  # completed tasks are never overdue
        (None, False, False),  # undated tasks are never overdue
    ],
)
def test_is_overdue(due_date: date | None, completed: bool, expected: bool) -> None:
    task = make_task(due_date=due_date, completed=completed)
    assert task.is_overdue(today=date(2026, 10, 2)) is expected


def test_is_overdue_accepts_injected_today() -> None:
    task = make_task(due_date=date(2026, 10, 1))
    assert task.is_overdue(today=date(2026, 9, 30)) is False
    assert task.is_overdue(today=date(2026, 10, 2)) is True


def test_to_dict_shape() -> None:
    data = make_task(
        priority=Priority.LOW,
        completed=True,
        completed_at=datetime(2026, 10, 2, 12, 30, tzinfo=timezone.utc),
    ).to_dict()
    assert data == {
        "id": 1,
        "title": "Write the spec",
        "priority": "low",
        "due_date": "2026-10-01",
        "tags": ["docs"],
        "completed": True,
        "created_at": "2026-09-28T09:00:00+00:00",
        "completed_at": "2026-10-02T12:30:00+00:00",
    }


def test_to_dict_uses_null_for_missing_values() -> None:
    data = make_task(due_date=None, completed_at=None).to_dict()
    assert data["due_date"] is None
    assert data["completed_at"] is None


def test_dict_round_trip_returns_an_equal_task() -> None:
    task = make_task(
        completed=True,
        completed_at=datetime(2026, 10, 2, 12, 30, tzinfo=timezone.utc),
        tags=["home", "errands"],
    )
    assert Task.from_dict(task.to_dict()) == task


def test_from_dict_rejects_unknown_priority() -> None:
    data = make_task().to_dict()
    data["priority"] = "urgent"
    with pytest.raises(ValueError):
        Task.from_dict(data)


def test_from_dict_rejects_missing_fields() -> None:
    data = make_task().to_dict()
    del data["title"]
    with pytest.raises(KeyError):
        Task.from_dict(data)
