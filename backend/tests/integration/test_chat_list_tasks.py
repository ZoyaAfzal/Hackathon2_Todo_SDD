"""Integration tests for US2: List tasks via chat."""

import uuid
from unittest.mock import AsyncMock, patch

from src.api.schemas.chat import ToolCallInfo
from src.models.task import Task


class TestChatListTasks:
    """Test listing tasks through the chat endpoint."""

    def test_list_pending_tasks(
        self, client, session, test_user, auth_headers
    ):
        """Chat message to list pending tasks returns correct count."""
        # Create 3 pending + 2 completed tasks
        for i in range(3):
            session.add(Task(
                id=uuid.uuid4(), title=f"Pending {i}",
                completed=False, user_id=test_user.id,
            ))
        for i in range(2):
            session.add(Task(
                id=uuid.uuid4(), title=f"Done {i}",
                completed=True, user_id=test_user.id,
            ))
        session.commit()

        mock_reply = "You have 3 pending tasks: Pending 0, Pending 1, Pending 2"

        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=(mock_reply, [
                ToolCallInfo(tool_name="list_tasks", arguments={"filter": "pending"})
            ]),
        ):
            response = client.post(
                f"/api/{test_user.id}/chat",
                json={"message": "Show me pending tasks"},
                headers=auth_headers,
            )

        assert response.status_code == 200
        assert "3" in response.json()["reply"] or "pending" in response.json()["reply"].lower()
