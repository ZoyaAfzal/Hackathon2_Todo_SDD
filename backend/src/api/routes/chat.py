"""Chat routes for AI-powered todo management.

Provides endpoints for:
- POST /api/{user_id}/chat - Send a chat message
- GET /api/{user_id}/conversations - List conversations
- GET /api/{user_id}/conversations/{conversation_id}/messages - Get messages
"""

import logging
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from src.api.deps.auth import CurrentUser
from src.api.deps.database import get_session
from src.api.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationSummary,
    MessageList,
    MessageOut,
    ToolCallInfo,
)
from src.services.chat_service import ChatService, get_chat_service
from src.services.conversation_service import (
    ConversationService,
    get_conversation_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


def _validate_user_ownership(
    path_user_id: uuid.UUID,
    current_user: CurrentUser,
) -> None:
    """Verify the path user_id matches the authenticated user."""
    if path_user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user ID mismatch",
        )


@router.post(
    "/api/{user_id}/chat",
    response_model=ChatResponse,
    responses={
        200: {"description": "Chat response"},
        400: {"description": "Invalid request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - user ID mismatch"},
        404: {"description": "Conversation not found"},
        503: {"description": "AI service unavailable"},
    },
)
async def send_chat_message(
    user_id: uuid.UUID,
    request: ChatRequest,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> ChatResponse:
    """Send a chat message to the AI todo assistant.

    Creates a new conversation if conversation_id is not provided.
    Loads conversation history and routes through the AI agent
    with MCP tools for task management.
    """
    _validate_user_ownership(user_id, current_user)

    chat_service = get_chat_service(session)

    try:
        response = await chat_service.process_message(
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id,
        )
        return response

    except ValueError as e:
        if str(e) == "conversation_not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except RuntimeError as e:
        logger.error("AI service error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable. Please try again.",
        )

    except Exception as e:
        logger.error("Unexpected chat error: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An unexpected error occurred. Please try again.",
        )


@router.post(
    "/api/{user_id}/chat/stream",
    responses={
        200: {
            "description": "SSE stream of chat response",
            "content": {"text/event-stream": {}},
        },
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - user ID mismatch"},
        404: {"description": "Conversation not found"},
    },
)
async def send_chat_message_stream(
    user_id: uuid.UUID,
    request: ChatRequest,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> StreamingResponse:
    """Send a chat message with streaming SSE response.

    Returns a Server-Sent Events stream with ChatKit-compatible events:
    - thread.created: Initial thread/conversation creation
    - thread.item.created: New message item started
    - thread.item.delta: Text chunk (streamed incrementally)
    - thread.item.done: Message complete with full content
    - done: Stream finished
    - error: Error occurred
    """
    _validate_user_ownership(user_id, current_user)

    chat_service = get_chat_service(session)

    async def generate_events():
        """Generator for SSE events."""
        try:
            async for event in chat_service.process_message_stream(
                user_id=user_id,
                message=request.message,
                conversation_id=request.conversation_id,
            ):
                yield event
        except Exception as e:
            logger.error("Stream error: %s", e, exc_info=True)
            import json
            yield f"event: error\ndata: {json.dumps({'message': 'Stream error'})}\n\n"
            yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/api/{user_id}/conversations",
    response_model=list[ConversationSummary],
    responses={
        200: {"description": "List of conversations"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)
async def list_conversations(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> list[ConversationSummary]:
    """List all conversations for the authenticated user."""
    _validate_user_ownership(user_id, current_user)

    service = get_conversation_service(session)
    conversations = service.list_conversations(user_id)

    return [
        ConversationSummary(
            id=c.id,
            title=c.title,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in conversations
    ]


@router.get(
    "/api/{user_id}/conversations/{conversation_id}/messages",
    response_model=MessageList,
    responses={
        200: {"description": "List of messages"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Conversation not found"},
    },
)
async def get_conversation_messages(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    limit: int = Query(default=50, ge=1, le=100),
    before_sequence: Optional[int] = Query(default=None),
) -> MessageList:
    """Get messages for a conversation."""
    _validate_user_ownership(user_id, current_user)

    conv_service = get_conversation_service(session)

    # Verify conversation ownership
    conversation = conv_service.get_conversation(conversation_id, user_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = conv_service.get_recent_messages(
        conversation_id,
        limit=limit + 1,
        before_sequence=before_sequence,
    )

    has_more = len(messages) > limit
    messages = messages[:limit]

    return MessageList(
        messages=[
            MessageOut(
                id=m.id,
                role=m.role,
                content=m.content,
                tool_calls=(
                    [ToolCallInfo(**tc) for tc in m.tool_calls]
                    if m.tool_calls
                    else None
                ),
                sequence_number=m.sequence_number,
                created_at=m.created_at.isoformat(),
            )
            for m in messages
        ],
        has_more=has_more,
    )
