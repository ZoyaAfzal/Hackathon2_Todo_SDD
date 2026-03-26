"""Contract tests for task deletion endpoint.

Tests DELETE /api/v1/tasks/{task_id} per API contract.
"""

import uuid

import pytest
from fastapi.testclient import TestClient


class TestTaskDeleteContract:
    """Test task deletion endpoint contract compliance."""

    def test_delete_task_returns_204_no_content(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """DELETE /api/v1/tasks/{task_id} returns 204 No Content."""
        response = client.delete(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204
        assert response.content == b""  # No response body

    def test_delete_removes_task_from_database(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Delete removes task from database."""
        # Delete the task
        delete_response = client.delete(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 204

        # Verify task no longer exists
        get_response = client.get(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_delete_nonexistent_task_returns_404(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Delete non-existent task returns 404."""
        fake_id = str(uuid.uuid4())
        response = client.delete(
            f"/api/v1/tasks/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    def test_delete_task_without_auth_returns_401(
        self,
        client: TestClient,
        test_task,
        session,
    ):
        """Delete without authentication returns 401."""
        response = client.delete(
            f"/api/v1/tasks/{test_task.id}",
        )

        assert response.status_code == 401

    def test_delete_twice_returns_404_second_time(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Deleting same task twice returns 404 on second attempt."""
        # First delete succeeds
        response1 = client.delete(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
        )
        assert response1.status_code == 204

        # Second delete returns 404
        response2 = client.delete(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
        )
        assert response2.status_code == 404

    def test_delete_completed_task_succeeds(
        self,
        client: TestClient,
        auth_headers: dict,
        completed_task,
        session,
    ):
        """Can delete a completed task."""
        response = client.delete(
            f"/api/v1/tasks/{completed_task.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    def test_delete_removes_from_task_list(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Deleted task no longer appears in task list."""
        task_id = str(test_task.id)

        # Verify task is in list before deletion
        list_before = client.get("/api/v1/tasks", headers=auth_headers)
        task_ids_before = [t["id"] for t in list_before.json()["tasks"]]
        assert task_id in task_ids_before

        # Delete the task
        client.delete(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
        )

        # Verify task is not in list after deletion
        list_after = client.get("/api/v1/tasks", headers=auth_headers)
        task_ids_after = [t["id"] for t in list_after.json()["tasks"]]
        assert task_id not in task_ids_after

    def test_delete_does_not_affect_other_tasks(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Deleting one task does not affect other tasks."""
        # Create two tasks
        task1 = client.post(
            "/api/v1/tasks",
            json={"title": "Task 1"},
            headers=auth_headers,
        ).json()
        task2 = client.post(
            "/api/v1/tasks",
            json={"title": "Task 2"},
            headers=auth_headers,
        ).json()

        # Delete task 1
        client.delete(
            f"/api/v1/tasks/{task1['id']}",
            headers=auth_headers,
        )

        # Task 2 still exists
        response = client.get(
            f"/api/v1/tasks/{task2['id']}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Task 2"
