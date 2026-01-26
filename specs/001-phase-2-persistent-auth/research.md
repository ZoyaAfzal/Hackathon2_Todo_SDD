# Phase 0 Research: Phase II - Persistent Storage with Authentication

**Date**: 2026-01-07
**Branch**: `001-phase-2-persistent-auth`
**Spec**: [spec.md](./spec.md)

## Executive Summary

This research document captures technical decisions and implementation patterns for Phase II of the Evolution of Todo project. The research covers Better Auth JWT integration with FastAPI, SQLModel schema design, Neon PostgreSQL connection patterns, and OpenTelemetry observability.

---

## 1. Better Auth JWT Integration with FastAPI

### Architecture Decision

Better Auth runs on the Next.js frontend and issues JWT tokens. The FastAPI backend verifies these tokens using JWKS (JSON Web Key Set) published by Better Auth.

### Token Flow

1. User authenticates via Better Auth on Next.js frontend
2. Better Auth issues JWT token with user identity
3. Frontend includes token in `Authorization: Bearer <token>` header
4. FastAPI backend verifies token signature via JWKS endpoint
5. User identity extracted from JWT `sub` claim

### Better Auth Configuration (Frontend)

```typescript
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
    plugins: [
        jwt(),
    ]
})
```

### JWT Verification (Backend - FastAPI)

Two options for token verification:

**Option A: Remote JWKS (Recommended for Production)**
```python
from jose import jwtVerify, createRemoteJWKSet

async def validate_token(token: str):
    JWKS = createRemoteJWKSet(
        new URL('http://localhost:3000/api/auth/jwks')
    )
    payload = await jwtVerify(token, JWKS, {
        issuer: 'http://localhost:3000',
        audience: 'http://localhost:3000'
    })
    return payload
```

**Option B: Shared Secret (Simpler for Phase II)**
```python
from datetime import datetime, timedelta
import jwt

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Decision: Use Shared Secret

For Phase II, we use the shared secret approach (`BETTER_AUTH_SECRET`) as specified in FR-006. This is simpler and sufficient for the current phase. JWKS can be adopted in future phases for key rotation.

### FastAPI Dependency Pattern

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Extract and verify user_id from JWT token."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## 2. SQLModel Schema Design

### User Entity

```python
import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Task Entity

```python
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1)  # Optimistic locking
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
```

### Key Design Decisions

1. **UUID Primary Keys**: Use `uuid.UUID` with `default_factory=uuid.uuid4` for globally unique identifiers
2. **Timestamps**: Both `created_at` and `updated_at` for audit trail
3. **Version Field**: Integer for optimistic locking per FR-020b
4. **Foreign Key**: `user_id` references `user.id` for ownership
5. **Indexes**: On `user_id` for efficient filtering, on `email` for login lookups

---

## 3. Neon PostgreSQL Connection

### Connection String Format

```ini
# Standard connection
DATABASE_URL="postgresql://user:password@ep-name-123456.us-east-2.aws.neon.tech/dbname?sslmode=require"

# Pooled connection (recommended for serverless)
DATABASE_URL="postgresql://user:password@ep-name-123456-pooler.us-east-2.aws.neon.tech/dbname?sslmode=require"
```

### SQLAlchemy/SQLModel Configuration

```python
import os
from sqlmodel import create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL")

# Enable pool_pre_ping to handle Neon compute suspension
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def get_session():
    with Session(engine) as session:
        yield session
```

### Key Configuration

- **pool_pre_ping=True**: Validates connections before use, handles Neon compute suspension
- **sslmode=require**: Required for Neon connections
- **Pooler endpoint**: Use `-pooler` suffix for connection pooling in serverless environments

---

## 4. OpenTelemetry Instrumentation

### Installation

```bash
pip install opentelemetry-api opentelemetry-sdk
pip install opentelemetry-instrumentation-fastapi
pip install opentelemetry-instrumentation-sqlalchemy
pip install opentelemetry-exporter-otlp
```

### Programmatic Instrumentation

```python
from opentelemetry.instrumentation.auto_instrumentation import initialize
initialize()

from fastapi import FastAPI

app = FastAPI()
```

