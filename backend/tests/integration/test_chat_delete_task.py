"""Integration tests for US5: Delete task via chat."""

import uuid
from unittest.mock import AsyncMock, patch

from sqlmodel import select

from src.api.schemas.chat import ToolCallInfo
from src.models.task import Task


class TestChatDeleteTask:
    """Test deleting tasks through the chat endpoint."""

    def test_delete_task_via_chat(
        self, client, session, test_user, auth_headers
    ):
        """Chat message to delete a task removes it from DB."""
        task = Task(
            id=uuid.uuid4(), title="Buy groceries",
            completed=False, user_id=test_user.id,
        )
        session.add(task)
        session.commit()
        task_id = task.id

        # Simulate agent deleting
        session.delete(task)
        session.commit()

        mock_reply = "Task 'Buy groceries' deleted successfully."

        with patch(
            "src.services.chat_service._run_agent",
            new_callable=AsyncMock,
            return_value=(mock_reply, [
                ToolCallInfo(tool_name="delete_task", arguments={"task_id": str(task_id)})
            ]),
        ):
            response = client.post(
                f"/api/{test_user.id}/chat",
                json={"message": "Delete my groceries task"},
                headers=auth_headers,
            )

        assert response.status_code == 200
        # Verify task gone
        stmt = select(Task).where(Task.id == task_id)
        assert session.exec(stmt).first() is None
