---
name: better-auth-python
description: Better Auth JWT verification for Python/FastAPI backends. Use when integrating Python APIs with a Better Auth TypeScript server via JWT tokens. Covers JWKS verification, FastAPI dependencies, SQLModel/SQLAlchemy integration, and protected routes.
---

# Better Auth Python Integration Skill

Integrate Python/FastAPI backends with Better Auth (TypeScript) authentication server using JWT verification.

## Important: Verified Better Auth JWT Behavior

**JWKS Endpoint:** `/api/auth/jwks` (NOT `/.well-known/jwks.json`)
**Default Algorithm:** EdDSA (Ed25519) (NOT RS256)
**Key Type:** OKP (Octet Key Pair) for EdDSA keys

These values were verified against actual Better Auth server responses and may differ from other documentation.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js App   │────▶│  Better Auth    │────▶│   PostgreSQL    │
│   (Frontend)    │     │  (Auth Server)  │     │   (Database)    │
└────────┬────────┘     └────────┬────────┘     └─────────────────┘
         │                       │
         │ JWT Token             │ JWKS: /api/auth/jwks
         ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│              (Verifies JWT with EdDSA/JWKS)                      │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
# pip
pip install fastapi uvicorn pyjwt cryptography httpx

# poetry
poetry add fastapi uvicorn pyjwt cryptography httpx

# uv
uv add fastapi uvicorn pyjwt cryptography httpx
```

### Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
BETTER_AUTH_URL=http://localhost:3000
```

## ORM Integration (Choose One)

| ORM | Guide |
|-----|-------|
| **SQLModel** | [reference/sqlmodel.md](reference/sqlmodel.md) |
| **SQLAlchemy** | [reference/sqlalchemy.md](reference/sqlalchemy.md) |

## Basic JWT Verification

```python
# app/auth.py
import os
import time
import httpx
import jwt
from dataclasses import dataclass
from typing import Optional
from fastapi import HTTPException, Header, status

BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")
JWKS_CACHE_TTL = 300  # 5 minutes

@dataclass
class User:
    id: str
    email: str
    name: Optional[str] = None
    image: Optional[str] = None

@dataclass
class _JWKSCache:
    keys: dict
    expires_at: float

_cache: Optional[_JWKSCache] = None

async def _get_jwks() -> dict:
    """Fetch JWKS from Better Auth with TTL caching."""
    global _cache
    now = time.time()

    if _cache and now < _cache.expires_at:
        return _cache.keys

    # Better Auth JWKS endpoint (NOT /.well-known/jwks.json)
    jwks_endpoint = f"{BETTER_AUTH_URL}/api/auth/jwks"

    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_endpoint, timeout=10.0)
        response.raise_for_status()
        jwks = response.json()

    # Build key lookup supporting multiple algorithms
    keys = {}
    for key in jwks.get("keys", []):
        kid = key.get("kid")
        kty = key.get("kty")
        if not kid:
            continue

        try:
            if kty == "RSA":
                keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            elif kty == "EC":
                keys[kid] = jwt.algorithms.ECAlgorithm.from_jwk(key)
            elif kty == "OKP":
                # EdDSA keys (Ed25519) - Better Auth default
                keys[kid] = jwt.algorithms.OKPAlgorithm.from_jwk(key)
        except Exception:
            continue

    _cache = _JWKSCache(keys=keys, expires_at=now + JWKS_CACHE_TTL)
    return keys

def clear_jwks_cache() -> None:
    """Clear cache for key rotation scenarios."""
    global _cache
    _cache = None

async def verify_token(token: str) -> User:
    """Verify JWT and extract user data."""
    if token.startswith("Bearer "):
        token = token[7:]

    if not token:
        raise HTTPException(status_code=401, detail="Token required")

    public_keys = await _get_jwks()

    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")
    alg = unverified_header.get("alg", "EdDSA")

    if not kid or kid not in public_keys:
        # Retry once for key rotation
        clear_jwks_cache()
        public_keys = await _get_jwks()
        if not kid or kid not in public_keys:
            raise HTTPException(status_code=401, detail="Invalid token key")

    # Support EdDSA (default), RS256, ES256
    payload = jwt.decode(
        token,
        public_keys[kid],
        algorithms=[alg, "EdDSA", "RS256", "ES256"],
        options={"verify_aud": False},
    )

    user_id = payload.get("sub") or payload.get("userId") or payload.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing user ID")

    return User(
        id=str(user_id),
        email=payload.get("email", ""),
        name=payload.get("name"),
        image=payload.get("image"),
    )

async def get_current_user(
    authorization: str = Header(default=None, alias="Authorization")
) -> User:
    """FastAPI dependency for authenticated routes."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    return await verify_token(authorization)
```

### Protected Route

```python
from fastapi import Depends
from app.auth import User, get_current_user

@app.get("/api/me")
async def get_me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "name": user.name}
```

## Examples

| Pattern | Guide |
|---------|-------|
| **Protected Routes** | [examples/protected-routes.md](examples/protected-routes.md) |
| **JWT Verification** | [examples/jwt-verification.md](examples/jwt-verification.md) |

## Templates

| Template | Purpose |
|----------|---------|
| [templates/auth.py](templates/auth.py) | JWT verification module |
| [templates/main.py](templates/main.py) | FastAPI app template |
| [templates/database_sqlmodel.py](templates/database_sqlmodel.py) | SQLModel database setup |
| [templates/models_sqlmodel.py](templates/models_sqlmodel.py) | SQLModel models |

## Quick SQLModel Example

```python
from sqlmodel import SQLModel, Field, Session, select
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    completed: bool = Field(default=False)
    user_id: str = Field(index=True)  # From JWT 'sub' claim

@app.get("/api/tasks")
async def get_tasks(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    statement = select(Task).where(Task.user_id == user.id)
    return session.exec(statement).all()
```

## Frontend Integration

### Getting JWT from Better Auth

```typescript
import { authClient } from "./auth-client";

const { data } = await authClient.token();
const jwtToken = data?.token;
```

### Sending to FastAPI

```typescript
async function fetchAPI(endpoint: string) {
  const { data } = await authClient.token();

  return fetch(`${API_URL}${endpoint}`, {
    headers: {
      Authorization: `Bearer ${data?.token}`,
      "Content-Type": "application/json",
    },
  });
}
```

## Security Considerations

1. **Always use HTTPS** in production
2. **Validate issuer and audience** to prevent token substitution
3. **Handle token expiration** gracefully
4. **Refresh JWKS** when encountering unknown key IDs
5. **Don't log tokens** - they contain sensitive data

## Troubleshooting

### JWKS fetch fails
- Ensure Better Auth server is running
- Check JWKS endpoint `/api/auth/jwks` is accessible (NOT `/.well-known/jwks.json`)
- Verify network connectivity between backend and frontend

### Token validation fails
- Verify token hasn't expired
- Check algorithm compatibility - Better Auth uses **EdDSA** by default, not RS256
- Ensure you're using `OKPAlgorithm.from_jwk()` for EdDSA keys
- Check key ID (kid) matches between token header and JWKS

### CORS errors
- Configure CORS middleware properly
- Allow credentials if using cookies
- Check origin is in allowed list

## Verified Better Auth Response Format

JWKS response from `/api/auth/jwks`:
```json
{
  "keys": [
    {
      "kty": "OKP",
      "crv": "Ed25519",
      "x": "...",
      "kid": "..."
    }
  ]
}
```

Note: `kty: "OKP"` indicates EdDSA keys, not RSA.
