"""Contract tests for JWT verification.

Tests that JWT tokens are correctly verified according to auth-contract.md.
"""

import pytest
from fastapi.testclient import TestClient


class TestJWTVerificationContract:
    """Test JWT verification contract compliance."""

    def test_valid_token_grants_access(
        self, client: TestClient, valid_token: str
    ):
        """Request with valid JWT token succeeds."""
        response = client.get(
            "/api/v1/tasks",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        # Should succeed (200) or return empty list
        assert response.status_code == 200

    def test_expired_token_returns_401(
        self, client: TestClient, expired_token: str
    ):
        """Request with expired JWT token returns 401."""
        response = client.get(
            "/api/v1/tasks",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "unauthorized"
        assert "expired" in data["error"]["message"].lower()

    def test_invalid_token_returns_401(
        self, client: TestClient, invalid_token: str
    ):
        """Request with invalid JWT token returns 401."""
        response = client.get(
            "/api/v1/tasks",
            headers={"Authorization": f"Bearer {invalid_token}"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "unauthorized"

    def test_missing_token_returns_401(self, client: TestClient):
        """Request without Authorization header returns 401."""
        response = client.get("/api/v1/tasks")

        assert response.status_code == 401 or response.status_code == 403

    def test_malformed_token_returns_401(self, client: TestClient):
        """Request with malformed token returns 401."""
        response = client.get(
            "/api/v1/tasks",
            headers={"Authorization": "Bearer not.a.valid.jwt"},
        )

        assert response.status_code == 401

    def test_wrong_auth_scheme_returns_401(self, client: TestClient):
        """Request with non-Bearer auth scheme returns 401."""
        response = client.get(
            "/api/v1/tasks",
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )

        assert response.status_code == 401 or response.status_code == 403

    def test_token_with_missing_sub_returns_401(self, client: TestClient):
        """Token without 'sub' claim returns 401."""
        import jwt
        from datetime import datetime, timedelta
        from src.core.config import settings

        # Create token without 'sub' claim
        payload = {
            "email": "test@example.com",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24),
        }
        token = jwt.encode(
            payload, settings.BETTER_AUTH_SECRET, algorithm="HS256"
        )

        response = client.get(
            "/api/v1/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "subject" in data["error"]["message"].lower() or "sub" in data["error"]["message"].lower()

    def test_www_authenticate_header_on_401(
        self, client: TestClient, expired_token: str
    ):
        """401 responses include WWW-Authenticate header."""
        response = client.get(
            "/api/v1/tasks",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401
        assert "www-authenticate" in [h.lower() for h in response.headers.keys()]
