"""Integration tests for US3: Complete task via chat."""

import uuid
from unittest.mock import AsyncMock, patch

from src.api.schemas.chat import ToolCallInfo
from src.models.task import Task


class TestChatCompleteTask:
    """Test completing tasks through the chat endpoint."""

    def test_complete_task_via_chat(
        self, client, session, test_user, auth_headers
    ):
        """Chat message to complete a task sets completed=true."""
        task = Task(
            id=uuid.uuid4(), title="Buy milk",
            completed=False, user_id=test_user.id,
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Simulate agent completing the task
        task.completed = True
        task.version = 2
        session.add(task)
        session.commit()

        mock_reply = f"Task 'Buy milk' marked as completed."

        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=(mock_reply, [
                ToolCallInfo(tool_name="complete_task", arguments={"task_id": str(task.id)})
            ]),
        ):
            response = client.post(
                f"/api/{test_user.id}/chat",
                json={"message": f"Mark task {task.id} as done"},
                headers=auth_headers,
            )

        assert response.status_code == 200
        session.refresh(task)
        assert task.completed is True

    def test_complete_nonexistent_task(
        self, client, session, test_user, auth_headers
    ):
        """Chat message to complete nonexistent task returns error in reply."""
        mock_reply = "Task with that ID was not found."

        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=(mock_reply, []),
        ):
            response = client.post(
                f"/api/{test_user.id}/chat",
                json={"message": "Complete task 999"},
                headers=auth_headers,
            )

        assert response.status_code == 200
        assert "not found" in response.json()["reply"].lower()
