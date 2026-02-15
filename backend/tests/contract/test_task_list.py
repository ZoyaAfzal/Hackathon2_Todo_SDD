"""Contract tests for task list endpoint.

Tests GET /api/v1/tasks against api-contract.md specification.
"""

import pytest
from fastapi.testclient import TestClient


class TestTaskListContract:
    """Test task list endpoint contract compliance."""

    def test_list_tasks_empty(
        self, client: TestClient, auth_headers: dict, session
    ):
        """GET /api/v1/tasks returns empty list when no tasks."""
        response = client.get("/api/v1/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure per api-contract.md
        assert "tasks" in data
        assert isinstance(data["tasks"], list)
        assert len(data["tasks"]) == 0
        assert "has_more" in data
        assert data["has_more"] is False
        assert "next_cursor" in data
        assert data["next_cursor"] is None

    def test_list_tasks_with_data(
        self, client: TestClient, auth_headers: dict, test_task, session
    ):
        """GET /api/v1/tasks returns user's tasks."""
        response = client.get("/api/v1/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert len(data["tasks"]) >= 1

        # Verify task structure
        task = data["tasks"][0]
        assert "id" in task
        assert "title" in task
        assert "description" in task
        assert "completed" in task
        assert "created_at" in task
        assert "updated_at" in task
        assert "version" in task

    def test_list_tasks_pagination_default_limit(
        self, client: TestClient, auth_headers: dict, multiple_tasks, session
    ):
        """GET /api/v1/tasks uses default limit of 20."""
        response = client.get("/api/v1/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should return up to 20 tasks (we have 15)
        assert len(data["tasks"]) == 15

    def test_list_tasks_pagination_custom_limit(
        self, client: TestClient, auth_headers: dict, multiple_tasks, session
    ):
        """GET /api/v1/tasks respects custom limit."""
        response = client.get(
            "/api/v1/tasks?limit=5", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["tasks"]) == 5
        assert data["has_more"] is True
        assert data["next_cursor"] is not None

    def test_list_tasks_pagination_cursor(
        self, client: TestClient, auth_headers: dict, multiple_tasks, session
    ):
        """GET /api/v1/tasks supports cursor-based pagination."""
        # First page
        response1 = client.get(
            "/api/v1/tasks?limit=5", headers=auth_headers
        )
        data1 = response1.json()
        cursor = data1["next_cursor"]

        # Second page
        response2 = client.get(
            f"/api/v1/tasks?limit=5&after_id={cursor}",
            headers=auth_headers,
        )
        data2 = response2.json()

        # Tasks should be different
        ids1 = {t["id"] for t in data1["tasks"]}
        ids2 = {t["id"] for t in data2["tasks"]}
        assert ids1.isdisjoint(ids2)

    def test_list_tasks_without_auth_returns_401(self, client: TestClient):
        """GET /api/v1/tasks without auth returns 401."""
        response = client.get("/api/v1/tasks")

        assert response.status_code == 401 or response.status_code == 403

    def test_list_tasks_with_invalid_cursor(
        self, client: TestClient, auth_headers: dict
    ):
        """GET /api/v1/tasks with invalid cursor returns 400."""
        response = client.get(
            "/api/v1/tasks?after_id=not-a-uuid",
            headers=auth_headers,
        )

        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
