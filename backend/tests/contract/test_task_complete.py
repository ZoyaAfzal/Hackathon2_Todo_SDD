"""Contract tests for task completion endpoint.

Tests POST /api/v1/tasks/{task_id}/complete per API contract.
"""

import uuid

import pytest
from fastapi.testclient import TestClient


class TestTaskCompleteContract:
    """Test task completion endpoint contract compliance."""

    def test_complete_task_returns_200_with_completed_task(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """POST /api/v1/tasks/{task_id}/complete returns 200 with completed task."""
        response = client.post(
            f"/api/v1/tasks/{test_task.id}/complete",
            json={"version": test_task.version},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_task.id)
        assert data["completed"] is True
        assert data["version"] == test_task.version + 1

    def test_complete_task_increments_version(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Complete increments the task version."""
        original_version = test_task.version

        response = client.post(
            f"/api/v1/tasks/{test_task.id}/complete",
            json={"version": original_version},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["version"] == original_version + 1

    def test_complete_task_without_version_returns_422(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Complete without version returns 422 validation error."""
        response = client.post(
            f"/api/v1/tasks/{test_task.id}/complete",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_complete_nonexistent_task_returns_404(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Complete non-existent task returns 404."""
        fake_id = str(uuid.uuid4())
        response = client.post(
            f"/api/v1/tasks/{fake_id}/complete",
            json={"version": 1},
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    def test_complete_task_without_auth_returns_401(
        self,
        client: TestClient,
        test_task,
        session,
    ):
        """Complete without authentication returns 401."""
        response = client.post(
            f"/api/v1/tasks/{test_task.id}/complete",
            json={"version": 1},
        )

        assert response.status_code == 401

    def test_complete_already_completed_task_succeeds(
        self,
        client: TestClient,
        auth_headers: dict,
        completed_task,
        session,
    ):
        """Completing already completed task still succeeds."""
        response = client.post(
            f"/api/v1/tasks/{completed_task.id}/complete",
            json={"version": completed_task.version},
            headers=auth_headers,
        )

        # Should succeed even if already completed
        assert response.status_code == 200
        assert response.json()["completed"] is True

    def test_complete_task_updates_updated_at_timestamp(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Complete modifies the updated_at timestamp."""
        original_updated_at = test_task.updated_at.isoformat()

        response = client.post(
            f"/api/v1/tasks/{test_task.id}/complete",
            json={"version": test_task.version},
            headers=auth_headers,
        )

        assert response.status_code == 200
        new_updated_at = response.json()["updated_at"]
        assert new_updated_at >= original_updated_at

    def test_complete_preserves_other_task_fields(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Complete preserves title and description."""
        original_title = test_task.title
        original_description = test_task.description

        response = client.post(
            f"/api/v1/tasks/{test_task.id}/complete",
            json={"version": test_task.version},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == original_title
        assert data["description"] == original_description
