# Authentication Contract: Phase II - Better Auth JWT Integration

**Date**: 2026-01-07
**Branch**: `001-phase-2-persistent-auth`
**Spec**: [../spec.md](../spec.md)
**Research**: [../research.md](../research.md)

---

## Overview

This contract defines the authentication flow between the Next.js frontend (Better Auth) and the FastAPI backend (JWT verification). Better Auth handles user management, password hashing, and JWT issuance. The FastAPI backend verifies JWT tokens using a shared secret.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client (Browser)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 1. Login/Register
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Next.js Frontend                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                     Better Auth                          │    │
│  │  - User registration                                     │    │
│  │  - Password hashing                                      │    │
│  │  - Session management                                    │    │
│  │  - JWT token issuance                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 2. API Request + JWT
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  JWT Verification                        │    │
│  │  - Validate signature (BETTER_AUTH_SECRET)              │    │
│  │  - Check expiration                                      │    │
│  │  - Extract user_id from 'sub' claim                     │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 3. Database Query (filtered by user_id)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Neon PostgreSQL                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Authentication Endpoints (Frontend - Better Auth)

### 1. User Registration

**Endpoint**: `POST /api/auth/sign-up/email`

**Description**: Create a new user account with email and password.

**Request**:
```http
POST /api/auth/sign-up/email HTTP/1.1
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd",
  "name": "John Doe"
}
```

**Request Body**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `email` | string | Yes | Valid email format | User's email address |
| `password` | string | Yes | Min 8 chars | User's password |
| `name` | string | No | - | User's display name |

**Response**: `200 OK`
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": false,
    "createdAt": "2026-01-07T10:00:00Z",
    "updatedAt": "2026-01-07T10:00:00Z"
  },
  "session": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresAt": "2026-01-08T10:00:00Z"
  }
}
```

**Errors**:
| Status | Code | Description |
|--------|------|-------------|
| 400 | `invalid_email` | Invalid email format |
| 400 | `weak_password` | Password doesn't meet requirements |
| 409 | `email_exists` | Email already registered |

---

### 2. User Login

**Endpoint**: `POST /api/auth/sign-in/email`

**Description**: Authenticate an existing user and receive a JWT token.

**Request**:
```http
POST /api/auth/sign-in/email HTTP/1.1
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd"
}
```

**Request Body**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | User's email address |
| `password` | string | Yes | User's password |

**Response**: `200 OK`
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": false,
    "createdAt": "2026-01-07T10:00:00Z",
    "updatedAt": "2026-01-07T10:00:00Z"
  },
  "session": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresAt": "2026-01-08T10:00:00Z"
  }
}
```

**Errors**:
| Status | Code | Description |
|--------|------|-------------|
| 401 | `invalid_credentials` | Email or password incorrect |
| 400 | `missing_fields` | Email or password not provided |

---

### 3. User Logout

**Endpoint**: `POST /api/auth/sign-out`

**Description**: Terminate the user's session.

**Request**:
```http
POST /api/auth/sign-out HTTP/1.1
Authorization: Bearer <token>
```

**Response**: `200 OK`
```json
{
  "success": true
}
```

---

### 4. Get Current Session

**Endpoint**: `GET /api/auth/session`

**Description**: Get the current user's session information.

**Request**:
```http
GET /api/auth/session HTTP/1.1
Authorization: Bearer <token>
```

**Response**: `200 OK`
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "session": {
    "expiresAt": "2026-01-08T10:00:00Z"
  }
}
```

**Errors**:
| Status | Code | Description |
|--------|------|-------------|
| 401 | `unauthorized` | No valid session |

---

## JWT Token Structure

### Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload
```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "iat": 1704621600,
  "exp": 1704708000
}
```

| Claim | Type | Description |
|-------|------|-------------|
| `sub` | string (UUID) | User ID (subject) - used for task ownership |
| `email` | string | User's email address |
| `iat` | integer | Issued at timestamp (Unix) |
| `exp` | integer | Expiration timestamp (Unix) - 24 hours from iat |

### Signature

The JWT is signed using HMAC-SHA256 with the `BETTER_AUTH_SECRET` environment variable.

---

## Backend JWT Verification

### Environment Variables

```env
BETTER_AUTH_SECRET=your-256-bit-secret-key-here
```

### FastAPI Dependency

```python
import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID

