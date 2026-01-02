"""
Task dataclass model per data-model.md specification.

The Task entity represents a single unit of work to be tracked.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.exceptions import EmptyTitleError


@dataclass
class Task:
    """
    Represents a single todo task.

    Attributes:
        id: Unique identifier (positive integer, immutable after creation).
        title: Human-readable task name (required, non-empty).
        description: Extended task details (optional, defaults to empty string).
        completed: Whether the task is finished (defaults to False).
        created_at: Timestamp of task creation (immutable after creation).

    Invariants:
        - id MUST be a positive integer
        - id MUST be unique across all tasks
        - title MUST NOT be empty or whitespace-only
        - description MAY be empty but MUST NOT be None
        - completed MUST be exactly True or False
        - created_at MUST NOT change after creation
    """

    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate and normalize task attributes after initialization.

        Raises:
            EmptyTitleError: If title is empty or contains only whitespace.
        """
        # Validate and strip title
        if not self.title or not self.title.strip():
            raise EmptyTitleError()
        self.title = self.title.strip()

        # Strip description if present
        if self.description:
            self.description = self.description.strip()
