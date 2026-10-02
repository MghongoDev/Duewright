"""Domain model: the `Task` dataclass and `Priority` enum.

Stdlib only — no web imports in the core (ADR-002). Due dates are plain
calendar dates; timestamps are timezone-aware UTC. `is_overdue` takes `today`
as an injectable parameter, so tests never freeze the clock.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any


class Priority(str, Enum):
    """Task importance. The value is what gets stored on disk and in JSON."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    """A single to-do item. Fields and defaults match ADR-003."""

    id: int
    title: str
    priority: Priority = Priority.MEDIUM
    due_date: date | None = None
    tags: list[str] = field(default_factory=list)
    completed: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    def is_overdue(self, today: date | None = None) -> bool:
        """True when the task is open, dated, and its due date has passed.

        Due today is not overdue — the date must have passed. `today`
        defaults to the real clock but is injectable for tests.
        """
        today = today or date.today()
        return (not self.completed) and self.due_date is not None and self.due_date < today

    def to_dict(self) -> dict[str, Any]:
        """Serialize to the JSON shape in ADR-003 (dates and times as ISO strings)."""
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority.value,
            "due_date": self.due_date.isoformat() if self.due_date is not None else None,
            "tags": list(self.tags),
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at is not None else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """Rebuild a Task from `to_dict` output.

        Strict by design: every key must be present and every value must
        parse. Unknown priorities and malformed dates raise here; the JSON
        repository wraps that in StorageError (Phase 2) instead of trusting
        the file.
        """
        return cls(
            id=data["id"],
            title=data["title"],
            priority=Priority(data["priority"]),
            due_date=(
                date.fromisoformat(data["due_date"]) if data["due_date"] is not None else None
            ),
            tags=list(data["tags"]),
            completed=data["completed"],
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data["completed_at"] is not None
                else None
            ),
        )
