# OpenAI Agents SDK + MCP Integration - Code Examples

This document provides complete, working code examples for building AI agents with OpenAI Agents SDK and MCP tool orchestration.

## Table of Contents

1. [Complete Todo Agent Example](#1-complete-todo-agent-example)
2. [Multi-Provider Model Factory](#2-multi-provider-model-factory)
3. [MCP Server with Tools](#3-mcp-server-with-tools)
4. [FastAPI Streaming Endpoint](#4-fastapi-streaming-endpoint)
5. [Database Models and Services](#5-database-models-and-services)
6. [Testing Examples](#6-testing-examples)

---

## 1. Complete Todo Agent Example

### File: `agent_config/todo_agent.py`

```python
"""
TodoAgent - AI assistant for task management (Phase III).

This module defines the TodoAgent class using OpenAI Agents SDK.
The agent connects to a separate MCP server process via MCPServerStdio
and accesses task management tools through the MCP protocol.

Architecture:
- MCP Server: Separate process exposing task tools via FastMCP
- Agent: Connects to MCP server via stdio transport
- Tools: Available through MCP protocol (not direct imports)
"""

import os
from pathlib import Path

from agents import Agent
from agents.mcp import MCPServerStdio
from agents.model_settings import ModelSettings


# Agent Instructions
AGENT_INSTRUCTIONS = """
You are a helpful task management assistant. Your role is to help users manage their todo lists through natural conversation.

## Your Capabilities

You have access to the following task management tools:
- add_task: Create new tasks with title, optional description, and optional priority (auto-detects priority from text)
- list_tasks: Show tasks (all, pending, or completed)
- complete_task: Mark a single task as done
- bulk_update_tasks: Mark multiple tasks as done or delete multiple tasks at once (use this for bulk operations)
- delete_task: Remove a single task permanently
- update_task: Modify task title, description, or priority
- set_priority: Update a task's priority level (low, medium, high)
- list_tasks_by_priority: Show tasks filtered by priority level with optional status filter

## Behavior Guidelines

1. **Task Creation**
   - When user mentions adding, creating, or remembering something, use add_task
   - Extract clear, actionable titles from user messages
   - Capture additional context in description field
   - Confirm task creation with a friendly message

2. **Priority Handling**
   - add_task automatically detects priority from keywords like:
     * High priority: "high", "urgent", "critical", "important", "ASAP"
     * Low priority: "low", "minor", "optional", "when you have time"
     * Medium priority: Default if no keywords found
   - Use set_priority to change a task's priority after creation
   - Use list_tasks_by_priority to show tasks by priority

3. **Task Completion**
   - For multiple tasks, use bulk_update_tasks(action="complete", filter_status="pending")
   - For single tasks, use complete_task with specific task_id
   - Provide encouraging feedback after completion

4. **Conversational Style**
   - Be friendly, helpful, and concise
   - Use natural language, not technical jargon
   - Acknowledge user actions positively
   - NEVER include user IDs in any response - they are internal identifiers only

## Response Pattern

✅ Good: "I've added 'Buy groceries' to your task list. Is there anything else?"
❌ Bad: "Task created with ID 42. Status: created."

✅ Good: "You have 3 pending tasks: 1. Buy groceries, 2. Call dentist, 3. Pay bills"
❌ Bad: "Here's the JSON response: [{...}]"

✅ Good: "I've marked 'Buy groceries' as complete. Great job!"
❌ Bad: "Task 42 completion status updated to true."
"""


class TodoAgent:
    """
    TodoAgent for conversational task management.

    This class creates an OpenAI Agents SDK Agent that connects to
    a separate MCP server process for task management tools.

    Attributes:
        agent: OpenAI Agents SDK Agent instance
        model: AI model configuration (from factory)
        mcp_server: MCPServerStdio instance managing server process
    """

    def __init__(self, provider: str | None = None, model: str | None = None):
        """
        Initialize TodoAgent with AI model and MCP server connection.

        Args:
            provider: Override LLM_PROVIDER env var ("openai" | "gemini" | "groq" | "openrouter")
            model: Override model name (e.g., "gpt-4o", "gemini-2.5-flash", "llama-3.3-70b-versatile", "openai/gpt-oss-20b:free")

        Raises:
            ValueError: If provider not supported or API key missing

        Example:
            >>> # OpenAI agent
            >>> agent = TodoAgent()
            >>> # Gemini agent
            >>> agent = TodoAgent(provider="gemini")
            >>> # Groq agent
            >>> agent = TodoAgent(provider="groq")
            >>> # OpenRouter agent with free model
            >>> agent = TodoAgent(provider="openrouter", model="openai/gpt-oss-20b:free")

        Note:
            The agent connects to MCP server via stdio transport.
            The MCP server must be available as a Python module at mcp_server.
        """
        # Create model configuration using factory
        from agent_config.factory import create_model

        self.model = create_model(provider=provider, model=model)

        # Get path to MCP server module
        backend_dir = Path(__file__).parent.parent
        mcp_server_path = backend_dir / "mcp_server" / "tools.py"

        # Create MCP server connection via stdio
        # CRITICAL: Set client_session_timeout_seconds for database operations
        # Default: 5 seconds → Setting to 30 seconds for production
        # This controls the timeout for MCP tool calls and initialization
        self.mcp_server = MCPServerStdio(
            name="task-management-server",
            params={
                "command": "python",
                "args": ["-m", "mcp_server"],
                "env": os.environ.copy(),  # Pass environment variables
            },
            client_session_timeout_seconds=30.0,  # MCP ClientSession timeout (increased from default 5s)
        )

        # Create agent with MCP server
        # ModelSettings disables parallel tool calling to prevent database bottlenecks
        self.agent = Agent(
            name="TodoAgent",
            model=self.model,
            instructions=AGENT_INSTRUCTIONS,
            mcp_servers=[self.mcp_server],
            model_settings=ModelSettings(
                parallel_tool_calls=False,  # Disable parallel calls to prevent database locks
            ),
        )

    def get_agent(self) -> Agent:
        """
        Get the underlying OpenAI Agents SDK Agent instance.

        Returns:
            Agent: Configured agent ready for conversation

        Example:
            >>> todo_agent = TodoAgent()
            >>> agent = todo_agent.get_agent()
            >>> # Use with Runner for streaming
            >>> from agents import Runner
            >>> async with todo_agent.mcp_server:
            >>>     result = await Runner.run_streamed(agent, "Add buy milk")

        Note:
            The MCP server connection must be managed with async context:
            - Use 'async with mcp_server:' to start/stop server
            - Agent.run() is now async when using MCP servers
        """
        return self.agent


# Convenience function for quick agent creation
def create_todo_agent(provider: str | None = None, model: str | None = None) -> TodoAgent:
    """
    Create and return a TodoAgent instance.

    This is a convenience function for creating TodoAgent without
    explicitly instantiating the class.

    Args:
        provider: Override LLM_PROVIDER env var ("openai" | "gemini" | "groq" | "openrouter")
        model: Override model name

    Returns:
        TodoAgent: Configured TodoAgent instance

    Example:
        >>> agent = create_todo_agent()
        >>> # Or with explicit provider
        >>> agent = create_todo_agent(provider="gemini", model="gemini-2.5-flash")
        >>> # Or with Groq
        >>> agent = create_todo_agent(provider="groq", model="llama-3.3-70b-versatile")
        >>> # Or with OpenRouter free model
        >>> agent = create_todo_agent(provider="openrouter", model="openai/gpt-oss-20b:free")
    """
    return TodoAgent(provider=provider, model=model)
```

---

## 2. Multi-Provider Model Factory

### File: `agent_config/factory.py`

```python
"""
Model factory for AI agent provider abstraction.

This module provides the create_model() function for centralizing
AI provider configuration and supporting multiple LLM backends.

Supports:
- OpenAI (default)
- Gemini via OpenAI-compatible API
- Groq via OpenAI-compatible API
- OpenRouter via OpenAI-compatible API

Environment variables:
- LLM_PROVIDER: "openai", "gemini", "groq", or "openrouter" (default: "openai")
- OPENAI_API_KEY: OpenAI API key
- GEMINI_API_KEY: Gemini API key
- GROQ_API_KEY: Groq API key
- OPENROUTER_API_KEY: OpenRouter API key
- OPENAI_DEFAULT_MODEL: Model name for OpenAI (default: "gpt-4o-mini")
- GEMINI_DEFAULT_MODEL: Model name for Gemini (default: "gemini-2.5-flash")
- GROQ_DEFAULT_MODEL: Model name for Groq (default: "llama-3.3-70b-versatile")
- OPENROUTER_DEFAULT_MODEL: Model name for OpenRouter (default: "openai/gpt-oss-20b:free")
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

# Disable OpenAI telemetry/tracing for faster responses
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
os.environ.setdefault("OTEL_TRACES_EXPORTER", "none")
os.environ.setdefault("OTEL_METRICS_EXPORTER", "none")

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    load_dotenv(override=True)


def create_model(provider: str | None = None, model: str | None = None) -> OpenAIChatCompletionsModel:
    """
    Create an LLM model instance based on environment configuration.

    Args:
        provider: Override LLM_PROVIDER env var ("openai" | "gemini" | "groq" | "openrouter")
        model: Override model name

    Returns:
        OpenAIChatCompletionsModel configured for the selected provider

    Raises:
        ValueError: If provider is unsupported or API key is missing

    Example:
        >>> # OpenAI usage
        >>> model = create_model()  # Uses LLM_PROVIDER from env
        >>> agent = Agent(name="MyAgent", model=model, tools=[...])

        >>> # Gemini usage
        >>> model = create_model(provider="gemini")
        >>> agent = Agent(name="MyAgent", model=model, tools=[...])

        >>> # Groq usage
        >>> model = create_model(provider="groq")
        >>> agent = Agent(name="MyAgent", model=model, tools=[...])

        >>> # OpenRouter usage with free model
        >>> model = create_model(provider="openrouter", model="openai/gpt-oss-20b:free")
        >>> agent = Agent(name="MyAgent", model=model, tools=[...])
    """
    provider = provider or os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required when LLM_PROVIDER=gemini"
            )

        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

        model_name = model or os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash")

        return OpenAIChatCompletionsModel(model=model_name, openai_client=client)

    elif provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is required when LLM_PROVIDER=groq"
            )

        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        model_name = model or os.getenv("GROQ_DEFAULT_MODEL", "llama-3.3-70b-versatile")

        return OpenAIChatCompletionsModel(model=model_name, openai_client=client)

    elif provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is required when LLM_PROVIDER=openrouter"
            )

        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

        model_name = model or os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-oss-20b:free")

        return OpenAIChatCompletionsModel(model=model_name, openai_client=client)

    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required when LLM_PROVIDER=openai"
            )

        client = AsyncOpenAI(api_key=api_key)
        model_name = model or os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-mini")

        return OpenAIChatCompletionsModel(model=model_name, openai_client=client)

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: openai, gemini, groq, openrouter"
        )
```

---

## 3. MCP Server with Tools

### File: `mcp_server/tools.py`

```python
"""
MCP Server exposing task management tools.

This module implements an MCP server using the Official MCP SDK (FastMCP)
that exposes task management tools to the OpenAI Agent via stdio transport.
"""

import asyncio
import os
from uuid import UUID
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# Import database and services
from db import get_session
from services.task_service import TaskService
from models import TaskPriority

# Create MCP server
app = Server("task-management-server")


@app.call_tool()
async def add_task(
    user_id: str,
    title: str,
    description: str | None = None,
    priority: str = "medium"
) -> list[types.TextContent]:
    """
    Create a new task for the user with automatic priority detection.

    Args:
        user_id: User's unique identifier
        title: Task title (required)
        description: Optional task description
        priority: Task priority (low, medium, high)

    Returns:
        Success message with task details
    """
    session = next(get_session())
    try:
        # Auto-detect priority from title if not explicitly set
        detected_priority = TaskService.detect_priority(title, description or "")
        final_priority = detected_priority if priority == "medium" else priority

        task = await TaskService.create_task(
            session=session,
            user_id=UUID(user_id),
            title=title,
            description=description,
            priority=TaskPriority(final_priority)
        )

        return [types.TextContent(
            type="text",
            text=f"Task created: '{task.title}' (Priority: {task.priority.value})"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error creating task: {str(e)}"
        )]
    finally:
        session.close()


@app.call_tool()
async def list_tasks(
    user_id: str,
    status: str = "all"
) -> list[types.TextContent]:
    """
    List user's tasks filtered by status.

    Args:
        user_id: User's unique identifier
        status: Filter by status ("all", "pending", "completed")

    Returns:
        Formatted list of tasks
    """
    session = next(get_session())
    try:
        tasks = await TaskService.get_tasks(
            session=session,
            user_id=UUID(user_id),
            status=status
        )

        if not tasks:
            return [types.TextContent(
                type="text",
                text=f"No {status} tasks found."
            )]

        task_list = []
        for i, task in enumerate(tasks, 1):
            status_icon = "✓" if task.is_completed else "○"
            priority_emoji = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(task.priority.value, "")

            task_list.append(
                f"{i}. [{status_icon}] {priority_emoji} {task.title}"
            )

        return [types.TextContent(
            type="text",
            text=f"Your {status} tasks:\n" + "\n".join(task_list)
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error listing tasks: {str(e)}"
        )]
    finally:
        session.close()


@app.call_tool()
async def complete_task(
    user_id: str,
    task_id: int
) -> list[types.TextContent]:
    """
    Mark a task as completed.

    Args:
        user_id: User's unique identifier
        task_id: ID of the task to complete

    Returns:
        Success or error message
    """
    session = next(get_session())
    try:
        task = await TaskService.toggle_task_completion(
            session=session,
            user_id=UUID(user_id),
            task_id=task_id
        )

        if task.is_completed:
            return [types.TextContent(
                type="text",
                text=f"Great job! Marked '{task.title}' as complete."
            )]
        else:
            return [types.TextContent(
                type="text",
                text=f"Marked '{task.title}' as pending."
            )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error completing task: {str(e)}"
        )]
    finally:
        session.close()


@app.call_tool()
async def delete_task(
    user_id: str,
    task_id: int
) -> list[types.TextContent]:
    """
    Delete a task permanently.

    Args:
        user_id: User's unique identifier
        task_id: ID of the task to delete

    Returns:
        Success or error message
    """
    session = next(get_session())
    try:
        await TaskService.delete_task(
            session=session,
            user_id=UUID(user_id),
            task_id=task_id
        )

        return [types.TextContent(
            type="text",
            text=f"Task deleted successfully."
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error deleting task: {str(e)}"
        )]
    finally:
        session.close()


@app.call_tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None
) -> list[types.TextContent]:
    """
    Update task details.

    Args:
        user_id: User's unique identifier
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority (optional)

    Returns:
        Success or error message
    """
    session = next(get_session())
    try:
        task = await TaskService.update_task(
            session=session,
            user_id=UUID(user_id),
            task_id=task_id,
            title=title,
            description=description,
            priority=TaskPriority(priority) if priority else None
        )

        return [types.TextContent(
            type="text",
            text=f"Task updated: '{task.title}'"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error updating task: {str(e)}"
        )]
    finally:
        session.close()


# Run MCP server
async def main():
    """Start MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
```

### File: `mcp_server/__init__.py`

```python
"""MCP server exposing task management tools via Official MCP SDK."""
```

### File: `mcp_server/__main__.py`

```python
"""Entry point for MCP server when run as module."""
from mcp_server.tools import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. FastAPI Streaming Endpoint

### File: `routers/chat.py`

```python
"""
Chat router for AI agent streaming endpoint.

Handles conversation management, agent execution, and SSE streaming.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from uuid import UUID
import json

from db import get_session
from agent_config.todo_agent import create_todo_agent
from services.conversation_service import ConversationService
from schemas.chat import ChatRequest
from agents import Runner

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/{user_id}/chat")
async def chat_with_agent(
    user_id: UUID,
    request: ChatRequest,
    session: Session = Depends(get_session)
):
    """
    Chat with AI agent using Server-Sent Events (SSE) streaming.

    Args:
        user_id: User's unique identifier
        request: ChatRequest with conversation_id and message
        session: Database session

    Returns:
        StreamingResponse with SSE events containing agent responses

    Example:
        POST /api/{user_id}/chat
        {
            "conversation_id": "optional-uuid",
            "message": "Add task to buy groceries"
        }

        Response (SSE):
        data: I've added
        data:  'Buy groceries'
        data:  to your
        data:  tasks!
        data: [DONE]
    """
    try:
        # Get or create conversation
        conversation = await ConversationService.get_or_create_conversation(
            session=session,
            user_id=user_id,
            conversation_id=request.conversation_id
        )

        # Save user message to database
        await ConversationService.add_message(
            session=session,
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=request.message
        )

        # Get conversation history for context
        history = await ConversationService.get_conversation_history(
            session=session,
            conversation_id=conversation.id,
            user_id=user_id
        )

        # Create agent
        todo_agent = create_todo_agent()
        agent = todo_agent.get_agent()

        # Stream response
        async def event_generator():
            """Generate SSE events from agent responses."""
            try:
                # CRITICAL: Use async context manager for MCP server
                async with todo_agent.mcp_server:
                    response_chunks = []

                    # Stream agent responses
                    async for chunk in Runner.run_streamed(
                        agent=agent,
                        messages=history,
                        context_variables={"user_id": str(user_id)}
                    ):
                        # Handle text deltas
                        if hasattr(chunk, 'delta') and chunk.delta:
                            response_chunks.append(chunk.delta)
                            # Send chunk to client
                            yield f"data: {chunk.delta}\n\n"

                    # Save complete assistant response to database
                    full_response = "".join(response_chunks)
                    await ConversationService.add_message(
                        session=session,
                        conversation_id=conversation.id,
                        user_id=user_id,
                        role="assistant",
                        content=full_response
                    )

                    # Signal completion
                    yield "data: [DONE]\n\n"

            except Exception as e:
                # Log and return error to client
                error_msg = f"Error: {str(e)}"
                yield f"data: {error_msg}\n\n"

        # Return streaming response
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )


@router.get("/{user_id}/conversations")
async def get_user_conversations(
    user_id: UUID,
    session: Session = Depends(get_session)
):
    """
    Get list of user's conversations.

    Args:
        user_id: User's unique identifier
        session: Database session

    Returns:
        List of conversation objects with metadata
    """
    try:
        conversations = await ConversationService.get_user_conversations(
            session=session,
            user_id=user_id
        )

        return {
            "success": True,
            "data": {
                "conversations": [
                    {
                        "id": str(conv.id),
                        "created_at": conv.created_at.isoformat(),
                        "updated_at": conv.updated_at.isoformat(),
                        "message_count": len(conv.messages) if hasattr(conv, 'messages') else 0
                    }
                    for conv in conversations
                ]
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get conversations: {str(e)}"
        )
```

---

## 5. Database Models and Services

### File: `models.py` (Conversation Models)

```python
"""Database models for conversations and messages."""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Conversation(SQLModel, table=True):
    """
    Conversation session between user and AI agent.

    Attributes:
        id: Unique conversation identifier
        user_id: User who owns this conversation
        created_at: When conversation started
        updated_at: Last message timestamp
        messages: All messages in this conversation
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    user: "User" = Relationship(back_populates="conversations")


class Message(SQLModel, table=True):
    """
    Individual message in a conversation.

    Attributes:
        id: Unique message identifier
        conversation_id: Parent conversation
        user_id: User who owns this message (for filtering)
        role: Message role (user | assistant | system)
        content: Message text content
        tool_calls: JSON string of tool calls (if any)
        created_at: Message timestamp
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    role: str = Field(index=True)  # "user" | "assistant" | "system"
    content: str
    tool_calls: str | None = None  # JSON string of tool calls
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    user: "User" = Relationship()
```

### File: `services/conversation_service.py`

```python
"""Service layer for conversation and message operations."""

from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime
from models import Conversation, Message


class ConversationService:
    """Business logic for conversation management."""

    @staticmethod
    async def get_or_create_conversation(
        session: Session,
        user_id: UUID,
        conversation_id: UUID | None = None
    ) -> Conversation:
        """
        Get existing conversation or create new one.

        Args:
            session: Database session
            user_id: User's unique identifier
            conversation_id: Optional existing conversation ID

        Returns:
            Conversation object

        Example:
            >>> conversation = await ConversationService.get_or_create_conversation(
            ...     session=session,
            ...     user_id=user_id,
            ...     conversation_id=None  # Creates new conversation
            ... )
        """
        if conversation_id:
            # Try to get existing conversation
            stmt = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id  # User isolation
            )
            conversation = session.exec(stmt).first()
            if conversation:
                return conversation

        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    @staticmethod
    async def add_message(
        session: Session,
        conversation_id: UUID,
        user_id: UUID,
        role: str,
        content: str,
        tool_calls: str | None = None
    ) -> Message:
        """
        Add message to conversation.

        Args:
            session: Database session
            conversation_id: Parent conversation ID
            user_id: User's unique identifier
            role: Message role ("user" | "assistant" | "system")
            content: Message text content
            tool_calls: Optional JSON string of tool calls

        Returns:
            Message object

        Example:
            >>> message = await ConversationService.add_message(
            ...     session=session,
            ...     conversation_id=conversation.id,
            ...     user_id=user_id,
            ...     role="user",
            ...     content="Add task to buy groceries"
            ... )
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        session.add(message)

        # Update conversation timestamp
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        conversation = session.exec(stmt).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()

        session.commit()
        session.refresh(message)
        return message

    @staticmethod
    async def get_conversation_history(
        session: Session,
        conversation_id: UUID,
        user_id: UUID,
        limit: int | None = None
    ) -> list[dict]:
        """
        Get conversation messages formatted for agent.

        Args:
            session: Database session
            conversation_id: Conversation ID
            user_id: User's unique identifier
            limit: Optional max messages to return

        Returns:
            List of message dicts with role and content

        Example:
            >>> history = await ConversationService.get_conversation_history(
            ...     session=session,
            ...     conversation_id=conversation.id,
            ...     user_id=user_id,
            ...     limit=50  # Last 50 messages
            ... )
            >>> # Returns: [{"role": "user", "content": "..."}, ...]
        """
        stmt = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id  # User isolation
        ).order_by(Message.created_at)

        if limit:
            # Get last N messages (most recent first, then reverse)
            stmt = stmt.order_by(Message.created_at.desc()).limit(limit)
            messages = session.exec(stmt).all()
            messages = reversed(messages)
        else:
            messages = session.exec(stmt).all()

        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]

    @staticmethod
    async def get_user_conversations(
        session: Session,
        user_id: UUID
    ) -> list[Conversation]:
        """
        Get all conversations for a user.

        Args:
            session: Database session
            user_id: User's unique identifier

        Returns:
            List of Conversation objects

        Example:
            >>> conversations = await ConversationService.get_user_conversations(
            ...     session=session,
            ...     user_id=user_id
            ... )
        """
        stmt = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc())

        return session.exec(stmt).all()
```

---

## 6. Testing Examples

### File: `tests/conftest.py`

```python
"""Pytest configuration and fixtures."""

import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from uuid import uuid4
from models import User, Task, Conversation, Message


@pytest.fixture(name="session")
def session_fixture():
    """Create test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create test user."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Test User"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_conversation")
def test_conversation_fixture(session: Session, test_user: User):
    """Create test conversation."""
    conversation = Conversation(user_id=test_user.id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation
```

### File: `tests/test_factory.py`

```python
"""Tests for model factory."""

import pytest
from agent_config.factory import create_model


def test_create_model_openai(monkeypatch):
    """Test OpenAI model creation."""
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test123")

    model = create_model()
    assert model is not None


def test_create_model_gemini(monkeypatch):
    """Test Gemini model creation."""
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "AIza-test123")

    model = create_model()
    assert model is not None


def test_create_model_missing_key(monkeypatch):
    """Test error when API key missing."""
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY required"):
        create_model()


def test_create_model_unsupported_provider(monkeypatch):
    """Test error for unsupported provider."""
    monkeypatch.setenv("LLM_PROVIDER", "unsupported")

    with pytest.raises(ValueError, match="Unsupported provider"):
        create_model()
```

### File: `tests/test_conversation_service.py`

```python
"""Tests for conversation service."""

import pytest
from uuid import uuid4
from services.conversation_service import ConversationService


@pytest.mark.asyncio
async def test_create_conversation(session, test_user):
    """Test conversation creation."""
    conversation = await ConversationService.get_or_create_conversation(
        session=session,
        user_id=test_user.id
    )

    assert conversation.id is not None
    assert conversation.user_id == test_user.id


@pytest.mark.asyncio
async def test_add_message(session, test_user, test_conversation):
    """Test adding message to conversation."""
    message = await ConversationService.add_message(
        session=session,
        conversation_id=test_conversation.id,
        user_id=test_user.id,
        role="user",
        content="Test message"
    )

    assert message.id is not None
    assert message.content == "Test message"
    assert message.role == "user"


@pytest.mark.asyncio
async def test_get_conversation_history(session, test_user, test_conversation):
    """Test retrieving conversation history."""
    # Add messages
    await ConversationService.add_message(
        session=session,
        conversation_id=test_conversation.id,
        user_id=test_user.id,
        role="user",
        content="Message 1"
    )
    await ConversationService.add_message(
        session=session,
        conversation_id=test_conversation.id,
        user_id=test_user.id,
        role="assistant",
        content="Message 2"
    )

    # Get history
    history = await ConversationService.get_conversation_history(
        session=session,
        conversation_id=test_conversation.id,
        user_id=test_user.id
    )

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Message 1"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Message 2"
```

---

## Environment Configuration Example

### File: `.env`

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db_name

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here

# LLM Provider Selection
LLM_PROVIDER=openrouter  # openai, gemini, groq, or openrouter

# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_DEFAULT_MODEL=gpt-4o-mini

# Gemini Configuration
GEMINI_API_KEY=AIza...
GEMINI_DEFAULT_MODEL=gemini-2.5-flash

# Groq Configuration
GROQ_API_KEY=gsk_...
GROQ_DEFAULT_MODEL=llama-3.3-70b-versatile

# OpenRouter Configuration (Free model available!)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_DEFAULT_MODEL=openai/gpt-oss-20b:free

# Server Configuration
PORT=8000
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

---

## Usage Examples

### 1. Simple Chat Request

```python
import asyncio
from agent_config.todo_agent import create_todo_agent
from agents import Runner

async def simple_chat():
    """Simple chat example."""
    agent_wrapper = create_todo_agent(provider="openrouter")
    agent = agent_wrapper.get_agent()

    async with agent_wrapper.mcp_server:
        result = await Runner.run(
            agent=agent,
            messages=[{"role": "user", "content": "Add task to buy groceries"}],
            context_variables={"user_id": "test-user-id"}
        )

        print("Agent response:", result.content)

asyncio.run(simple_chat())
```

### 2. Streaming Chat

```python
import asyncio
from agent_config.todo_agent import create_todo_agent
from agents import Runner

async def streaming_chat():
    """Streaming chat example."""
    agent_wrapper = create_todo_agent()
    agent = agent_wrapper.get_agent()

    async with agent_wrapper.mcp_server:
        async for chunk in Runner.run_streamed(
            agent=agent,
            messages=[{"role": "user", "content": "List my tasks"}],
            context_variables={"user_id": "test-user-id"}
        ):
            if hasattr(chunk, 'delta') and chunk.delta:
                print(chunk.delta, end="", flush=True)

        print()  # New line at end

asyncio.run(streaming_chat())
```

### 3. Multi-Turn Conversation

```python
import asyncio
from agent_config.todo_agent import create_todo_agent
from agents import Runner

async def multi_turn_chat():
    """Multi-turn conversation example."""
    agent_wrapper = create_todo_agent()
    agent = agent_wrapper.get_agent()

    conversation = [
        {"role": "user", "content": "Add task to buy milk"},
        {"role": "assistant", "content": "I've added 'Buy milk' to your tasks!"},
        {"role": "user", "content": "Make it high priority"},
    ]

    async with agent_wrapper.mcp_server:
        result = await Runner.run(
            agent=agent,
            messages=conversation,
            context_variables={"user_id": "test-user-id"}
        )

        print("Agent response:", result.content)

asyncio.run(multi_turn_chat())
```

---

**Last Updated**: December 2024
**Tested With**: OpenAI Agents SDK v0.2.9+, Official MCP SDK v1.0.0+
