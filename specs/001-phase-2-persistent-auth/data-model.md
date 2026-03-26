# Data Model: Phase II - Persistent Storage with Authentication

**Date**: 2026-01-07
**Branch**: `001-phase-2-persistent-auth`
**Spec**: [spec.md](./spec.md)
**Research**: [research.md](./research.md)

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────┐
│                 User                     │
├─────────────────────────────────────────┤
│ id: UUID (PK)                           │
│ email: VARCHAR(255) UNIQUE NOT NULL     │
│ password_hash: VARCHAR(255) NOT NULL    │
│ created_at: TIMESTAMP NOT NULL          │
└─────────────────────────────────────────┘
                    │
                    │ 1:N
                    ▼
┌─────────────────────────────────────────┐
│                 Task                     │
├─────────────────────────────────────────┤
│ id: UUID (PK)                           │
│ title: VARCHAR(255) NOT NULL            │
│ description: TEXT NULL                  │
│ completed: BOOLEAN NOT NULL DEFAULT false│
│ created_at: TIMESTAMP NOT NULL          │
│ updated_at: TIMESTAMP NOT NULL          │
│ version: INTEGER NOT NULL DEFAULT 1     │
│ user_id: UUID (FK → User.id) NOT NULL   │
└─────────────────────────────────────────┘
```

---

## Entity: User

### Description

Represents an authenticated user of the system. Users can own zero or more tasks. User identity is established via Better Auth and verified via JWT tokens.

### Schema

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for the user |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User's email address for authentication |
| `password_hash` | VARCHAR(255) | NOT NULL | Securely hashed password (handled by Better Auth) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the user registered |

### SQLModel Definition

```python
import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task

class User(SQLModel, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the user"
    )
    email: str = Field(
        max_length=255,
        unique=True,
        index=True,
        description="User's email address for authentication"
    )
    password_hash: str = Field(
        max_length=255,
        description="Securely hashed password"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the user registered"
    )

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="owner")
```

### Indexes

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| `ix_user_email` | `email` | UNIQUE | Fast lookup for login |

### Business Rules

1. Email must be unique across all users
2. Password is never stored in plaintext - only the hash
3. Users can only be created through the registration endpoint
4. User deletion is not supported in Phase II

---

## Entity: Task

### Description

Represents a todo task owned by a user. Tasks persist across sessions and are isolated per user. Each task has a version field for optimistic locking.

### Schema

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for the task |
| `title` | VARCHAR(255) | NOT NULL | Task title (required) |
| `description` | TEXT | NULL | Optional task description |
| `completed` | BOOLEAN | NOT NULL, DEFAULT false | Completion status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the task was created |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the task was last modified |
| `version` | INTEGER | NOT NULL, DEFAULT 1 | Version for optimistic locking |
| `user_id` | UUID | FOREIGN KEY → user.id, NOT NULL, INDEX | Owner of the task |

### SQLModel Definition

```python
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .user import User

class Task(SQLModel, table=True):
    __tablename__ = "task"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the task"
    )
    title: str = Field(
        max_length=255,
        description="Task title (required)"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional task description"
    )
    completed: bool = Field(
        default=False,
        description="Completion status"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the task was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the task was last modified"
    )
    version: int = Field(
        default=1,
        description="Version for optimistic locking"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        index=True,
        description="Owner of the task"
    )

    # Relationship
    owner: Optional["User"] = Relationship(back_populates="tasks")
```

### Indexes

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| `ix_task_user_id` | `user_id` | BTREE | Fast filtering by owner |
| `ix_task_created_at` | `created_at` | BTREE | Ordering for pagination |

### Business Rules

1. Title is required and cannot be empty
2. Title has a maximum length of 255 characters
3. Description is optional
4. Completed defaults to false
5. Version starts at 1 and increments on every update
6. updated_at is automatically set on every modification
7. user_id must reference a valid user
8. Tasks are hard deleted (no soft delete)

---

## Pydantic Schemas (API Request/Response)

### Task Create Request

```python
from pydantic import BaseModel, Field
from typing import Optional

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }
```

### Task Update Request

```python
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    completed: Optional[bool] = Field(default=None)
    version: int = Field(..., description="Expected version for optimistic locking")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries and supplies",
                "version": 1
            }
        }
```

### Task Response

```python
import uuid
from datetime import datetime

class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-01-07T10:00:00Z",
                "updated_at": "2026-01-07T10:00:00Z",
                "version": 1
            }
        }
```

### Task List Response

```python
from typing import List, Optional

class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    has_more: bool
    next_cursor: Optional[uuid.UUID] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [...],
                "has_more": True,
                "next_cursor": "123e4567-e89b-12d3-a456-426614174001"
            }
        }
```

---

## Database Migrations

### Initial Migration (Alembic)

```python
"""Initial schema for Phase II

Revision ID: 001_initial
Create Date: 2026-01-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_user_email', 'user', ['email'], unique=True)

    # Create task table
    op.create_table(
        'task',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('user.id'), nullable=False),
    )
    op.create_index('ix_task_user_id', 'task', ['user_id'])
    op.create_index('ix_task_created_at', 'task', ['created_at'])

def downgrade():
    op.drop_table('task')
    op.drop_table('user')
```

---

## Validation Rules

### Task Title

- Required: Yes
- Min length: 1 character
- Max length: 255 characters
- Validation error: "Title is required and must be 1-255 characters"

### Task Description

- Required: No
- Max length: No limit (TEXT field)

### Version (Optimistic Locking)

- Required on update: Yes
- Must match current version in database
- Conflict error (409): "Task was modified by another request"

---

## State Transitions

### Task Lifecycle

```
                    ┌──────────┐
                    │  Create  │
                    └────┬─────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │                                │
        ▼                                │
┌───────────────┐                        │
│  Incomplete   │◄───────────────────────┤
│ (completed=   │                        │
│   false)      │                        │
└───────┬───────┘                        │
        │                                │
        │ complete()                     │ uncomplete()
        │                                │
        ▼                                │
┌───────────────┐                        │
│   Complete    │────────────────────────┘
│ (completed=   │
│   true)       │
└───────┬───────┘
        │
        │ delete()
        ▼
┌───────────────┐
│   Deleted     │
│  (removed)    │
└───────────────┘
```

### Version Increment

- Version is incremented on every update operation
- Version starts at 1 when task is created
- Version must be provided in update requests for optimistic locking
