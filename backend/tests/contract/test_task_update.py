"""Contract tests for task update endpoint.

Tests PUT /api/v1/tasks/{task_id} per API contract.
"""

import uuid

import pytest
from fastapi.testclient import TestClient


class TestTaskUpdateContract:
    """Test task update endpoint contract compliance."""

    def test_update_task_returns_200_with_updated_task(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """PUT /api/v1/tasks/{task_id} returns 200 with updated task."""
        response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={
                "title": "Updated Title",
                "description": "Updated description",
                "version": test_task.version,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_task.id)
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        assert data["version"] == test_task.version + 1

    def test_update_task_increments_version(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Update increments the task version."""
        original_version = test_task.version

        response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "New Title", "version": original_version},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["version"] == original_version + 1

    def test_update_task_with_partial_data(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Update with only title preserves description."""
        original_description = test_task.description

        response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "Only Title Changed", "version": test_task.version},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Only Title Changed"
        assert data["description"] == original_description

    def test_update_task_without_version_returns_422(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Update without version returns 422 validation error."""
        response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "No Version"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_update_nonexistent_task_returns_404(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Update non-existent task returns 404."""
        fake_id = str(uuid.uuid4())
        response = client.put(
            f"/api/v1/tasks/{fake_id}",
            json={"title": "Ghost Task", "version": 1},
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    def test_update_task_without_auth_returns_401(
        self,
        client: TestClient,
        test_task,
        session,
    ):
        """Update without authentication returns 401."""
        response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "Unauthorized", "version": 1},
        )

        assert response.status_code == 401

    def test_update_task_with_empty_title_returns_422(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Update with empty title returns 422."""
        response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "", "version": test_task.version},
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_update_task_updates_updated_at_timestamp(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Update modifies the updated_at timestamp."""
        original_updated_at = test_task.updated_at.isoformat()

        response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "Timestamp Test", "version": test_task.version},
            headers=auth_headers,
        )

        assert response.status_code == 200
        # updated_at should be different (or at least not earlier)
        new_updated_at = response.json()["updated_at"]
        assert new_updated_at >= original_updated_at

    def test_update_task_can_set_completed_status(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Update can change completed status."""
        response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"completed": True, "version": test_task.version},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["completed"] is True
