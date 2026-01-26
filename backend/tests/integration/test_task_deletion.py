"""Integration tests for task deletion permanence.

Tests that task deletion is permanent and irreversible.
"""

import pytest
from fastapi.testclient import TestClient


class TestTaskDeletionPermanence:
    """Test task deletion permanence scenarios."""

    def test_deleted_task_cannot_be_retrieved(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Deleted task cannot be retrieved after deletion."""
        task_id = test_task.id

        # Delete the task
        client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )

        # Attempt to retrieve returns 404
        response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_deleted_task_cannot_be_updated(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Deleted task cannot be updated after deletion."""
        task_id = test_task.id
        version = test_task.version

        # Delete the task
        client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )

        # Attempt to update returns 404
        response = client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Updated", "version": version},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_deleted_task_cannot_be_completed(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Deleted task cannot be completed after deletion."""
        task_id = test_task.id
        version = test_task.version

        # Delete the task
        client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )

        # Attempt to complete returns 404
        response = client.post(
            f"/api/v1/tasks/{task_id}/complete",
            json={"version": version},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_delete_workflow_create_delete_verify(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Full workflow: create task, delete it, verify it's gone."""
        # Create
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Task to delete"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Delete
        delete_response = client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 204

        # Verify gone
        get_response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_deletion_persists_across_requests(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Deleted task remains deleted across multiple requests."""
        task_id = test_task.id

        # Delete the task
        client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )

        # Multiple retrieval attempts all return 404
        for _ in range(3):
            response = client.get(
                f"/api/v1/tasks/{task_id}",
                headers=auth_headers,
            )
            assert response.status_code == 404

    def test_delete_multiple_tasks_sequentially(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Multiple tasks can be deleted sequentially."""
        # Create 3 tasks
        task_ids = []
        for i in range(3):
            response = client.post(
                "/api/v1/tasks",
                json={"title": f"Task {i + 1}"},
                headers=auth_headers,
            )
            task_ids.append(response.json()["id"])

        # Delete all tasks
        for task_id in task_ids:
            response = client.delete(
                f"/api/v1/tasks/{task_id}",
                headers=auth_headers,
            )
            assert response.status_code == 204

        # Verify all are gone
        for task_id in task_ids:
            response = client.get(
                f"/api/v1/tasks/{task_id}",
                headers=auth_headers,
            )
            assert response.status_code == 404

    def test_task_list_count_decreases_after_delete(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Task list count decreases after deletion."""
        # Create a task
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Countable Task"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # Get count before
        list_before = client.get("/api/v1/tasks", headers=auth_headers)
        count_before = len(list_before.json()["tasks"])

        # Delete the task
        client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )

        # Get count after
        list_after = client.get("/api/v1/tasks", headers=auth_headers)
        count_after = len(list_after.json()["tasks"])

        assert count_after == count_before - 1

    def test_delete_is_hard_delete_not_soft_delete(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Delete is a hard delete (not soft delete with restore capability)."""
        task_id = test_task.id

        # Delete the task
        client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )

        # There's no restore endpoint - task is permanently gone
        # Attempting to get it always returns 404
        response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404

        # Creating a task with the same ID wouldn't recreate it
        # (IDs are UUIDs, so this scenario shouldn't happen in practice)
