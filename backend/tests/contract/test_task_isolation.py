"""Contract tests for task isolation between users.

Tests that users cannot access each other's tasks per FR-013.
Returns 404 (not 403) for non-owned resources to prevent enumeration.
"""

import uuid

import pytest
from fastapi.testclient import TestClient


class TestTaskIsolationContract:
    """Test task isolation contract compliance."""

    def test_get_other_user_task_returns_404(
        self,
        client: TestClient,
        another_user_headers: dict,
        test_task,
        session,
    ):
        """GET /api/v1/tasks/{task_id} for another user's task returns 404."""
        # test_task belongs to test_user, not another_user
        response = client.get(
            f"/api/v1/tasks/{test_task.id}",
            headers=another_user_headers,
        )

        # Should return 404, not 403, to prevent enumeration
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "not_found"

    def test_list_tasks_only_shows_own_tasks(
        self,
        client: TestClient,
        auth_headers: dict,
        another_user_headers: dict,
        test_task,
        session,
    ):
        """GET /api/v1/tasks only returns tasks owned by the user."""
        # test_task belongs to test_user
        # another_user should not see it
        response = client.get(
            "/api/v1/tasks",
            headers=another_user_headers,
        )

        assert response.status_code == 200
        task_ids = [t["id"] for t in response.json()["tasks"]]

        # test_task should not be in another_user's list
        assert str(test_task.id) not in task_ids

    def test_update_other_user_task_returns_404(
        self,
        client: TestClient,
        another_user_headers: dict,
        test_task,
        session,
    ):
        """PUT /api/v1/tasks/{task_id} for another user's task returns 404."""
        response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "Hacked Title", "version": test_task.version},
            headers=another_user_headers,
        )

        assert response.status_code == 404

    def test_delete_other_user_task_returns_404(
        self,
        client: TestClient,
        another_user_headers: dict,
        test_task,
        session,
    ):
        """DELETE /api/v1/tasks/{task_id} for another user's task returns 404."""
        response = client.delete(
            f"/api/v1/tasks/{test_task.id}",
            headers=another_user_headers,
        )

        assert response.status_code == 404

    def test_complete_other_user_task_returns_404(
        self,
        client: TestClient,
        another_user_headers: dict,
        test_task,
        session,
    ):
        """POST /api/v1/tasks/{task_id}/complete for another user's task returns 404."""
        response = client.post(
            f"/api/v1/tasks/{test_task.id}/complete",
            json={"version": test_task.version},
            headers=another_user_headers,
        )

        assert response.status_code == 404

    def test_uncomplete_other_user_task_returns_404(
        self,
        client: TestClient,
        another_user_headers: dict,
        completed_task,
        session,
    ):
        """POST /api/v1/tasks/{task_id}/uncomplete for another user's task returns 404."""
        response = client.post(
            f"/api/v1/tasks/{completed_task.id}/uncomplete",
            json={"version": completed_task.version},
            headers=another_user_headers,
        )

        assert response.status_code == 404

    def test_user_can_access_own_task_after_other_user_attempt(
        self,
        client: TestClient,
        auth_headers: dict,
        another_user_headers: dict,
        test_task,
        session,
    ):
        """User can still access their task after another user's failed attempt."""
        # Another user tries to access
        client.get(
            f"/api/v1/tasks/{test_task.id}",
            headers=another_user_headers,
        )

        # Original owner can still access
        response = client.get(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == str(test_task.id)
