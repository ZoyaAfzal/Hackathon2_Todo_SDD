"""Integration tests for US4: Update task via chat."""

import uuid
from unittest.mock import AsyncMock, patch

from src.api.schemas.chat import ToolCallInfo
from src.models.task import Task


class TestChatUpdateTask:
    """Test updating tasks through the chat endpoint."""

    def test_update_task_title_via_chat(
        self, client, session, test_user, auth_headers
    ):
        """Chat message to update task title changes it in DB."""
        task = Task(
            id=uuid.uuid4(), title="Buy groceries",
            completed=False, user_id=test_user.id,
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Simulate agent updating
        task.title = "Buy organic groceries"
        task.version = 2
        session.add(task)
        session.commit()

        mock_reply = "Task updated to 'Buy organic groceries'."

        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=(mock_reply, [
                ToolCallInfo(
                    tool_name="update_task",
                    arguments={"task_id": str(task.id), "title": "Buy organic groceries"},
                )
            ]),
        ):
            response = client.post(
                f"/api/{test_user.id}/chat",
                json={"message": f"Change task {task.id} title to Buy organic groceries"},
                headers=auth_headers,
            )

        assert response.status_code == 200
        session.refresh(task)
        assert task.title == "Buy organic groceries"
