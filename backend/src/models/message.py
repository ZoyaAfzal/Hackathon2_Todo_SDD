"""Message entity model for conversation messages."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlmodel import Column, Field, Relationship, SQLModel
from sqlalchemy import JSON


if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """
    Message entity representing a single message in a conversation.

    Attributes:
        id: Unique identifier (UUID)
        conversation_id: Foreign key to parent conversation
        role: Message author role (user or assistant)
        content: Message text content
        tool_calls: JSON of MCP tool invocations (nullable)
        sequence_number: Ordering position within conversation
        created_at: When the message was created
    """

    __tablename__ = "message"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the message",
    )
    conversation_id: uuid.UUID = Field(
        foreign_key="conversation.id",
        index=True,
        description="Parent conversation",
    )
    role: str = Field(
        max_length=20,
        description="Message role: user or assistant",
    )
    content: str = Field(
        description="Message text content",
    )
    tool_calls: Optional[list[dict[str, Any]]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="MCP tool invocations for this message",
    )
    sequence_number: int = Field(
        description="Ordering position within conversation",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the message was created",
    )

    # Relationship
    conversation: Optional["Conversation"] = Relationship(
        back_populates="messages"
    )
