"""Exception hierarchy for Duewright.

`TodoError` is the base: callers can catch every application error in one
place. The core raises these; interfaces map them to output — CLI messages,
API 404/422/500 (ADR-005). Nothing outside this module defines an error type.
"""

from __future__ import annotations


class TodoError(Exception):
    """Base class for every error Duewright raises on purpose."""


class ValidationError(TodoError):
    """Input broke a rule: empty title, bad date, unknown priority, and so on."""


class TaskNotFoundError(TodoError):
    """No task exists with the requested id."""


class StorageError(TodoError):
    """Data could not be read, parsed, or written safely."""
