"""Conversation entity model for chat sessions."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .message import Message
    from .user import User


class Conversation(SQLModel, table=True):
    """
    Conversation entity representing a chat session.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to conversation owner
        title: Auto-generated from first message (first 50 chars)
        created_at: When the conversation started
        updated_at: When the last message was added
    """

    __tablename__ = "conversation"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the conversation",
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        index=True,
        description="Owner of the conversation",
    )
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Auto-generated title from first message",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the conversation started",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the last message was added",
    )

    # Relationships
    owner: Optional["User"] = Relationship()
    messages: List["Message"] = Relationship(back_populates="conversation")
