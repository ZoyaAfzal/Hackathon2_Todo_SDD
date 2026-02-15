"""Contract tests for logout endpoint.

Tests POST /api/auth/logout per API contract.
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthLogoutContract:
    """Test logout endpoint contract compliance."""

    def test_logout_returns_204_no_content(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """POST /api/auth/logout returns 204 No Content."""
        response = client.post(
            "/api/auth/logout",
            headers=auth_headers,
        )

        assert response.status_code == 204
        assert response.content == b""  # No response body

    def test_logout_without_auth_returns_401(
        self,
        client: TestClient,
        session,
    ):
        """Logout without authentication returns 401."""
        response = client.post("/api/auth/logout")

        assert response.status_code == 401

    def test_logout_with_invalid_token_returns_401(
        self,
        client: TestClient,
        session,
    ):
        """Logout with invalid token returns 401."""
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401

    def test_logout_can_be_called_multiple_times(
        self,
        client: TestClient,
        auth_headers: dict,
        session,
    ):
        """Logout can be called multiple times with same token.

        Note: In a stateless JWT implementation, the token remains valid
        until expiration. Repeated logouts are acknowledged.
        """
        # First logout
        response1 = client.post(
            "/api/auth/logout",
            headers=auth_headers,
        )
        assert response1.status_code == 204

        # Second logout with same token (still valid JWT)
        response2 = client.post(
            "/api/auth/logout",
            headers=auth_headers,
        )
        # Stateless JWT means token is still valid
        assert response2.status_code == 204
