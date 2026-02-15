"""Integration tests for task persistence across sessions.

Tests that tasks persist in the database and survive session changes.
"""

import pytest
from fastapi.testclient import TestClient


class TestTaskPersistence:
    """Test task persistence across sessions."""

    def test_created_task_persists_in_database(
        self, client: TestClient, auth_headers: dict, session
    ):
        """Created task can be retrieved from database."""
        # Create a task
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Persistent Task", "description": "Should persist"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Retrieve the task
        get_response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Persistent Task"

    def test_task_appears_in_list_after_creation(
        self, client: TestClient, auth_headers: dict, session
    ):
        """Created task appears in task list."""
        # Create a task
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Listed Task"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # List tasks
        list_response = client.get("/api/v1/tasks", headers=auth_headers)
        task_ids = [t["id"] for t in list_response.json()["tasks"]]

        assert task_id in task_ids

    def test_multiple_tasks_persist(
        self, client: TestClient, auth_headers: dict, session
    ):
        """Multiple created tasks all persist."""
        task_ids = []

        # Create multiple tasks
        for i in range(5):
            response = client.post(
                "/api/v1/tasks",
                json={"title": f"Task {i + 1}"},
                headers=auth_headers,
            )
            task_ids.append(response.json()["id"])

        # List tasks and verify all exist
        list_response = client.get("/api/v1/tasks", headers=auth_headers)
        listed_ids = [t["id"] for t in list_response.json()["tasks"]]

        for task_id in task_ids:
            assert task_id in listed_ids

    def test_task_details_match_creation_data(
        self, client: TestClient, auth_headers: dict, session
    ):
        """Retrieved task matches creation data."""
        create_data = {
            "title": "Detailed Task",
            "description": "With a long description",
        }

        create_response = client.post(
            "/api/v1/tasks",
            json=create_data,
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        get_response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        task = get_response.json()

        assert task["title"] == create_data["title"]
        assert task["description"] == create_data["description"]
        assert task["completed"] is False
        assert task["version"] == 1

    def test_task_has_timestamps(
        self, client: TestClient, auth_headers: dict, session
    ):
        """Created task has created_at and updated_at timestamps."""
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Timestamped Task"},
            headers=auth_headers,
        )
        task = create_response.json()

        assert "created_at" in task
        assert "updated_at" in task
        assert task["created_at"] is not None
        assert task["updated_at"] is not None

    def test_task_has_uuid_id(
        self, client: TestClient, auth_headers: dict, session
    ):
        """Created task has a valid UUID id."""
        import uuid

        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "UUID Task"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # Should be a valid UUID
        parsed_uuid = uuid.UUID(task_id)
        assert str(parsed_uuid) == task_id
