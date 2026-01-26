"""Integration tests for the complete authentication flow.

Tests the full registration-login flow from end to end.
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthenticationFlow:
    """Test complete authentication flows."""

    def test_register_then_login_flow(self, client: TestClient, session):
        """User can register and then immediately login."""
        email = "flowtest@example.com"
        password = "SecureP@ss123"

        # Step 1: Register
        register_response = client.post(
            "/api/auth/register",
            json={"email": email, "password": password, "name": "Flow Test"},
        )
        assert register_response.status_code == 200
        register_data = register_response.json()
        assert "token" in register_data
        registration_token = register_data["token"]

        # Step 2: Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "token" in login_data
        login_token = login_data["token"]

        # Both tokens should be valid JWTs
        assert len(registration_token) > 0
        assert len(login_token) > 0

    def test_register_token_can_access_protected_routes(
        self, client: TestClient, session
    ):
        """Token from registration can access protected routes."""
        # Register and get token
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "protected@example.com",
                "password": "SecureP@ss123",
            },
        )
        assert register_response.status_code == 200
        token = register_response.json()["token"]

        # Use token to access protected route
        tasks_response = client.get(
            "/api/v1/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert tasks_response.status_code == 200

    def test_login_token_can_access_protected_routes(
        self, client: TestClient, session
    ):
        """Token from login can access protected routes."""
        email = "loginprotected@example.com"
        password = "SecureP@ss123"

        # Register
        client.post(
            "/api/auth/register",
            json={"email": email, "password": password},
        )

        # Login and get fresh token
        login_response = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]

        # Use token to access protected route
        tasks_response = client.get(
            "/api/v1/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert tasks_response.status_code == 200

    def test_user_id_in_token_matches_user(self, client: TestClient, session):
        """User ID in JWT token matches the registered user."""
        import jwt
        from src.core.config import settings

        # Register
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "idcheck@example.com",
                "password": "SecureP@ss123",
            },
        )
        assert register_response.status_code == 200
        data = register_response.json()

        # Decode token and verify user ID matches
        token = data["token"]
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        assert payload["sub"] == data["user"]["id"]
        assert payload["email"] == "idcheck@example.com"

    def test_multiple_users_get_different_tokens(
        self, client: TestClient, session
    ):
        """Different users receive different tokens with unique user IDs."""
        import jwt
        from src.core.config import settings

        # Register user 1
        user1_response = client.post(
            "/api/auth/register",
            json={
                "email": "user1@example.com",
                "password": "SecureP@ss123",
            },
        )
        user1_token = user1_response.json()["token"]
        user1_payload = jwt.decode(
            user1_token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # Register user 2
        user2_response = client.post(
            "/api/auth/register",
            json={
                "email": "user2@example.com",
                "password": "SecureP@ss123",
            },
        )
        user2_token = user2_response.json()["token"]
        user2_payload = jwt.decode(
            user2_token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # User IDs should be different
        assert user1_payload["sub"] != user2_payload["sub"]
        assert user1_payload["email"] != user2_payload["email"]

    def test_token_contains_required_claims(self, client: TestClient, session):
        """JWT token contains all required claims per auth-contract.md."""
        import jwt
        from src.core.config import settings

        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "claims@example.com",
                "password": "SecureP@ss123",
            },
        )
        token = register_response.json()["token"]
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # Required claims per auth-contract.md
        assert "sub" in payload  # User ID
        assert "email" in payload  # User email
        assert "iat" in payload  # Issued at
        assert "exp" in payload  # Expiration

        # Expiration should be in the future
        import time

        assert payload["exp"] > time.time()
