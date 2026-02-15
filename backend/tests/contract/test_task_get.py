"""Contract tests for get task by ID endpoint.

Tests GET /api/v1/tasks/{task_id} against api-contract.md specification.
"""

import uuid

import pytest
from fastapi.testclient import TestClient


class TestTaskGetContract:
    """Test get task endpoint contract compliance."""

    def test_get_task_success(
        self, client: TestClient, auth_headers: dict, test_task, session
    ):
        """GET /api/v1/tasks/{task_id} returns task details."""
        response = client.get(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure per api-contract.md
        assert data["id"] == str(test_task.id)
        assert data["title"] == test_task.title
        assert data["description"] == test_task.description
        assert data["completed"] == test_task.completed
        assert "created_at" in data
        assert "updated_at" in data
        assert "version" in data

    def test_get_task_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """GET /api/v1/tasks/{task_id} returns 404 for non-existent task."""
        non_existent_id = uuid.uuid4()
        response = client.get(
            f"/api/v1/tasks/{non_existent_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "not_found"

    def test_get_task_invalid_id_format(
        self, client: TestClient, auth_headers: dict
    ):
        """GET /api/v1/tasks/{task_id} with invalid UUID returns 422."""
        response = client.get(
            "/api/v1/tasks/not-a-uuid",
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_get_task_without_auth_returns_401(
        self, client: TestClient, test_task
    ):
        """GET /api/v1/tasks/{task_id} without auth returns 401."""
        response = client.get(f"/api/v1/tasks/{test_task.id}")

        assert response.status_code == 401 or response.status_code == 403

    def test_get_task_with_expired_token_returns_401(
        self, client: TestClient, expired_token: str, test_task
    ):
        """GET /api/v1/tasks/{task_id} with expired token returns 401."""
        response = client.get(
            f"/api/v1/tasks/{test_task.id}",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401
