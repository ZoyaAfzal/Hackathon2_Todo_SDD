"""Integration tests for task completion persistence.

Tests that task completion status persists correctly across sessions.
"""

import pytest
from fastapi.testclient import TestClient


class TestTaskCompletionPersistence:
    """Test task completion persistence scenarios."""

    def test_completed_status_persists_after_session(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Completed status persists and can be retrieved."""
        # Complete the task
        complete_response = client.post(
            f"/api/v1/tasks/{test_task.id}/complete",
            json={"version": test_task.version},
            headers=auth_headers,
        )
        assert complete_response.status_code == 200

        # Retrieve the task
        get_response = client.get(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
        )

        assert get_response.status_code == 200
        assert get_response.json()["completed"] is True

    def test_uncompleted_status_persists_after_session(
        self,
        client: TestClient,
        auth_headers: dict,
        completed_task,
        session,
    ):
        """Uncompleted status persists and can be retrieved."""
        # Uncomplete the task
        uncomplete_response = client.post(
            f"/api/v1/tasks/{completed_task.id}/uncomplete",
            json={"version": completed_task.version},
            headers=auth_headers,
        )
        assert uncomplete_response.status_code == 200

        # Retrieve the task
        get_response = client.get(
            f"/api/v1/tasks/{completed_task.id}",
            headers=auth_headers,
        )

        assert get_response.status_code == 200
        assert get_response.json()["completed"] is False

    def test_toggle_complete_multiple_times(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Task can be toggled complete/incomplete multiple times."""
        task_id = test_task.id
        current_version = test_task.version

        # Complete
        response1 = client.post(
            f"/api/v1/tasks/{task_id}/complete",
            json={"version": current_version},
            headers=auth_headers,
        )
        assert response1.json()["completed"] is True
        current_version = response1.json()["version"]

        # Uncomplete
        response2 = client.post(
            f"/api/v1/tasks/{task_id}/uncomplete",
            json={"version": current_version},
            headers=auth_headers,
        )
        assert response2.json()["completed"] is False
        current_version = response2.json()["version"]

        # Complete again
        response3 = client.post(
            f"/api/v1/tasks/{task_id}/complete",
            json={"version": current_version},
            headers=auth_headers,
        )
        assert response3.json()["completed"] is True

        # Verify final state
        get_response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.json()["completed"] is True
        assert get_response.json()["version"] == test_task.version + 3

    def test_completed_task_appears_in_list(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Completed task shows in task list with correct status."""
        # Complete the task
        client.post(
            f"/api/v1/tasks/{test_task.id}/complete",
            json={"version": test_task.version},
            headers=auth_headers,
        )

        # Get task list
        list_response = client.get("/api/v1/tasks", headers=auth_headers)
        tasks = list_response.json()["tasks"]

        # Find the task
        task = next((t for t in tasks if t["id"] == str(test_task.id)), None)

        assert task is not None
        assert task["completed"] is True

    def test_completion_workflow_create_complete_verify(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Full workflow: create task, complete it, verify status."""
        # Create
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Task to complete"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        version = create_response.json()["version"]
        assert create_response.json()["completed"] is False

        # Complete
        complete_response = client.post(
            f"/api/v1/tasks/{task_id}/complete",
            json={"version": version},
            headers=auth_headers,
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["completed"] is True

        # Verify
        get_response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.json()["completed"] is True

    def test_completion_status_survives_concurrent_updates(
        self,
        client: TestClient,
        auth_headers: dict,
        test_task,
        session,
    ):
        """Completion status persists even after title update."""
        task_id = test_task.id
        version = test_task.version

        # Complete the task
        complete_response = client.post(
            f"/api/v1/tasks/{task_id}/complete",
            json={"version": version},
            headers=auth_headers,
        )
        new_version = complete_response.json()["version"]

        # Update the title (should preserve completion)
        update_response = client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Updated Title", "version": new_version},
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Title"
        assert update_response.json()["completed"] is True

    def test_completion_across_different_api_calls(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Create multiple tasks, complete some, verify mixed states."""
        # Create 3 tasks
        task_ids = []
        versions = []
        for i in range(3):
            response = client.post(
                "/api/v1/tasks",
                json={"title": f"Task {i + 1}"},
                headers=auth_headers,
            )
            task_ids.append(response.json()["id"])
            versions.append(response.json()["version"])

        # Complete first and third tasks
        client.post(
            f"/api/v1/tasks/{task_ids[0]}/complete",
            json={"version": versions[0]},
            headers=auth_headers,
        )
        client.post(
            f"/api/v1/tasks/{task_ids[2]}/complete",
            json={"version": versions[2]},
            headers=auth_headers,
        )

        # Verify states
        for i, task_id in enumerate(task_ids):
            response = client.get(
                f"/api/v1/tasks/{task_id}",
                headers=auth_headers,
            )
            if i == 0 or i == 2:
                assert response.json()["completed"] is True
            else:
                assert response.json()["completed"] is False
