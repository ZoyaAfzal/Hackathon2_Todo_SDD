"""
FastAPI Chat Router Template - SSE Streaming Endpoint

Copy this template to create a streaming chat endpoint for your AI agent.

Usage:
    1. Copy to your project's routers directory
    2. Update imports for your agent and services
    3. Customize endpoint paths and logic
    4. Register router in main.py: app.include_router(router)
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from uuid import UUID
from pydantic import BaseModel

# TODO: Update these imports for your project
from db import get_session
# from agent_config.my_agent import create_my_agent
# from services.conversation_service import ConversationService

from agents import Runner


# Request/Response Schemas
class ChatRequest(BaseModel):
    """
    Chat request payload.

    Attributes:
        conversation_id: Optional existing conversation ID
        message: User's message text
    """
    conversation_id: UUID | None = None
    message: str


class ConversationResponse(BaseModel):
    """
    Conversation metadata response.

    Attributes:
        id: Conversation unique ID
        created_at: ISO timestamp when created
        updated_at: ISO timestamp when last updated
        message_count: Number of messages in conversation
    """
    id: str
    created_at: str
    updated_at: str
    message_count: int


# Create router
# UPDATE: Prefix and tags
router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/{user_id}/chat")
async def chat_with_agent(
    user_id: UUID,
    request: ChatRequest,
    session: Session = Depends(get_session)
):
    """
    Chat with AI agent using Server-Sent Events (SSE) streaming.

    This endpoint:
    1. Gets or creates a conversation
    2. Saves user message to database
    3. Retrieves conversation history
    4. Streams agent response via SSE
    5. Saves agent response to database

    Args:
        user_id: User's unique identifier (from JWT/auth)
        request: ChatRequest with optional conversation_id and message
        session: Database session (injected)

    Returns:
        StreamingResponse with SSE events

    Example:
        POST /api/{user_id}/chat
        {
            "conversation_id": null,
            "message": "Hello, how can you help me?"
        }

        Response (SSE):
        data: Hello!
        data:  I can help you with...
        data: [DONE]
    """
    try:
        # STEP 1: Get or create conversation
        # TODO: Replace with your ConversationService
        # conversation = await ConversationService.get_or_create_conversation(
        #     session=session,
        #     user_id=user_id,
        #     conversation_id=request.conversation_id
        # )
        conversation = None  # Placeholder

        # STEP 2: Save user message to database
        # TODO: Replace with your ConversationService
        # await ConversationService.add_message(
        #     session=session,
        #     conversation_id=conversation.id,
        #     user_id=user_id,
        #     role="user",
        #     content=request.message
        # )

        # STEP 3: Get conversation history
        # TODO: Replace with your ConversationService
        # history = await ConversationService.get_conversation_history(
        #     session=session,
        #     conversation_id=conversation.id,
        #     user_id=user_id
        # )
        history = [{"role": "user", "content": request.message}]  # Placeholder

        # STEP 4: Create agent
        # TODO: Replace with your agent
        # my_agent = create_my_agent()
        # agent = my_agent.get_agent()

        # STEP 5: Stream response
        async def event_generator():
            """Generate SSE events from agent responses."""
            try:
                # CRITICAL: Use async context manager for MCP server
                # TODO: Replace with your agent
                # async with my_agent.mcp_server:
                response_chunks = []

                # TODO: Replace with your agent
                # Stream agent responses
                # async for chunk in Runner.run_streamed(
                #     agent=agent,
                #     messages=history,
                #     context_variables={"user_id": str(user_id)}
                # ):
                #     # Handle text deltas
                #     if hasattr(chunk, 'delta') and chunk.delta:
                #         response_chunks.append(chunk.delta)
                #         # Send chunk to client
                #         yield f"data: {chunk.delta}\n\n"

                # Placeholder response
                yield "data: Hello! This is a placeholder response.\n\n"
                response_chunks.append("Hello! This is a placeholder response.")

                # STEP 6: Save assistant response to database
                # TODO: Replace with your ConversationService
                # full_response = "".join(response_chunks)
                # await ConversationService.add_message(
                #     session=session,
                #     conversation_id=conversation.id,
                #     user_id=user_id,
                #     role="assistant",
                #     content=full_response
                # )

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
        JSON response with conversation list

    Example:
        GET /api/{user_id}/conversations

        Response:
        {
            "success": true,
            "data": {
                "conversations": [
                    {
                        "id": "uuid-string",
                        "created_at": "2024-12-18T10:30:00Z",
                        "updated_at": "2024-12-18T10:35:00Z",
                        "message_count": 5
                    }
                ]
            }
        }
    """
    try:
        # TODO: Replace with your ConversationService
        # conversations = await ConversationService.get_user_conversations(
        #     session=session,
        #     user_id=user_id
        # )

        # Placeholder response
        conversations = []

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
