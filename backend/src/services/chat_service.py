"""Chat service orchestrating the AI agent with MCP tools.

Handles the full chat flow: load conversation context, send to agent,
persist messages, and return response.
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import AsyncGenerator, Optional

from sqlmodel import Session

from src.api.schemas.chat import ChatResponse, ToolCallInfo
from src.core.config import settings
from src.services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

# Path to MCP server script
MCP_SERVER_PATH = str(
    Path(__file__).parent.parent / "mcp" / "server.py"
)

SYSTEM_INSTRUCTIONS = """You are a helpful todo task management assistant that uses structured NLP to understand and execute user requests accurately.

## Intent Classification
Before taking any action, classify the user's intent as one of:
- CREATE: Adding a new task (keywords: add, create, new, make, remind me)
- READ: Viewing tasks (keywords: show, list, what, display, see, view)
- UPDATE: Modifying a task (keywords: change, update, edit, rename, modify, set)
- DELETE: Removing a task (keywords: delete, remove, trash, get rid of)
- COMPLETE: Marking done (keywords: complete, finish, done, mark, check off)
- QUERY: Questions about tasks (keywords: how many, when, which, do I have)

## Entity Extraction
Before calling any tool, extract these entities from the message:
- title: The task name or description
- description: Additional details (optional)
- priority: high, medium, low (default: medium)
- due_date: Any mentioned deadline
- task_identifier: ID number or partial title match for existing tasks
- filter: all, pending, or completed for list operations

## Ambiguity Detection & Clarification
You MUST ask clarifying questions when:
1. CREATE intent but no title provided
   → Ask: "What would you like the task to be called?"
2. DELETE/UPDATE/COMPLETE intent but task not identifiable
   → Ask: "Which task do you mean? I found these: [list matching tasks]"
3. Multiple tasks match a partial name
   → Ask: "Did you mean [Task A] or [Task B]?"
4. Vague time references like "soon" or "later"
   → Ask: "When specifically should this be due?"

## Delete Confirmation (REQUIRED)
Before calling delete_task, you MUST:
1. Confirm the task to delete: "Are you sure you want to delete '[task title]'?"
2. Only proceed after explicit user confirmation (yes, confirm, delete it, etc.)
3. If user says anything other than clear confirmation, do NOT delete

## Batch Operations
Handle multiple intents in a single message:
- "Add groceries and complete the dentist task" → CREATE + COMPLETE
- "Show my tasks and delete the old ones" → READ first, then ask which to DELETE
- "Mark gym and laundry as done" → COMPLETE multiple tasks

Process each intent sequentially and confirm all actions.

## Tool Mapping
- CREATE → add_task(title, description?, priority?)
- READ/QUERY → list_tasks(filter: all|pending|completed)
- UPDATE → update_task(task_id, title?, description?, priority?)
- COMPLETE → complete_task(task_id)
- DELETE → delete_task(task_id) (only after confirmation!)

