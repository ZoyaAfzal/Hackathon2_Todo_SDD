"""Integration tests for logout flow.

Tests complete logout workflow with session handling.
"""

import pytest
from fastapi.testclient import TestClient


class TestLogoutFlow:
    """Test logout flow scenarios."""

    def test_logout_after_login(
        self,
        client: TestClient,
        session,
    ):
        """User can logout after logging in."""
        # Register a new user
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "logout_test@example.com",
                "password": "SecurePass123!",
            },
        )
        assert register_response.status_code == 200
        token = register_response.json()["token"]

        # Logout
        logout_response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert logout_response.status_code == 204

    def test_tasks_accessible_before_logout_acknowledged(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Tasks are accessible before logout is called."""
        # Create a task
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Pre-logout task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201

        # Tasks are accessible
        list_response = client.get(
            "/api/v1/tasks",
            headers=auth_headers,
        )
        assert list_response.status_code == 200

    def test_full_auth_workflow_register_tasks_logout(
        self,
        client: TestClient,
        session,
    ):
        """Full workflow: register, create tasks, logout."""
        # Register
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "workflow_test@example.com",
                "password": "SecurePass123!",
            },
        )
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create tasks
        for i in range(3):
            client.post(
                "/api/v1/tasks",
                json={"title": f"Task {i + 1}"},
                headers=headers,
            )

        # Verify tasks exist
        list_response = client.get("/api/v1/tasks", headers=headers)
        assert len(list_response.json()["tasks"]) == 3

        # Logout
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 204

    def test_login_after_logout_works(
        self,
        client: TestClient,
        session,
    ):
        """User can login again after logging out."""
        email = "relogin_test@example.com"
        password = "SecurePass123!"

        # Register
        client.post(
            "/api/auth/register",
            json={"email": email, "password": password},
        )

        # Login
        login1_response = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        assert login1_response.status_code == 200
        token1 = login1_response.json()["token"]

        # Logout
        client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token1}"},
        )

        # Login again
        login2_response = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        assert login2_response.status_code == 200
        token2 = login2_response.json()["token"]

        # New token works
        tasks_response = client.get(
            "/api/v1/tasks",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert tasks_response.status_code == 200

    def test_logout_endpoint_accepts_post_only(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Logout endpoint only accepts POST method."""
        # GET should fail
        get_response = client.get("/api/auth/logout", headers=auth_headers)
        assert get_response.status_code == 405

        # DELETE should fail
        delete_response = client.delete("/api/auth/logout", headers=auth_headers)
        assert delete_response.status_code == 405

        # PUT should fail
        put_response = client.put("/api/auth/logout", headers=auth_headers)
        assert put_response.status_code == 405
