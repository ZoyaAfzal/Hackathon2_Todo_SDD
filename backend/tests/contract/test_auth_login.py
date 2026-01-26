"""Contract tests for user login endpoint.

Tests the login endpoint against the auth-contract.md specification.
"""

import pytest
from fastapi.testclient import TestClient


class TestLoginContract:
    """Test login endpoint contract compliance."""

    def test_login_success_returns_user_and_token(
        self, client: TestClient, session
    ):
        """POST /api/auth/login with valid credentials returns user and token."""
        # First register a user
        client.post(
            "/api/auth/register",
            json={
                "email": "logintest@example.com",
                "password": "SecureP@ss123",
            },
        )

        # Then login
        response = client.post(
            "/api/auth/login",
            json={
                "email": "logintest@example.com",
                "password": "SecureP@ss123",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify user object structure
        assert "user" in data
        assert "id" in data["user"]
        assert data["user"]["email"] == "logintest@example.com"

        # Verify token is returned
        assert "token" in data
        assert isinstance(data["token"], str)
        assert len(data["token"]) > 0

    def test_login_invalid_password_returns_401(
        self, client: TestClient, session
    ):
        """POST /api/auth/login with wrong password returns 401."""
        # First register a user
        client.post(
            "/api/auth/register",
            json={
                "email": "wrongpass@example.com",
                "password": "SecureP@ss123",
            },
        )

        # Attempt login with wrong password
        response = client.post(
            "/api/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "WrongPassword123",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "invalid_credentials"

    def test_login_nonexistent_user_returns_401(self, client: TestClient):
        """POST /api/auth/login with non-existent email returns 401."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SecureP@ss123",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "invalid_credentials"

    def test_login_missing_email_returns_400(self, client: TestClient):
        """POST /api/auth/login without email returns 400."""
        response = client.post(
            "/api/auth/login",
            json={
                "password": "SecureP@ss123",
            },
        )

        assert response.status_code == 400 or response.status_code == 422

    def test_login_missing_password_returns_400(self, client: TestClient):
        """POST /api/auth/login without password returns 400."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "user@example.com",
            },
        )

        assert response.status_code == 400 or response.status_code == 422

    def test_login_empty_body_returns_400(self, client: TestClient):
        """POST /api/auth/login with empty body returns 400."""
        response = client.post(
            "/api/auth/login",
            json={},
        )

        assert response.status_code == 400 or response.status_code == 422