security = HTTPBearer()

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"


class TokenPayload:
    def __init__(self, user_id: UUID, email: str):
        self.user_id = user_id
        self.email = email


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenPayload:
    """
    Verify JWT token and extract user information.

    Returns:
        TokenPayload with user_id and email

    Raises:
        HTTPException 401 if token is invalid or expired
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")
        email = payload.get("email")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return TokenPayload(
            user_id=UUID(user_id),
            email=email
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
```

### Protected Route Example

```python
from fastapi import APIRouter, Depends
from uuid import UUID

router = APIRouter()

@router.get("/api/v1/tasks")
async def list_tasks(
    current_user: TokenPayload = Depends(get_current_user)
):
    # current_user.user_id contains the authenticated user's UUID
    # Use this to filter tasks
    tasks = await task_service.get_tasks_by_user(current_user.user_id)
    return {"tasks": tasks}
```

---

## Security Rules

### Token Handling

1. **Token Transmission**: Always via `Authorization: Bearer <token>` header
2. **Token Storage**: Frontend stores in httpOnly cookie or secure storage
3. **Token Expiration**: 24 hours from issuance (FR-006a)
4. **No Refresh Tokens**: User must re-authenticate after expiration

### User ID Extraction

1. **Source**: Exclusively from JWT `sub` claim (FR-022)
2. **URL Parameters**: Any `user_id` in URL paths is ignored
3. **Request Body**: Any `user_id` in request body is ignored

### Password Security

1. Better Auth handles all password hashing
2. Passwords are never transmitted in plaintext over network (HTTPS required)
3. Passwords are never logged or stored in plaintext

---

## Error Responses

### 401 Unauthorized

Returned when:
- No Authorization header provided
- Invalid token format
- Token signature verification fails
- Token has expired

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Token has expired",
    "details": {}
  }
}
```

### Response Headers

All 401 responses include:
```
WWW-Authenticate: Bearer
```

---

## Frontend Integration

### Better Auth Client Setup

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/client"

export const authClient = createAuthClient({
    baseURL: process.env.NEXT_PUBLIC_APP_URL
})
```

### Making Authenticated API Requests

```typescript
// lib/api-client.ts
import { authClient } from "./auth-client"

export async function apiRequest(
    endpoint: string,
    options: RequestInit = {}
) {
    const session = await authClient.getSession()

    if (!session?.token) {
        throw new Error("Not authenticated")
    }

    const response = await fetch(`/api/v1${endpoint}`, {
        ...options,
        headers: {
            ...options.headers,
            "Authorization": `Bearer ${session.token}`,
            "Content-Type": "application/json"
        }
    })

    if (response.status === 401) {
        // Token expired, redirect to login
        window.location.href = "/login"
        throw new Error("Session expired")
    }

    return response
}
```

---

## Testing Authentication

### Test User Creation

```python
# tests/conftest.py
import pytest
import jwt
from datetime import datetime, timedelta
from uuid import uuid4

@pytest.fixture
def test_user_id():
    return uuid4()

@pytest.fixture
def valid_token(test_user_id):
    payload = {
        "sub": str(test_user_id),
        "email": "test@example.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")

@pytest.fixture
def expired_token(test_user_id):
    payload = {
        "sub": str(test_user_id),
        "email": "test@example.com",
        "iat": datetime.utcnow() - timedelta(hours=48),
        "exp": datetime.utcnow() - timedelta(hours=24)
    }
    return jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")
```

### Test Cases

```python
# tests/contract/test_auth.py

def test_valid_token_grants_access(client, valid_token):
    response = client.get(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200

def test_expired_token_returns_401(client, expired_token):
    response = client.get(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"

def test_missing_token_returns_401(client):
    response = client.get("/api/v1/tasks")
    assert response.status_code == 401

def test_invalid_token_returns_401(client):
    response = client.get(
        "/api/v1/tasks",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401
```
