"""JWT authentication dependency for FastAPI."""

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.config import settings

# HTTP Bearer scheme for JWT tokens
security = HTTPBearer()


@dataclass
class TokenPayload:
    """Decoded JWT token payload.

    Attributes:
        user_id: User's unique identifier from 'sub' claim
        email: User's email address
    """

    user_id: UUID
    email: str


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> TokenPayload:
    """
    Verify JWT token and extract user information.

    This dependency extracts the JWT token from the Authorization header,
    verifies its signature using BETTER_AUTH_SECRET, and returns the
    decoded payload with user information.

    Args:
        credentials: HTTP Bearer credentials containing the JWT token

    Returns:
        TokenPayload with user_id and email

    Raises:
        HTTPException 401: If token is invalid, expired, or missing required claims
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # Extract user_id from 'sub' claim (standard JWT subject claim)
        user_id_str = payload.get("sub")
        email = payload.get("email")

        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenPayload(
            user_id=UUID(user_id_str),
            email=email or "",
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except ValueError:
        # Invalid UUID in 'sub' claim
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: malformed subject",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Type alias for dependency injection
CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]
