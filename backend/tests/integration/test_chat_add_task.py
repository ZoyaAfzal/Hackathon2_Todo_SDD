"""Integration tests for US1: Add task via chat."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from src.api.schemas.chat import ToolCallInfo
from src.models.task import Task
from src.models.user import User


class TestChatAddTask:
    """Test adding tasks through the chat endpoint."""

    def test_add_task_via_chat_creates_task(
        self, client, session, test_user, auth_headers
    ):
        """POST /api/{user_id}/chat with add task message creates task in DB."""
        mock_reply = "I've created a task 'Buy groceries' for you!"
        mock_tool_calls = [
            ToolCallInfo(
                tool_name="add_task",
                arguments={"title": "Buy groceries"},
                result={"status": "success"},
            )
        ]

        # Create the task in DB as the mock agent would
        task = Task(
            id=uuid.uuid4(),
            title="Buy groceries",
            completed=False,
            user_id=test_user.id,
        )
        session.add(task)
        session.commit()

        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=(mock_reply, mock_tool_calls),
        ):
            response = client.post(
                f"/api/{test_user.id}/chat",
                json={"message": "Add a task to buy groceries"},
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "reply" in data
        assert "Buy groceries" in data["reply"]

        # Verify task exists in DB
        from sqlmodel import select
        stmt = select(Task).where(
            Task.user_id == test_user.id,
            Task.title == "Buy groceries",
        )
        db_task = session.exec(stmt).first()
        assert db_task is not None
        assert db_task.completed is False

    def test_add_task_returns_conversation_id(
        self, client, session, test_user, auth_headers
    ):
        """New chat message creates a conversation and returns its ID."""
        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=("Task created!", []),
        ):
            response = client.post(
                f"/api/{test_user.id}/chat",
                json={"message": "Add a task to read a book"},
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] is not None
        # Validate it's a valid UUID
        uuid.UUID(data["conversation_id"])

    def test_chat_rejects_empty_message(
        self, client, test_user, auth_headers
    ):
        """POST with empty message returns 422 validation error."""
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": ""},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_chat_requires_auth(self, client, test_user):
        """POST without auth token returns 401."""
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": "Add a task"},
        )
        assert response.status_code == 401

    def test_chat_rejects_user_id_mismatch(
        self, client, test_user, another_user, auth_headers
    ):
        """POST with mismatched user_id returns 403."""
        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=("ok", []),
        ):
            response = client.post(
                f"/api/{another_user.id}/chat",
                json={"message": "Add a task"},
                headers=auth_headers,
            )
        assert response.status_code == 403
