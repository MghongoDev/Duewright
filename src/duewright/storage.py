"""Storage: the `TaskRepository` protocol and its implementations.

The protocol is the seam between business logic and persistence (ADR-002):
`TaskManager` depends on this contract only, so the in-memory double used in
tests and the JSON file used in production (Phase 2) are interchangeable.

Contract notes:
- `add` assigns the id from a monotonically increasing counter; ids are never
  reused after deletions (ADR-003).
- `update` raises `TaskNotFoundError` for an unknown id; `delete` returns
  False instead — the service turns that into `TaskNotFoundError`.
- Implementations may return live objects; the service treats every method
  call as read-modify-write anyway.
"""

from __future__ import annotations

from typing import Protocol

from duewright.exceptions import TaskNotFoundError
from duewright.models import Task


class TaskRepository(Protocol):
    """Persistence contract. Implementations store Task objects by id."""

    def all(self) -> list[Task]:
        """Return every task, in creation order."""
        ...

    def get(self, task_id: int) -> Task | None:
        """Return the task with this id, or None when absent."""
        ...

    def add(self, task: Task) -> Task:
        """Store the task, assign its id, and return it."""
        ...

    def update(self, task: Task) -> Task:
        """Persist changes to an existing task and return it."""
        ...

    def delete(self, task_id: int) -> bool:
        """Remove the task; True when it existed, False otherwise."""
        ...


class InMemoryTaskRepository:
    """Dict-backed repository: the first implementation and the fast test double."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def all(self) -> list[Task]:
        return list(self._tasks.values())

    def get(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def add(self, task: Task) -> Task:
        task.id = self._next_id
        self._next_id += 1
        self._tasks[task.id] = task
        return task

    def update(self, task: Task) -> Task:
        if task.id not in self._tasks:
            raise TaskNotFoundError(task.id)
        self._tasks[task.id] = task
        return task

    def delete(self, task_id: int) -> bool:
        return self._tasks.pop(task_id, None) is not None
