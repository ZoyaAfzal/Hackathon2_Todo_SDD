"""Contract tests for user registration endpoint.

Tests the registration endpoint against the auth-contract.md specification.
These tests verify the API contract is correctly implemented.
"""

import pytest
from fastapi.testclient import TestClient


class TestRegistrationContract:
    """Test registration endpoint contract compliance."""

    def test_register_success_returns_user_and_token(
        self, client: TestClient, session
    ):
        """POST /api/auth/register with valid data returns user and token."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecureP@ss123",
                "name": "New User",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify user object structure
        assert "user" in data
        assert "id" in data["user"]
        assert data["user"]["email"] == "newuser@example.com"
        assert "name" in data["user"]

        # Verify token is returned
        assert "token" in data
        assert isinstance(data["token"], str)
        assert len(data["token"]) > 0

    def test_register_minimal_data_success(self, client: TestClient, session):
        """POST /api/auth/register with email and password only succeeds."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "minimal@example.com",
                "password": "SecureP@ss123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == "minimal@example.com"
        assert "token" in data

    def test_register_duplicate_email_returns_409(
        self, client: TestClient, session
    ):
        """POST /api/auth/register with existing email returns 409."""
        # First registration
        client.post(
            "/api/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "SecureP@ss123",
            },
        )

        # Duplicate registration
        response = client.post(
            "/api/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "AnotherP@ss123",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "email_exists"

    def test_register_invalid_email_returns_400(self, client: TestClient):
        """POST /api/auth/register with invalid email returns 400."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecureP@ss123",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "validation_error"

    def test_register_weak_password_returns_400(self, client: TestClient):
        """POST /api/auth/register with weak password returns 400."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "password": "weak",  # Less than 8 chars
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] in ["validation_error", "weak_password"]

    def test_register_missing_email_returns_400(self, client: TestClient):
        """POST /api/auth/register without email returns 400."""
        response = client.post(
            "/api/auth/register",
            json={
                "password": "SecureP@ss123",
            },
        )

        assert response.status_code == 400 or response.status_code == 422

    def test_register_missing_password_returns_400(self, client: TestClient):
        """POST /api/auth/register without password returns 400."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
            },
        )

        assert response.status_code == 400 or response.status_code == 422
