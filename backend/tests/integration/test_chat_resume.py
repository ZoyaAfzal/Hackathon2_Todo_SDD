"""Integration tests for US6: Resume conversation after restart."""

import uuid
from unittest.mock import AsyncMock, patch

from src.models.conversation import Conversation
from src.models.message import Message


class TestChatResume:
    """Test conversation resumption via conversation_id."""

    def test_new_conversation_created_without_id(
        self, client, session, test_user, auth_headers
    ):
        """POST without conversation_id creates a new conversation."""
        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=("Hello! How can I help?", []),
        ):
            response = client.post(
                f"/api/{test_user.id}/chat",
                json={"message": "Hello"},
                headers=auth_headers,
            )

        assert response.status_code == 200
        conv_id = response.json()["conversation_id"]
        assert conv_id is not None

        # Verify conversation exists in DB
        conv = session.get(Conversation, uuid.UUID(conv_id))
        assert conv is not None
        assert conv.user_id == test_user.id

    def test_resume_conversation_with_id(
        self, client, session, test_user, auth_headers
    ):
        """POST with existing conversation_id resumes the conversation."""
        # First message - creates conversation
        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=("Hello!", []),
        ):
            r1 = client.post(
                f"/api/{test_user.id}/chat",
                json={"message": "Hi there"},
                headers=auth_headers,
            )
        conv_id = r1.json()["conversation_id"]

        # Second message - resumes conversation
        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=("I remember our conversation!", []),
        ):
            r2 = client.post(
                f"/api/{test_user.id}/chat",
                json={
                    "message": "What did I say before?",
                    "conversation_id": conv_id,
                },
                headers=auth_headers,
            )

        assert r2.status_code == 200
        assert r2.json()["conversation_id"] == conv_id

        # Verify messages persisted
        from sqlmodel import select, col
        stmt = (
            select(Message)
            .where(Message.conversation_id == uuid.UUID(conv_id))
            .order_by(col(Message.sequence_number))
        )
        messages = list(session.exec(stmt).all())
        assert len(messages) == 4  # 2 user + 2 assistant

    def test_nonexistent_conversation_id_returns_404(
        self, client, session, test_user, auth_headers
    ):
        """POST with nonexistent conversation_id returns 404."""
        fake_id = str(uuid.uuid4())

        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=("ok", []),
        ):
            response = client.post(
                f"/api/{test_user.id}/chat",
                json={
                    "message": "Hello",
                    "conversation_id": fake_id,
                },
                headers=auth_headers,
            )

        assert response.status_code == 404
