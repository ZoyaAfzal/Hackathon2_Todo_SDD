"""Integration tests for user task isolation.

Tests complete isolation between two users in end-to-end scenarios.
"""

import pytest
from fastapi.testclient import TestClient


class TestUserIsolation:
    """Test complete user isolation scenarios."""

    def test_two_users_have_separate_task_lists(
        self,
        client: TestClient,
        auth_headers: dict,
        another_user_headers: dict,
        session,
    ):
        """Two users have completely separate task lists."""
        # User 1 creates tasks
        user1_tasks = []
        for i in range(3):
            response = client.post(
                "/api/v1/tasks",
                json={"title": f"User1 Task {i + 1}"},
                headers=auth_headers,
            )
            user1_tasks.append(response.json()["id"])

        # User 2 creates tasks
        user2_tasks = []
        for i in range(2):
            response = client.post(
                "/api/v1/tasks",
                json={"title": f"User2 Task {i + 1}"},
                headers=another_user_headers,
            )
            user2_tasks.append(response.json()["id"])

        # User 1 only sees their tasks
        user1_list = client.get("/api/v1/tasks", headers=auth_headers)
        user1_ids = [t["id"] for t in user1_list.json()["tasks"]]

        for task_id in user1_tasks:
            assert task_id in user1_ids
        for task_id in user2_tasks:
            assert task_id not in user1_ids

        # User 2 only sees their tasks
        user2_list = client.get("/api/v1/tasks", headers=another_user_headers)
        user2_ids = [t["id"] for t in user2_list.json()["tasks"]]

        for task_id in user2_tasks:
            assert task_id in user2_ids
        for task_id in user1_tasks:
            assert task_id not in user2_ids

    def test_user_cannot_modify_other_user_task(
        self,
        client: TestClient,
        auth_headers: dict,
        another_user_headers: dict,
        session,
    ):
        """User cannot update another user's task."""
        # User 1 creates a task
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "User1 Private Task"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]
        version = create_response.json()["version"]

        # User 2 attempts to update it
        update_response = client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Hacked by User2", "version": version},
            headers=another_user_headers,
        )

        # Should fail with 404
        assert update_response.status_code == 404

        # Original task should be unchanged
        get_response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.json()["title"] == "User1 Private Task"

    def test_user_cannot_delete_other_user_task(
        self,
        client: TestClient,
        auth_headers: dict,
        another_user_headers: dict,
        session,
    ):
        """User cannot delete another user's task."""
        # User 1 creates a task
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Protected Task"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # User 2 attempts to delete it
        delete_response = client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=another_user_headers,
        )

        # Should fail with 404
        assert delete_response.status_code == 404

        # Task should still exist
        get_response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 200

    def test_user_cannot_complete_other_user_task(
        self,
        client: TestClient,
        auth_headers: dict,
        another_user_headers: dict,
        session,
    ):
        """User cannot mark another user's task as complete."""
        # User 1 creates a task
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Incomplete Task"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]
        version = create_response.json()["version"]

        # User 2 attempts to complete it
        complete_response = client.post(
            f"/api/v1/tasks/{task_id}/complete",
            json={"version": version},
            headers=another_user_headers,
        )

        # Should fail with 404
        assert complete_response.status_code == 404

        # Task should still be incomplete
        get_response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.json()["completed"] is False

    def test_isolation_response_does_not_leak_existence(
        self,
        client: TestClient,
        auth_headers: dict,
        another_user_headers: dict,
        session,
    ):
        """404 response doesn't reveal if task exists."""
        import uuid

        # User 1 creates a task
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Secret Task"},
            headers=auth_headers,
        )
        existing_task_id = create_response.json()["id"]
        non_existent_id = str(uuid.uuid4())

        # User 2 tries to access existing task
        existing_response = client.get(
            f"/api/v1/tasks/{existing_task_id}",
            headers=another_user_headers,
        )

        # User 2 tries to access non-existent task
        non_existent_response = client.get(
            f"/api/v1/tasks/{non_existent_id}",
            headers=another_user_headers,
        )

        # Both should return identical 404 responses
        assert existing_response.status_code == 404
        assert non_existent_response.status_code == 404
        assert existing_response.json()["error"]["code"] == non_existent_response.json()["error"]["code"]