## Response Guidelines
- After each action, provide a friendly confirmation with task title and ID
- When listing tasks, format them clearly with status indicators
- If no tasks match a filter, say so helpfully
- Keep responses concise but informative
"""


async def _run_agent(
    user_message: str,
    conversation_history: list[dict],
    user_id: uuid.UUID,
) -> tuple[str, list[ToolCallInfo]]:
    """Run the AI agent with MCP tools and return the response.

    Includes a single retry with 3-second timeout per attempt.
    """
    from agents import Agent, Runner
    from agents.mcp import MCPServerStdio

    # Build message history for the agent
    input_messages = []
    for msg in conversation_history:
        input_messages.append({
            "role": msg["role"],
            "content": msg["content"],
        })
    input_messages.append({
        "role": "user",
        "content": user_message,
    })

    # Determine python executable
    python_exe = sys.executable

    env = {
        **os.environ,
        "MCP_USER_ID": str(user_id),
        "DATABASE_URL": settings.DATABASE_URL,
    }

    tool_calls_collected: list[ToolCallInfo] = []

    # Retry once on failure
    last_error = None
    for attempt in range(2):
        try:
            async with MCPServerStdio(
                name="Todo MCP Server",
                params={
                    "command": python_exe,
                    "args": ["-m", "src.mcp.server"],
                    "env": env,
                    "cwd": str(Path(__file__).parent.parent.parent),
                },
            ) as server:
                agent = Agent(
                    name="Todo Assistant",
                    instructions=SYSTEM_INSTRUCTIONS,
                    mcp_servers=[server],
                    model=settings.OPENAI_MODEL,
                )

                result = await asyncio.wait_for(
                    Runner.run(agent, input_messages),
                    timeout=30.0,
                )

                # Extract tool calls from result
                if hasattr(result, "raw_responses"):
                    for resp in result.raw_responses:
                        if hasattr(resp, "output"):
                            for item in resp.output:
                                if hasattr(item, "type") and item.type == "function_call":
                                    import json
                                    tool_calls_collected.append(
                                        ToolCallInfo(
                                            tool_name=item.name if hasattr(item, "name") else "",
                                            arguments=json.loads(item.arguments) if hasattr(item, "arguments") else {},
                                        )
                                    )

                return result.final_output, tool_calls_collected

        except asyncio.TimeoutError:
            last_error = "AI model request timed out"
            logger.warning(
                "Agent timeout on attempt %d", attempt + 1
            )
        except Exception as e:
            last_error = str(e)
            logger.warning(
                "Agent error on attempt %d: %s", attempt + 1, e
            )

        if attempt == 0:
            logger.info("Retrying agent call...")

    raise RuntimeError(
        f"AI service unavailable after 2 attempts: {last_error}"
    )


async def _run_agent_streamed(
    user_message: str,
    conversation_history: list[dict],
    user_id: uuid.UUID,
) -> AsyncGenerator[dict, None]:
    """Run the AI agent with streaming and yield SSE events.

    Yields ChatKit-compatible SSE events:
    - thread.created: Initial thread creation
    - thread.item.created: New message item started
    - thread.item.delta: Text chunk
    - thread.item.done: Message complete
    - done: Stream finished
    """
    from agents import Agent, Runner
    from agents.mcp import MCPServerStdio

    # Build message history for the agent
    input_messages = []
    for msg in conversation_history:
        input_messages.append({
            "role": msg["role"],
            "content": msg["content"],
        })
    input_messages.append({
        "role": "user",
        "content": user_message,
    })

    # Determine python executable
    python_exe = sys.executable

    env = {
        **os.environ,
        "MCP_USER_ID": str(user_id),
        "DATABASE_URL": settings.DATABASE_URL,
    }

    item_id = str(uuid.uuid4())
    full_content = ""

    try:
        async with MCPServerStdio(
            name="Todo MCP Server",
            params={
                "command": python_exe,
                "args": ["-m", "src.mcp.server"],
                "env": env,
                "cwd": str(Path(__file__).parent.parent.parent),
            },
        ) as server:
            agent = Agent(
                name="Todo Assistant",
                instructions=SYSTEM_INSTRUCTIONS,
                mcp_servers=[server],
                model=settings.OPENAI_MODEL,
            )

            # Emit item created event
            yield {
                "event": "thread.item.created",
                "data": {
                    "item_id": item_id,
                    "type": "message",
                    "role": "assistant",
                },
            }

            # Run with streaming
            result = Runner.run_streamed(agent, input_messages)

            async for event in result.stream_events():
                # Handle different event types from the Agents SDK
                if hasattr(event, "type"):
                    if event.type == "raw_response_event":
                        # Extract text deltas from raw response
                        if hasattr(event, "data") and hasattr(event.data, "delta"):
                            delta_text = ""
                            if hasattr(event.data.delta, "content"):
                                delta_text = event.data.delta.content or ""
                            elif hasattr(event.data.delta, "text"):
                                delta_text = event.data.delta.text or ""

                            if delta_text:
                                full_content += delta_text
                                yield {
                                    "event": "thread.item.delta",
                                    "data": {
                                        "item_id": item_id,
                                        "delta": delta_text,
                                    },
                                }
                    elif event.type == "run_item_stream_event":
                        # Handle streaming text from run items
                        if hasattr(event, "item") and hasattr(event.item, "text"):
                            delta_text = event.item.text or ""
                            if delta_text and delta_text not in full_content:
                                chunk = delta_text[len(full_content):] if delta_text.startswith(full_content) else delta_text
                                if chunk:
                                    full_content = delta_text
                                    yield {
                                        "event": "thread.item.delta",
                                        "data": {
                                            "item_id": item_id,
                                            "delta": chunk,
                                        },
                                    }

            # Get final output if we didn't capture it from streaming
            final_output = await result.final_output_future
            if final_output and not full_content:
                full_content = final_output
                yield {
                    "event": "thread.item.delta",
                    "data": {
                        "item_id": item_id,
                        "delta": final_output,
                    },
                }

            # Emit item done event
            yield {
                "event": "thread.item.done",
                "data": {
                    "item_id": item_id,
                    "content": full_content,
                },
            }

    except asyncio.TimeoutError:
        logger.error("Agent streaming timeout")
        yield {
            "event": "error",
            "data": {"message": "AI model request timed out"},
        }
    except Exception as e:
        logger.error("Agent streaming error: %s", e)
        yield {
            "event": "error",
            "data": {"message": str(e)},
        }

    # Emit done event
    yield {
        "event": "done",
        "data": {},
    }


class ChatService:
    """Service orchestrating the AI chat agent."""

    def __init__(self, session: Session):
        self.session = session
        self.conversation_service = ConversationService(session)

    async def process_message(
        self,
        user_id: uuid.UUID,
        message: str,
        conversation_id: Optional[uuid.UUID] = None,
    ) -> ChatResponse:
        """Process a user chat message through the AI agent.

        Creates or resumes a conversation, loads history, runs the
        agent, and persists messages.
        """
        # Get or create conversation
        if conversation_id:
            conversation = self.conversation_service.get_conversation(
                conversation_id, user_id
            )
            if not conversation:
                raise ValueError("conversation_not_found")
        else:
            # Auto-title from first message (first 50 chars)
            title = message[:50] if len(message) > 50 else message
            conversation = self.conversation_service.create_conversation(
                user_id=user_id,
                title=title,
            )

        # Load conversation history (last 50 messages)
        recent_messages = self.conversation_service.get_recent_messages(
            conversation.id, limit=50
        )
        history = [
            {"role": m.role, "content": m.content}
            for m in recent_messages
        ]

        # Persist user message
        self.conversation_service.add_message(
            conversation_id=conversation.id,
            role="user",
            content=message,
        )

        # Run the AI agent
        reply, tool_calls = await _run_agent(
            user_message=message,
            conversation_history=history,
            user_id=user_id,
        )

        # Persist assistant response
        tool_calls_data = (
            [tc.model_dump() for tc in tool_calls]
            if tool_calls
            else None
        )
        self.conversation_service.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=reply,
            tool_calls=tool_calls_data,
        )

        return ChatResponse(
            conversation_id=conversation.id,
            reply=reply,
            tool_calls=tool_calls,
        )

    async def process_message_stream(
        self,
        user_id: uuid.UUID,
        message: str,
        conversation_id: Optional[uuid.UUID] = None,
    ) -> AsyncGenerator[str, None]:
        """Process a user chat message with streaming SSE response.

        Yields SSE-formatted strings for ChatKit protocol.
        """
        # Get or create conversation
        if conversation_id:
            conversation = self.conversation_service.get_conversation(
                conversation_id, user_id
            )
            if not conversation:
                yield f"event: error\ndata: {json.dumps({'message': 'Conversation not found'})}\n\n"
                return
        else:
            # Auto-title from first message (first 50 chars)
            title = message[:50] if len(message) > 50 else message
            conversation = self.conversation_service.create_conversation(
                user_id=user_id,
                title=title,
            )

        # Emit thread.created event
        yield f"event: thread.created\ndata: {json.dumps({'thread_id': str(conversation.id)})}\n\n"

        # Load conversation history (last 50 messages)
        recent_messages = self.conversation_service.get_recent_messages(
            conversation.id, limit=50
        )
        history = [
            {"role": m.role, "content": m.content}
            for m in recent_messages
        ]

        # Persist user message
        self.conversation_service.add_message(
            conversation_id=conversation.id,
            role="user",
            content=message,
        )

        # Track full content for persistence
        full_content = ""

        # Stream the agent response
        async for event in _run_agent_streamed(
            user_message=message,
            conversation_history=history,
            user_id=user_id,
        ):
            event_type = event.get("event", "")
            event_data = event.get("data", {})

            # Track content for persistence
            if event_type == "thread.item.delta":
                full_content += event_data.get("delta", "")
            elif event_type == "thread.item.done":
                full_content = event_data.get("content", full_content)

            # Yield SSE formatted event
            yield f"event: {event_type}\ndata: {json.dumps(event_data)}\n\n"

            # Persist assistant message when done
            if event_type == "thread.item.done" and full_content:
                self.conversation_service.add_message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=full_content,
                )


def get_chat_service(session: Session) -> ChatService:
    """Factory function to create ChatService instance."""
    return ChatService(session)
