"""User entity model for authentication."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .task import Task


class User(SQLModel, table=True):
    """
    User entity representing an authenticated user.

    Attributes:
        id: Unique identifier (UUID)
        email: User's email address (unique)
        password_hash: Securely hashed password
        created_at: When the user registered
        tasks: List of tasks owned by this user
    """

    __tablename__ = "user"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the user",
    )
    email: str = Field(
        max_length=255,
        unique=True,
        index=True,
        description="User's email address for authentication",
    )
    password_hash: str = Field(
        max_length=255,
        description="Securely hashed password",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the user registered",
    )

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="owner")
