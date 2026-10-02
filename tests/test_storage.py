"""Tests for the repository protocol's in-memory implementation (Phase 1, Task 1.4).

Phase 2 adds the JSON repository here and parametrizes these same behaviors
over both implementations (tasks/plan.md, Task 2.2).
"""

import pytest

from duewright.exceptions import TaskNotFoundError
from duewright.models import Task
from duewright.storage import InMemoryTaskRepository


def test_add_assigns_sequential_ids() -> None:
    repo = InMemoryTaskRepository()
    first = repo.add(Task(id=0, title="one"))
    second = repo.add(Task(id=0, title="two"))
    assert (first.id, second.id) == (1, 2)


def test_added_tasks_are_retrievable() -> None:
    repo = InMemoryTaskRepository()
    added = repo.add(Task(id=0, title="one"))
    assert repo.get(added.id) is added
    assert [t.title for t in repo.all()] == ["one"]


def test_get_unknown_id_returns_none() -> None:
    repo = InMemoryTaskRepository()
    assert repo.get(99) is None


def test_update_persists_changes() -> None:
    repo = InMemoryTaskRepository()
    task = repo.add(Task(id=0, title="one"))
    task.title = "renamed"
    assert repo.update(task).title == "renamed"
    assert repo.get(task.id).title == "renamed"


def test_update_unknown_id_raises() -> None:
    repo = InMemoryTaskRepository()
    with pytest.raises(TaskNotFoundError):
        repo.update(Task(id=99, title="ghost"))


def test_delete_reports_whether_the_task_existed() -> None:
    repo = InMemoryTaskRepository()
    task = repo.add(Task(id=0, title="one"))
    assert repo.delete(task.id) is True
    assert repo.delete(task.id) is False
    assert repo.all() == []


def test_ids_are_never_reused_after_deletes() -> None:
    repo = InMemoryTaskRepository()
    repo.add(Task(id=0, title="one"))
    repo.add(Task(id=0, title="two"))
    third = repo.add(Task(id=0, title="three"))
    repo.delete(third.id)
    repo.delete(2)
    assert repo.add(Task(id=0, title="four")).id == 4


def test_all_returns_creation_order() -> None:
    repo = InMemoryTaskRepository()
    for title in ("first", "second", "third"):
        repo.add(Task(id=0, title=title))
    assert [t.title for t in repo.all()] == ["first", "second", "third"]