### Manual Instrumentation (Alternative)

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Configure tracing
trace.set_tracer_provider(TracerProvider())
tracer_provider = trace.get_tracer_provider()
tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter())
)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Instrument SQLAlchemy
SQLAlchemyInstrumentor().instrument(engine=engine)
```

### Custom Metrics

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider

meter = metrics.get_meter(__name__)

# Auth event counter
auth_events = meter.create_counter(
    "auth_events",
    description="Count of authentication events"
)

# Request latency histogram
request_latency = meter.create_histogram(
    "request_latency_ms",
    description="Request latency in milliseconds"
)
```

---

## 5. Cursor-Based Pagination

### Implementation Pattern

```python
from typing import Optional, List
from uuid import UUID

async def get_tasks(
    user_id: UUID,
    after_id: Optional[UUID] = None,
    limit: int = 20
) -> List[Task]:
    query = select(Task).where(Task.user_id == user_id)

    if after_id:
        # Get the created_at of the cursor task
        cursor_task = session.get(Task, after_id)
        if cursor_task:
            query = query.where(
                (Task.created_at < cursor_task.created_at) |
                ((Task.created_at == cursor_task.created_at) & (Task.id > after_id))
            )

    query = query.order_by(Task.created_at.desc(), Task.id).limit(limit + 1)

    results = session.exec(query).all()
    has_more = len(results) > limit

    return {
        "tasks": results[:limit],
        "has_more": has_more,
        "next_cursor": results[limit - 1].id if has_more else None
    }
```

### API Response Format

```json
{
  "tasks": [...],
  "has_more": true,
  "next_cursor": "uuid-of-last-task"
}
```

---

## 6. Optimistic Locking

### Implementation Pattern

```python
from fastapi import HTTPException

async def update_task(
    task_id: UUID,
    user_id: UUID,
    update: TaskUpdate,
    expected_version: int
) -> Task:
    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.version != expected_version:
        raise HTTPException(
            status_code=409,
            detail="Conflict: Task was modified by another request"
        )

    # Apply updates
    for key, value in update.dict(exclude_unset=True).items():
        setattr(task, key, value)

    task.version += 1
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

### Client Handling

Clients must:
1. Include `version` field when updating tasks
2. Handle 409 Conflict by refetching and retrying

---

## 7. Security Considerations

### Password Hashing

Better Auth handles password hashing internally using secure algorithms (bcrypt/argon2).

### JWT Token Security

- 24-hour expiration (FR-006a)
- Shared secret stored in environment variable
- No refresh tokens in Phase II

### User Isolation

- All task queries filter by `user_id` from JWT
- Return 404 (not 403) for non-owned resources to prevent enumeration
- URL-provided user_id parameters are ignored (FR-022)

---

## 8. Dependencies Summary

### Backend (Python)

```txt
fastapi>=0.109.0
sqlmodel>=0.0.14
pyjwt>=2.8.0
python-dotenv>=1.0.0
psycopg2-binary>=2.9.9
opentelemetry-api>=1.22.0
opentelemetry-sdk>=1.22.0
opentelemetry-instrumentation-fastapi>=0.43b0
opentelemetry-instrumentation-sqlalchemy>=0.43b0
opentelemetry-exporter-otlp>=1.22.0
uvicorn>=0.27.0
pytest>=8.0.0
httpx>=0.26.0
```

### Frontend (TypeScript)

```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.0.0",
    "better-auth": "^1.0.0",
    "@better-auth/client": "^1.0.0"
  }
}
```

---

## 9. Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Hard delete vs soft delete? | Hard delete (FR-020a) |
| User ID from JWT or URL? | JWT only (FR-022) |
| Include updated_at? | Yes, auto-set on modification |
| JWT expiration strategy? | 24-hour, no refresh token |
| Pagination approach? | Cursor-based with after_id |
| Conflict resolution? | Optimistic locking with version field |
| Observability? | OpenTelemetry for traces + custom metrics |

---

## 10. Next Steps

1. Generate data-model.md with complete entity schemas
2. Create API contracts for all endpoints
3. Create authentication flow contract
4. Generate quickstart guide for development setup
