"""Business logic: the `TaskManager` service.

Owns every rule: validation on each mutation (callers are never trusted),
the smart sort, filters, search, completion timestamps, and stats. No I/O —
the interfaces print and serve; this module returns values or raises
(ADR-002).
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Callable, TypedDict

from duewright.exceptions import TaskNotFoundError, ValidationError
from duewright.models import Priority, Task
from duewright.storage import TaskRepository
from duewright.validation import (
    normalize_tags,
    validate_completed,
    validate_due_date,
    validate_priority,
    validate_title,
)

_PRIORITY_RANK: dict[Priority, int] = {
    Priority.HIGH: 0,
    Priority.MEDIUM: 1,
    Priority.LOW: 2,
}


class TaskStats(TypedDict):
    """The shape `TaskManager.stats` returns; the API mirrors it (Phase 4)."""

    total: int
    completed: int
    open: int
    overdue: int
    by_priority: dict[str, int]


def _smart_key(task: Task) -> tuple[bool, date, int]:
    """Dated tasks first by due date, then undated; ties by priority, high first."""
    return (task.due_date is None, task.due_date or date.max, _PRIORITY_RANK[task.priority])


def _due_key(task: Task) -> tuple[bool, date]:
    return (task.due_date is None, task.due_date or date.max)


def _priority_key(task: Task) -> tuple[int, str]:
    return (_PRIORITY_RANK[task.priority], task.title.lower())


def _created_key(task: Task) -> datetime:
    return task.created_at


_SORT_KEYS: dict[str, Callable[[Task], Any]] = {
    "smart": _smart_key,
    "due": _due_key,
    "priority": _priority_key,
    "created": _created_key,
}


def _filter_status(tasks: list[Task], status: str | None) -> list[Task]:
    """Keep open or done tasks; None keeps everything."""
    if status == "open":
        return [t for t in tasks if not t.completed]
    if status == "done":
        return [t for t in tasks if t.completed]
    return tasks


def _filter_priority(tasks: list[Task], priority: Priority | None) -> list[Task]:
    if priority is None:
        return tasks
    return [t for t in tasks if t.priority is priority]


def _filter_tag(tasks: list[Task], tag: str | None) -> list[Task]:
    """Blank tags filter nothing rather than matching nothing."""
    if not tag or not tag.strip():
        return tasks
    needle = tag.strip().lower()
    return [t for t in tasks if needle in t.tags]


def _filter_search(tasks: list[Task], search: str | None) -> list[Task]:
    """Case-insensitive substring match on the title; blank searches filter nothing."""
    if not search or not search.strip():
        return tasks
    needle = search.strip().lower()
    return [t for t in tasks if needle in t.title.lower()]


class TaskManager:
    """CRUD and queries over a TaskRepository, with the rules attached."""

    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    # -- mutations ------------------------------------------------------

    def add(
        self,
        title: str,
        priority: Priority = Priority.MEDIUM,
        due_date: date | None = None,
        tags: list[str] | None = None,
    ) -> Task:
        """Validate input, build a Task, and hand it to the repository."""
        task = Task(
            id=0,  # the repository assigns the real id
            title=validate_title(title),
            priority=validate_priority(priority),
            due_date=validate_due_date(due_date),
            tags=normalize_tags(tags or []),
        )
        return self._repo.add(task)

    def update(self, task_id: int, **changes: Any) -> Task:
        """Apply whitelisted, re-validated changes to an existing task.

        Every field is validated before any is applied, so a rejected value
        never leaves a half-updated task behind.
        """
        setters: dict[str, Callable[[Any], Any]] = {
            "title": validate_title,
            "priority": validate_priority,
            "due_date": validate_due_date,
            "tags": normalize_tags,
            "completed": validate_completed,
        }
        unknown = set(changes) - set(setters)
        if unknown:
            allowed = ", ".join(sorted(setters))
            raise ValidationError(
                f"Unknown field(s): {', '.join(sorted(unknown))}. Allowed: {allowed}."
            )
        task = self.get(task_id)
        validated = {name: setters[name](value) for name, value in changes.items()}
        for name, value in validated.items():
            setattr(task, name, value)
        self._sync_completion(task, changes)
        return self._repo.update(task)

    def complete(self, task_id: int) -> Task:
        """Mark a task done and stamp completed_at. Completing twice is safe."""
        return self.update(task_id, completed=True)

    def delete(self, task_id: int) -> None:
        """Remove a task; raises TaskNotFoundError when the id is unknown."""
        if not self._repo.delete(task_id):
            raise TaskNotFoundError(task_id)

    # -- queries --------------------------------------------------------

    def get(self, task_id: int) -> Task:
        """Return one task, or raise — callers never get None to check."""
        task = self._repo.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def list(
        self,
        status: str | None = None,
        priority: Priority | None = None,
        tag: str | None = None,
        search: str | None = None,
        sort_by: str = "smart",
    ) -> list[Task]:
        """Filter first, then sort. Text filters are case-insensitive."""
        if status not in (None, "open", "done"):
            raise ValidationError("status must be 'open', 'done', or omitted.")

        tasks = self._repo.all()
        tasks = _filter_status(tasks, status)
        tasks = _filter_priority(tasks, priority)
        tasks = _filter_tag(tasks, tag)
        tasks = _filter_search(tasks, search)
        return self._sorted(tasks, sort_by)

    def stats(self) -> TaskStats:
        """Summary counts: total, completed, open, overdue, by priority."""
        tasks = self._repo.all()
        by_priority = {p.value: 0 for p in Priority}
        completed = 0
        overdue = 0
        for task in tasks:
            if task.completed:
                completed += 1
            if task.is_overdue():
                overdue += 1
            by_priority[task.priority.value] += 1
        return {
            "total": len(tasks),
            "completed": completed,
            "open": len(tasks) - completed,
            "overdue": overdue,
            "by_priority": by_priority,
        }

    # -- helpers --------------------------------------------------------

    @staticmethod
    def _sync_completion(task: Task, changes: dict[str, Any]) -> None:
        """Keep completed_at consistent whenever `completed` changes."""
        if "completed" not in changes:
            return
        if task.completed and task.completed_at is None:
            task.completed_at = datetime.now(timezone.utc)
        elif not task.completed:
            task.completed_at = None

    @staticmethod
    def _sorted(tasks: list[Task], sort_by: str) -> list[Task]:
        key = _SORT_KEYS.get(sort_by)
        if key is None:
            options = ", ".join(sorted(_SORT_KEYS))
            raise ValidationError(f"Unknown sort {sort_by!r}; choose from: {options}.")
        return sorted(tasks, key=key)
