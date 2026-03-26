"""Contract tests for chat API endpoints."""

import uuid
from unittest.mock import AsyncMock, patch

from src.models.conversation import Conversation
from src.models.message import Message


class TestChatEndpointContract:
    """Validate chat API request/response schemas match contracts."""

    def test_chat_response_schema(
        self, client, session, test_user, auth_headers
    ):
        """POST /api/{user_id}/chat returns conversation_id and reply."""
        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=("Hello!", []),
        ):
            response = client.post(
                f"/api/{test_user.id}/chat",
                json={"message": "Hello"},
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "reply" in data
        assert "tool_calls" in data
        assert isinstance(data["tool_calls"], list)
        # conversation_id must be valid UUID
        uuid.UUID(data["conversation_id"])

    def test_conversations_list_schema(
        self, client, session, test_user, auth_headers
    ):
        """GET /api/{user_id}/conversations returns list."""
        # Create a conversation first
        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=("Hi!", []),
        ):
            client.post(
                f"/api/{test_user.id}/chat",
                json={"message": "Hello"},
                headers=auth_headers,
            )

        response = client.get(
            f"/api/{test_user.id}/conversations",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        conv = data[0]
        assert "id" in conv
        assert "title" in conv
        assert "created_at" in conv
        assert "updated_at" in conv

    def test_messages_list_schema(
        self, client, session, test_user, auth_headers
    ):
        """GET messages endpoint returns ordered messages."""
        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=("Reply!", []),
        ):
            r = client.post(
                f"/api/{test_user.id}/chat",
                json={"message": "Test message"},
                headers=auth_headers,
            )
        conv_id = r.json()["conversation_id"]

        response = client.get(
            f"/api/{test_user.id}/conversations/{conv_id}/messages",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "has_more" in data
        assert len(data["messages"]) == 2  # user + assistant
        msg = data["messages"][0]
        assert "id" in msg
        assert "role" in msg
        assert "content" in msg
        assert "sequence_number" in msg
        assert "created_at" in msg

    def test_chat_stream_returns_sse(
        self, client, session, test_user, auth_headers
    ):
        """POST /api/{user_id}/chat/stream returns SSE response."""

        async def mock_stream(*args, **kwargs):
            yield 'event: thread.created\ndata: {"thread_id": "test-123"}\n\n'
            yield 'event: thread.item.created\ndata: {"item_id": "i1", "type": "message", "role": "assistant"}\n\n'
            yield 'event: thread.item.delta\ndata: {"item_id": "i1", "delta": "Hello"}\n\n'
            yield 'event: thread.item.done\ndata: {"item_id": "i1", "content": "Hello"}\n\n'
            yield 'event: done\ndata: {}\n\n'

        with patch(
            "src.services.chat_service.ChatService.process_message_stream",
            return_value=mock_stream(),
        ):
            response = client.post(
                f"/api/{test_user.id}/chat/stream",
                json={"message": "Hello"},
                headers=auth_headers,
            )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
        assert response.headers.get("cache-control") == "no-cache"

        # Verify SSE format
        content = response.text
        assert "event: thread.created" in content
        assert "event: thread.item.delta" in content
        assert "event: done" in content
