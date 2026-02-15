"""Integration tests for task update persistence.

Tests that task updates persist correctly across sessions.
"""

import pytest
from fastapi.testclient import TestClient


class TestTaskUpdatePersistence:
    """Test task update persistence scenarios."""

    def test_updated_task_persists_after_session(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Updated task data persists and can be retrieved."""
        # Update the task
        update_response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={
                "title": "Persisted Title",
                "description": "Persisted Description",
                "version": test_task.version,
            },
            headers=auth_headers,
        )
        assert update_response.status_code == 200

        # Retrieve the task
        get_response = client.get(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
        )

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["title"] == "Persisted Title"
        assert data["description"] == "Persisted Description"

    def test_multiple_updates_persist_correctly(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Multiple sequential updates all persist correctly."""
        task_id = test_task.id
        current_version = test_task.version

        # First update
        response1 = client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Update 1", "version": current_version},
            headers=auth_headers,
        )
        current_version = response1.json()["version"]

        # Second update
        response2 = client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Update 2", "version": current_version},
            headers=auth_headers,
        )
        current_version = response2.json()["version"]

        # Third update
        response3 = client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Update 3", "version": current_version},
            headers=auth_headers,
        )

        # Verify final state
        get_response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        data = get_response.json()
        assert data["title"] == "Update 3"
        assert data["version"] == test_task.version + 3

    def test_updated_task_appears_in_list(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Updated task shows new data in task list."""
        new_title = "Listed Update"

        # Update the task
        client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": new_title, "version": test_task.version},
            headers=auth_headers,
        )

        # Get task list
        list_response = client.get("/api/v1/tasks", headers=auth_headers)
        tasks = list_response.json()["tasks"]

        # Find the updated task
        updated_task = next(
            (t for t in tasks if t["id"] == str(test_task.id)), None
        )

        assert updated_task is not None
        assert updated_task["title"] == new_title

    def test_description_update_persists_null_to_value(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Setting description from null to value persists."""
        # Create task without description
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "No Description Task"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]
        version = create_response.json()["version"]

        # Update with description
        update_response = client.put(
            f"/api/v1/tasks/{task_id}",
            json={"description": "Now has description", "version": version},
            headers=auth_headers,
        )
        assert update_response.status_code == 200

        # Verify persistence
        get_response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.json()["description"] == "Now has description"

    def test_completed_via_update_persists(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Completing task via PUT endpoint persists."""
        # Complete via update
        update_response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={"completed": True, "version": test_task.version},
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["completed"] is True

        # Verify persistence
        get_response = client.get(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
        )
        assert get_response.json()["completed"] is True

    def test_update_workflow_create_update_verify(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Full workflow: create task, update it, verify changes."""
        # Create
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Original", "description": "Original desc"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        version = create_response.json()["version"]

        # Update
        update_response = client.put(
            f"/api/v1/tasks/{task_id}",
            json={
                "title": "Modified",
                "description": "Modified desc",
                "version": version,
            },
            headers=auth_headers,
        )
        assert update_response.status_code == 200

        # Verify
        get_response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        data = get_response.json()
        assert data["title"] == "Modified"
        assert data["description"] == "Modified desc"
        assert data["version"] == version + 1
