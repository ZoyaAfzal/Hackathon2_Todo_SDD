"""
SQLModel Database Models Template

This template provides the Phase III database models for the Todo AI Chatbot.
Copy and customize for your project.
"""

from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship


# ============================================================================
# Task Model
# ============================================================================

class TaskBase(SQLModel):
    """Base Task model for validation."""
    title: str
    description: Optional[str] = None


class Task(TaskBase, table=True):
    """Task database model.

    Fields:
        id: Primary key (auto-generated)
        user_id: Owner of the task (indexed for fast lookups)
        title: Task title
        description: Optional task description
        completed: Task completion status
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass


class TaskRead(TaskBase):
    """Schema for reading a task."""
    id: int
    user_id: str
    completed: bool
    created_at: datetime


class TaskUpdate(SQLModel):
    """Schema for updating a task (all fields optional)."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


# ============================================================================
# Conversation Model
# ============================================================================

class ConversationBase(SQLModel):
    """Base Conversation model."""
    pass


class Conversation(ConversationBase, table=True):
    """Conversation database model.

    Fields:
        id: Primary key (auto-generated)
        user_id: Owner of the conversation (indexed)
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # Relationship: One conversation has many messages
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationRead(ConversationBase):
    """Schema for reading a conversation."""
    id: int
    user_id: str
    created_at: datetime


# ============================================================================
# Message Model
# ============================================================================

class MessageBase(SQLModel):
    """Base Message model."""
    role: str  # "user" or "assistant"
    content: str


class Message(MessageBase, table=True):
    """Message database model.

    Fields:
        id: Primary key (auto-generated)
        user_id: Owner of the message (indexed)
        conversation_id: Foreign key to conversation
        role: "user" or "assistant"
        content: Message content
        created_at: Timestamp of creation
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship: Each message belongs to one conversation
    conversation: Optional[Conversation] = Relationship(back_populates="messages")


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    conversation_id: int


class MessageRead(MessageBase):
    """Schema for reading a message."""
    id: int
    user_id: str
    conversation_id: int
    created_at: datetime
