"""Task entity model for todo items."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class Task(SQLModel, table=True):
    """
    Task entity representing a todo item.

    Attributes:
        id: Unique identifier (UUID)
        title: Task title (required, max 255 chars)
        description: Optional task description
        completed: Completion status (default: False)
        created_at: When the task was created
        updated_at: When the task was last modified
        version: Version for optimistic locking
        user_id: Foreign key to task owner
        owner: Relationship to User entity
    """

    __tablename__ = "task"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the task",
    )
    title: str = Field(
        max_length=255,
        description="Task title (required)",
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional task description",
    )
    completed: bool = Field(
        default=False,
        description="Completion status",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the task was created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the task was last modified",
    )
    version: int = Field(
        default=1,
        description="Version for optimistic locking",
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        index=True,
        description="Owner of the task",
    )

    # Relationship to user
    owner: Optional["User"] = Relationship(back_populates="tasks")
