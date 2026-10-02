"""Tests for the TaskManager service (Phase 1, Task 1.5)."""

from datetime import date, datetime, timedelta, timezone

import pytest

from duewright.exceptions import TaskNotFoundError, ValidationError
from duewright.models import Priority
from duewright.service import TaskManager
from duewright.storage import InMemoryTaskRepository

FROZEN_NOW = datetime(2026, 10, 2, 12, 0, tzinfo=timezone.utc)


class _FrozenDatetime(datetime):
    """Stand-in for service.datetime so completion stamps are deterministic."""

    @classmethod
    def now(cls, tz: timezone | None = None) -> datetime:
        return FROZEN_NOW


@pytest.fixture()
def frozen_clock(monkeypatch: pytest.MonkeyPatch) -> datetime:
    monkeypatch.setattr("duewright.service.datetime", _FrozenDatetime)
    return FROZEN_NOW


def make_manager() -> TaskManager:
    return TaskManager(InMemoryTaskRepository())


# -- add and list ------------------------------------------------------


def test_add_then_list_returns_the_task() -> None:
    manager = make_manager()
    manager.add("Buy milk", Priority.LOW, tags=["Home", "home "])
    tasks = manager.list()
    assert len(tasks) == 1
    assert tasks[0].title == "Buy milk"
    assert tasks[0].priority is Priority.LOW
    assert tasks[0].tags == ["home"]


def test_add_defaults_priority_to_medium() -> None:
    manager = make_manager()
    assert manager.add("Buy milk").priority is Priority.MEDIUM


def test_add_rejects_a_blank_title() -> None:
    manager = make_manager()
    with pytest.raises(ValidationError):
        manager.add("   ")


def test_add_rejects_an_overlong_title() -> None:
    manager = make_manager()
    with pytest.raises(ValidationError):
        manager.add("x" * 500)


def test_add_rejects_a_string_priority() -> None:
    manager = make_manager()
    with pytest.raises(ValidationError):
        manager.add("Buy milk", "high")


def test_add_rejects_a_string_due_date() -> None:
    manager = make_manager()
    with pytest.raises(ValidationError):
        manager.add("Buy milk", due_date="2026-10-01")


# -- smart sort --------------------------------------------------------


def test_smart_sort_puts_dated_tasks_first_then_undated() -> None:
    manager = make_manager()
    manager.add("undated")
    manager.add("due later", due_date=date(2026, 10, 5))
    manager.add("due soon", due_date=date(2026, 10, 1))
    assert [t.title for t in manager.list()] == ["due soon", "due later", "undated"]


def test_smart_sort_breaks_due_date_ties_by_priority_high_first() -> None:
    manager = make_manager()
    manager.add("low", Priority.LOW, due_date=date(2026, 10, 1))
    manager.add("high", Priority.HIGH, due_date=date(2026, 10, 1))
    manager.add("medium", Priority.MEDIUM, due_date=date(2026, 10, 1))
    assert [t.title for t in manager.list()] == ["high", "medium", "low"]


def test_priority_sort_ignores_due_dates() -> None:
    manager = make_manager()
    manager.add("low", Priority.LOW)
    manager.add("high", Priority.HIGH, due_date=date(2026, 10, 1))
    assert [t.title for t in manager.list(sort_by="priority")] == ["high", "low"]


def test_unknown_sort_raises_with_the_options() -> None:
    manager = make_manager()
    with pytest.raises(ValidationError, match="smart"):
        manager.list(sort_by="vibes")


# -- filters ------------------------------------------------------------


def test_filter_by_tag_is_case_insensitive() -> None:
    manager = make_manager()
    manager.add("Buy milk", tags=["home"])
    manager.add("Ship release", tags=["work"])
    assert [t.title for t in manager.list(tag="HOME")] == ["Buy milk"]
    assert manager.list(tag="nope") == []


def test_search_is_a_case_insensitive_substring_match() -> None:
    manager = make_manager()
    manager.add("Write the README")
    manager.add("Buy milk")
    assert [t.title for t in manager.list(search="readme")] == ["Write the README"]
    assert manager.list(search="zzz") == []


