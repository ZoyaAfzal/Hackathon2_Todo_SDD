"""Integration tests for cross-user data isolation in chat."""

import uuid
from unittest.mock import AsyncMock, patch


class TestChatIsolation:
    """Test that users cannot access each other's conversations."""

    def test_user_cannot_access_other_users_conversation(
        self, client, session, test_user, another_user,
        auth_headers, another_user_headers,
    ):
        """User B cannot access User A's conversation."""
        # User A creates a conversation
        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=("Hello A!", []),
        ):
            r = client.post(
                f"/api/{test_user.id}/chat",
                json={"message": "Hello from user A"},
                headers=auth_headers,
            )
        conv_id = r.json()["conversation_id"]

        # User B tries to get User A's conversation messages
        response = client.get(
            f"/api/{another_user.id}/conversations/{conv_id}/messages",
            headers=another_user_headers,
        )
        assert response.status_code == 404

    def test_user_cannot_resume_other_users_conversation(
        self, client, session, test_user, another_user,
        auth_headers, another_user_headers,
    ):
        """User B cannot resume User A's conversation."""
        # User A creates a conversation
        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=("Hello!", []),
        ):
            r = client.post(
                f"/api/{test_user.id}/chat",
                json={"message": "Hello"},
                headers=auth_headers,
            )
        conv_id = r.json()["conversation_id"]

        # User B tries to resume it
        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=("ok", []),
        ):
            response = client.post(
                f"/api/{another_user.id}/chat",
                json={
                    "message": "Hijack attempt",
                    "conversation_id": conv_id,
                },
                headers=another_user_headers,
            )
        assert response.status_code == 404
