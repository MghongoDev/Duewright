"""Tests for the exception hierarchy (Phase 1, Task 1.1)."""

import pytest

from duewright.exceptions import (
    StorageError,
    TaskNotFoundError,
    TodoError,
    ValidationError,
)


def test_every_application_error_is_a_todo_error() -> None:
    assert issubclass(TodoError, Exception)
    assert issubclass(ValidationError, TodoError)
    assert issubclass(TaskNotFoundError, TodoError)
    assert issubclass(StorageError, TodoError)


def test_todo_error_catches_every_application_error() -> None:
    with pytest.raises(TodoError):
        raise TaskNotFoundError(7)
