"""Chat API request and response schemas."""

import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for POST /api/{user_id}/chat."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Natural language message from user",
    )
    conversation_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Existing conversation ID to continue, or null for new",
    )


class ToolCallInfo(BaseModel):
    """Information about an MCP tool invocation."""

    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Response body for POST /api/{user_id}/chat."""

    conversation_id: uuid.UUID = Field(
        description="Conversation ID (new or existing)",
    )
    reply: str = Field(
        description="Assistant's response message",
    )
    tool_calls: list[ToolCallInfo] = Field(
        default_factory=list,
        description="MCP tools invoked during this turn",
    )


class ConversationSummary(BaseModel):
    """Summary of a conversation for listing."""

    id: uuid.UUID
    title: Optional[str] = None
    created_at: str
    updated_at: str


class MessageOut(BaseModel):
    """A single message in a conversation."""

    id: uuid.UUID
    role: str
    content: str
    tool_calls: Optional[list[ToolCallInfo]] = None
    sequence_number: int
    created_at: str


class MessageList(BaseModel):
    """Paginated message list response."""

    messages: list[MessageOut]
    has_more: bool = False
