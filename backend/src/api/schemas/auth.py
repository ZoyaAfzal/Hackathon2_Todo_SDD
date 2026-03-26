"""Pydantic schemas for authentication endpoints.

Defines request and response schemas for registration and login.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration request.

    Attributes:
        email: User's email address (must be valid email format)
        password: User's password (minimum 8 characters)
        name: Optional display name
    """

    email: EmailStr = Field(
        ...,
        description="User's email address",
        json_schema_extra={"example": "user@example.com"},
    )
    password: str = Field(
        ...,
        min_length=8,
        description="User's password (minimum 8 characters)",
        json_schema_extra={"example": "SecureP@ssw0rd"},
    )
    name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User's display name",
        json_schema_extra={"example": "John Doe"},
    )


class UserLogin(BaseModel):
    """Schema for user login request.

    Attributes:
        email: User's email address
        password: User's password
    """

    email: EmailStr = Field(
        ...,
        description="User's email address",
        json_schema_extra={"example": "user@example.com"},
    )
    password: str = Field(
        ...,
        description="User's password",
        json_schema_extra={"example": "SecureP@ssw0rd"},
    )


class UserResponse(BaseModel):
    """Schema for user data in responses.

    Attributes:
        id: User's unique identifier
        email: User's email address
        name: User's display name (may be empty)
        created_at: When the user registered
    """

    id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    name: Optional[str] = Field(default=None, description="User's display name")
    created_at: datetime = Field(..., description="When the user registered")

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Schema for authentication responses (registration and login).

    Attributes:
        user: User data
        token: JWT token for authentication
    """

    user: UserResponse = Field(..., description="User data")
    token: str = Field(..., description="JWT token for authentication")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "name": "John Doe",
                    "created_at": "2026-01-07T10:00:00Z",
                },
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        }
    }
