"""Authentication routes for registration, login, and logout.

Provides endpoints:
- POST /api/auth/register - User registration
- POST /api/auth/login - User login
- POST /api/auth/logout - User logout
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlmodel import Session

from src.api.deps.auth import CurrentUser
from src.api.deps.database import get_session
from src.api.schemas.auth import AuthResponse, UserCreate, UserLogin, UserResponse
from src.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def get_auth_service_dep(
    session: Annotated[Session, Depends(get_session)],
) -> AuthService:
    """Dependency to get auth service with session."""
    return get_auth_service(session)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User registered successfully"},
        400: {"description": "Validation error"},
        409: {"description": "Email already exists"},
    },
)
async def register(
    user_data: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service_dep)],
) -> AuthResponse:
    """Register a new user.

    Creates a new user account with email and password.
    Returns the user data and a JWT token for authentication.

    Args:
        user_data: Registration data (email, password, optional name)
        auth_service: Auth service instance

    Returns:
        AuthResponse with user data and JWT token

    Raises:
        HTTPException 400: Invalid request data
        HTTPException 409: Email already registered
    """
    try:
        user, token = auth_service.register(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
        )

        return AuthResponse(
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                name=user_data.name,
                created_at=user.created_at,
            ),
            token=token,
        )

    except ValueError as e:
        error_code = str(e)
        if error_code == "email_exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "email_exists",
                        "message": "Email address is already registered",
                        "details": {},
                    }
                },
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "validation_error",
                    "message": str(e),
                    "details": {},
                }
            },
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Login successful"},
        400: {"description": "Validation error"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    credentials: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service_dep)],
) -> AuthResponse:
    """Authenticate a user and return a token.

    Verifies email and password, then returns user data and JWT token.

    Args:
        credentials: Login credentials (email, password)
        auth_service: Auth service instance

    Returns:
        AuthResponse with user data and JWT token

    Raises:
        HTTPException 401: Invalid email or password
    """
    try:
        user, token = auth_service.authenticate(
            email=credentials.email,
            password=credentials.password,
        )

        return AuthResponse(
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                name=None,  # User model doesn't store name currently
                created_at=user.created_at,
            ),
            token=token,
        )

    except ValueError as e:
        error_code = str(e)
        if error_code == "invalid_credentials":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "invalid_credentials",
                        "message": "Invalid email or password",
                        "details": {},
                    }
                },
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "validation_error",
                    "message": str(e),
                    "details": {},
                }
            },
        )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Logout successful"},
        401: {"description": "Not authenticated"},
    },
)
async def logout(
    current_user: CurrentUser,
) -> None:
    """Log out the current user.

    This endpoint acknowledges a logout request. In a stateless JWT
    implementation, the actual token invalidation happens on the client
    by discarding the token.

    For enhanced security, a token blocklist could be implemented to
    invalidate tokens server-side before expiration.

    Args:
        current_user: Authenticated user from JWT

    Returns:
        204 No Content on success
    """
    # In stateless JWT, logout is primarily a client-side operation.
    # The server acknowledges the request.
    # For production, consider implementing a token blocklist.
    return None