def test_filter_by_status() -> None:
    manager = make_manager()
    done = manager.add("done thing")
    manager.add("open thing")
    manager.complete(done.id)
    assert [t.title for t in manager.list(status="done")] == ["done thing"]
    assert [t.title for t in manager.list(status="open")] == ["open thing"]
    with pytest.raises(ValidationError):
        manager.list(status="finished")


def test_filters_combine() -> None:
    manager = make_manager()
    manager.add("Ship release", Priority.HIGH, tags=["work"])
    manager.add("Ship docs", Priority.LOW, tags=["work"])
    manager.add("Buy milk", Priority.HIGH, tags=["home"])
    titles = [t.title for t in manager.list(priority=Priority.HIGH, tag="work", search="ship")]
    assert titles == ["Ship release"]


# -- get, update, complete, delete ---------------------------------------


def test_get_unknown_id_raises_task_not_found() -> None:
    manager = make_manager()
    with pytest.raises(TaskNotFoundError):
        manager.get(99)


def test_update_changes_only_the_given_fields() -> None:
    manager = make_manager()
    task = manager.add("Buy milk", Priority.LOW, due_date=date(2026, 10, 1), tags=["home"])
    updated = manager.update(task.id, title="Buy oat milk")
    assert updated.title == "Buy oat milk"
    assert updated.priority is Priority.LOW
    assert updated.due_date == date(2026, 10, 1)
    assert updated.tags == ["home"]


def test_update_rejects_unknown_fields() -> None:
    manager = make_manager()
    task = manager.add("Buy milk")
    with pytest.raises(ValidationError, match="notes"):
        manager.update(task.id, notes="call mum")
    assert manager.get(task.id).title == "Buy milk"


def test_update_rejects_invalid_values_without_partial_mutation() -> None:
    manager = make_manager()
    task = manager.add("Buy milk", tags=["home"])
    with pytest.raises(ValidationError):
        manager.update(task.id, tags=["work"], title="  ")
    assert manager.get(task.id).tags == ["home"]  # nothing was applied


def test_update_can_clear_the_due_date() -> None:
    manager = make_manager()
    task = manager.add("Buy milk", due_date=date(2026, 10, 1))
    assert manager.update(task.id, due_date=None).due_date is None


def test_update_unknown_id_raises_task_not_found() -> None:
    manager = make_manager()
    with pytest.raises(TaskNotFoundError):
        manager.update(99, title="ghost")


def test_complete_stamps_completed_at(frozen_clock: datetime) -> None:
    manager = make_manager()
    task = manager.add("Ship it")
    done = manager.complete(task.id)
    assert done.completed is True
    assert done.completed_at == frozen_clock


def test_complete_is_idempotent(frozen_clock: datetime) -> None:
    manager = make_manager()
    task = manager.add("Ship it")
    manager.complete(task.id)
    assert manager.complete(task.id).completed_at == frozen_clock


def test_reopening_clears_completed_at(frozen_clock: datetime) -> None:
    manager = make_manager()
    task = manager.add("Ship it")
    manager.complete(task.id)
    reopened = manager.update(task.id, completed=False)
    assert reopened.completed is False
    assert reopened.completed_at is None


def test_delete_removes_and_a_second_delete_raises() -> None:
    manager = make_manager()
    task = manager.add("Buy milk")
    manager.delete(task.id)
    assert manager.list() == []
    with pytest.raises(TaskNotFoundError):
        manager.delete(task.id)


# -- stats ---------------------------------------------------------------


def test_stats_counts_everything() -> None:
    manager = make_manager()
    manager.add("overdue", Priority.HIGH, due_date=date.today() - timedelta(days=1))
    manager.add("open", Priority.MEDIUM)
    done = manager.add("done", Priority.LOW, due_date=date.today() - timedelta(days=1))
    manager.complete(done.id)
    assert manager.stats() == {
        "total": 3,
        "completed": 1,
        "open": 2,
        "overdue": 1,  # the completed task's past due date does not count
        "by_priority": {"low": 1, "medium": 1, "high": 1},
    }


def test_stats_on_an_empty_store_are_zero() -> None:
    manager = make_manager()
    assert manager.stats() == {
        "total": 0,
        "completed": 0,
        "open": 0,
        "overdue": 0,
        "by_priority": {"low": 0, "medium": 0, "high": 0},
    }
