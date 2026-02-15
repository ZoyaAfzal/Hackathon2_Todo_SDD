"""Contract tests for task uncomplete endpoint.

Tests POST /api/v1/tasks/{task_id}/uncomplete per API contract.
"""

import uuid

import pytest
from fastapi.testclient import TestClient


class TestTaskUncompleteContract:
    """Test task uncomplete endpoint contract compliance."""

    def test_uncomplete_task_returns_200_with_incomplete_task(
        self,
        client: TestClient,
        auth_headers: dict,
        completed_task,
        session,
    ):
        """POST /api/v1/tasks/{task_id}/uncomplete returns 200 with incomplete task."""
        response = client.post(
            f"/api/v1/tasks/{completed_task.id}/uncomplete",
            json={"version": completed_task.version},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(completed_task.id)
        assert data["completed"] is False
        assert data["version"] == completed_task.version + 1

    def test_uncomplete_task_increments_version(
        self,
        client: TestClient,
        auth_headers: dict,
        completed_task,
        session,
    ):
        """Uncomplete increments the task version."""
        original_version = completed_task.version

        response = client.post(
            f"/api/v1/tasks/{completed_task.id}/uncomplete",
            json={"version": original_version},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["version"] == original_version + 1

    def test_uncomplete_task_without_version_returns_422(
        self,
        client: TestClient,
        auth_headers: dict,
        completed_task,
        session,
    ):
        """Uncomplete without version returns 422 validation error."""
        response = client.post(
            f"/api/v1/tasks/{completed_task.id}/uncomplete",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_uncomplete_nonexistent_task_returns_404(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Uncomplete non-existent task returns 404."""
        fake_id = str(uuid.uuid4())
        response = client.post(
            f"/api/v1/tasks/{fake_id}/uncomplete",
            json={"version": 1},
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    def test_uncomplete_task_without_auth_returns_401(
        self,
        client: TestClient,
        completed_task,
        session,
    ):
        """Uncomplete without authentication returns 401."""
        response = client.post(
            f"/api/v1/tasks/{completed_task.id}/uncomplete",
            json={"version": 1},
        )

        assert response.status_code == 401

    def test_uncomplete_already_incomplete_task_succeeds(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Uncompleting already incomplete task still succeeds."""
        response = client.post(
            f"/api/v1/tasks/{test_task.id}/uncomplete",
            json={"version": test_task.version},
            headers=auth_headers,
        )

        # Should succeed even if already incomplete
        assert response.status_code == 200
        assert response.json()["completed"] is False

    def test_uncomplete_task_updates_updated_at_timestamp(
        self,
        client: TestClient,
        auth_headers: dict,
        completed_task,
        session,
    ):
        """Uncomplete modifies the updated_at timestamp."""
        original_updated_at = completed_task.updated_at.isoformat()

        response = client.post(
            f"/api/v1/tasks/{completed_task.id}/uncomplete",
            json={"version": completed_task.version},
            headers=auth_headers,
        )

        assert response.status_code == 200
        new_updated_at = response.json()["updated_at"]
        assert new_updated_at >= original_updated_at

    def test_uncomplete_preserves_other_task_fields(
        self,
        client: TestClient,
        auth_headers: dict,
        completed_task,
        session,
    ):
        """Uncomplete preserves title and description."""
        original_title = completed_task.title
        original_description = completed_task.description

        response = client.post(
            f"/api/v1/tasks/{completed_task.id}/uncomplete",
            json={"version": completed_task.version},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == original_title
        assert data["description"] == original_description
