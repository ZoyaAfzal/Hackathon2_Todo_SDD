"""Contract tests for optimistic locking version conflicts.

Tests that version conflicts return 409 Conflict per API contract.
"""

import pytest
from fastapi.testclient import TestClient


class TestVersionConflictContract:
    """Test optimistic locking version conflict handling."""

    def test_update_with_stale_version_returns_409(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Update with outdated version returns 409 Conflict."""
        # First update succeeds
        response1 = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "First Update", "version": test_task.version},
            headers=auth_headers,
        )
        assert response1.status_code == 200

        # Second update with old version fails
        response2 = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "Second Update", "version": test_task.version},
            headers=auth_headers,
        )

        assert response2.status_code == 409
        data = response2.json()
        assert data["error"]["code"] == "conflict"
        assert "modified" in data["error"]["message"].lower()

    def test_complete_with_stale_version_returns_409(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Complete with outdated version returns 409 Conflict."""
        stale_version = test_task.version

        # First update succeeds
        client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "Title Changed", "version": stale_version},
            headers=auth_headers,
        )

        # Complete with stale version fails
        response = client.post(
            f"/api/v1/tasks/{test_task.id}/complete",
            json={"version": stale_version},
            headers=auth_headers,
        )

        assert response.status_code == 409
        assert response.json()["error"]["code"] == "conflict"

    def test_uncomplete_with_stale_version_returns_409(
        self,
        client: TestClient,
        auth_headers: dict,
        completed_task,
        session,
    ):
        """Uncomplete with outdated version returns 409 Conflict."""
        stale_version = completed_task.version

        # First update the task
        client.put(
            f"/api/v1/tasks/{completed_task.id}",
            json={"title": "Title Changed", "version": stale_version},
            headers=auth_headers,
        )

        # Uncomplete with stale version fails
        response = client.post(
            f"/api/v1/tasks/{completed_task.id}/uncomplete",
            json={"version": stale_version},
            headers=auth_headers,
        )

        assert response.status_code == 409
        assert response.json()["error"]["code"] == "conflict"

    def test_update_with_correct_version_after_conflict(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Update succeeds with correct version after fetching latest."""
        original_version = test_task.version

        # First update succeeds
        response1 = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "First Update", "version": original_version},
            headers=auth_headers,
        )
        assert response1.status_code == 200
        new_version = response1.json()["version"]

        # Second update with stale version fails
        response2 = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "Stale Update", "version": original_version},
            headers=auth_headers,
        )
        assert response2.status_code == 409

        # Third update with correct version succeeds
        response3 = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "Correct Update", "version": new_version},
            headers=auth_headers,
        )
        assert response3.status_code == 200
        assert response3.json()["title"] == "Correct Update"
        assert response3.json()["version"] == new_version + 1

    def test_concurrent_updates_conflict_handling(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Simulated concurrent updates: only first succeeds."""
        version = test_task.version

        # Simulate two concurrent clients reading same version
        client_a_version = version
        client_b_version = version

        # Client A updates first
        response_a = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "Client A Update", "version": client_a_version},
            headers=auth_headers,
        )
        assert response_a.status_code == 200

        # Client B updates with stale version - should conflict
        response_b = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "Client B Update", "version": client_b_version},
            headers=auth_headers,
        )
        assert response_b.status_code == 409

        # Verify final state is from Client A
        get_response = client.get(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
        )
        assert get_response.json()["title"] == "Client A Update"

    def test_version_conflict_preserves_task_state(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Version conflict does not partially update task."""
        original_title = test_task.title
        original_version = test_task.version

        # First update changes the task
        client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "Successful Update", "version": original_version},
            headers=auth_headers,
        )

        # Conflicting update should fail completely
        response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={
                "title": "Failed Update",
                "description": "Failed Description",
                "version": original_version,
            },
            headers=auth_headers,
        )
        assert response.status_code == 409

        # Verify task state was not partially modified
        get_response = client.get(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
        )
        data = get_response.json()
        assert data["title"] == "Successful Update"
        assert data["description"] != "Failed Description"
