"""Contract tests for task creation endpoint.

Tests POST /api/v1/tasks against api-contract.md specification.
"""

import pytest
from fastapi.testclient import TestClient


class TestTaskCreateContract:
    """Test task creation endpoint contract compliance."""

    def test_create_task_success(
        self, client: TestClient, auth_headers: dict, session
    ):
        """POST /api/v1/tasks with valid data returns created task."""
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()

        # Verify response structure per api-contract.md
        assert "id" in data
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"
        assert data["completed"] is False
        assert "created_at" in data
        assert "updated_at" in data
        assert data["version"] == 1

    def test_create_task_minimal(
        self, client: TestClient, auth_headers: dict, session
    ):
        """POST /api/v1/tasks with title only succeeds."""
        response = client.post(
            "/api/v1/tasks",
            json={"title": "Minimal Task"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["description"] is None
        assert data["completed"] is False

    def test_create_task_empty_title_returns_400(
        self, client: TestClient, auth_headers: dict
    ):
        """POST /api/v1/tasks with empty title returns 400."""
        response = client.post(
            "/api/v1/tasks",
            json={"title": ""},
            headers=auth_headers,
        )

        assert response.status_code == 400 or response.status_code == 422
        data = response.json()
        assert "error" in data or "detail" in data

    def test_create_task_missing_title_returns_400(
        self, client: TestClient, auth_headers: dict
    ):
        """POST /api/v1/tasks without title returns 400."""
        response = client.post(
            "/api/v1/tasks",
            json={"description": "No title provided"},
            headers=auth_headers,
        )

        assert response.status_code == 400 or response.status_code == 422

    def test_create_task_title_too_long_returns_400(
        self, client: TestClient, auth_headers: dict
    ):
        """POST /api/v1/tasks with title > 255 chars returns 400."""
        response = client.post(
            "/api/v1/tasks",
            json={"title": "x" * 256},
            headers=auth_headers,
        )

        assert response.status_code == 400 or response.status_code == 422

    def test_create_task_without_auth_returns_401(self, client: TestClient):
        """POST /api/v1/tasks without auth returns 401."""
        response = client.post(
            "/api/v1/tasks",
            json={"title": "Unauthorized Task"},
        )

        assert response.status_code == 401 or response.status_code == 403

    def test_create_task_with_expired_token_returns_401(
        self, client: TestClient, expired_token: str
    ):
        """POST /api/v1/tasks with expired token returns 401."""
        response = client.post(
            "/api/v1/tasks",
            json={"title": "Expired Token Task"},
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401
