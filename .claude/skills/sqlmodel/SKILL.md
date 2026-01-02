---
name: sqlmodel
description: >
  SQLModel ORM for Python - combines SQLAlchemy and Pydantic for type-safe database
  operations. Use when building database models, CRUD operations, relationships,
  and FastAPI integrations with PostgreSQL, SQLite, or other SQL databases.
---

# SQLModel Skill

You are a **SQLModel specialist**.

Your job is to help users design and implement **database layers** using SQLModel, the Python ORM that combines SQLAlchemy's power with Pydantic's type safety.

## 1. When to Use This Skill

Use this Skill **whenever**:

- The user mentions:
  - "SQLModel"
  - "database models"
  - "ORM in Python"
  - "FastAPI database"
  - "Pydantic models for database"
- Or asks to:
  - Create database tables/models
  - Implement CRUD operations
  - Set up relationships between tables
  - Integrate database with FastAPI
  - Use async database operations

## 2. Model Definition Patterns

### 2.1 Basic Model with Table

```python
from typing import Optional
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)
```

### 2.2 Model with Indexes and Foreign Keys

```python
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Index for faster queries
    title: str = Field(index=True)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # Foreign key
    conversation_id: Optional[int] = Field(default=None, foreign_key="conversation.id")
```

### 2.3 Model Inheritance Pattern (Recommended)

```python
from typing import Optional
from sqlmodel import Field, SQLModel

# Base model (no table)
class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None

# Database model (with table)
class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    completed: bool = Field(default=False)

# API models (no table)
class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: int
    user_id: str
    completed: bool

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
```

## 3. Database Engine Setup

### 3.1 SQLite (Development)

```python
from sqlmodel import SQLModel, create_engine

sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

### 3.2 PostgreSQL (Production)

```python
from sqlmodel import create_engine

DATABASE_URL = "postgresql://user:password@host:5432/dbname"
engine = create_engine(DATABASE_URL, pool_recycle=300, pool_pre_ping=True)
```

### 3.3 Neon PostgreSQL (Serverless)

```python
import os
from sqlmodel import create_engine

DATABASE_URL = os.environ["DATABASE_URL"]  # From Neon dashboard
engine = create_engine(
    DATABASE_URL,
    pool_recycle=300,      # Recycle connections every 5 minutes
    pool_pre_ping=True,    # Verify connection before use
    pool_size=5,           # Connection pool size
    max_overflow=10,       # Additional connections when pool is full
)
```

## 4. CRUD Operations

### 4.1 Create

```python
from sqlmodel import Session

def create_task(task: TaskCreate, user_id: str) -> Task:
    with Session(engine) as session:
        db_task = Task.model_validate(task, update={"user_id": user_id})
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task
```

### 4.2 Read

```python
from sqlmodel import Session, select

# Get by ID
def get_task(task_id: int) -> Optional[Task]:
    with Session(engine) as session:
        return session.get(Task, task_id)

# Get all with filter
def get_tasks(user_id: str, status: str = "all") -> list[Task]:
    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id)
        if status == "pending":
            statement = statement.where(Task.completed == False)
        elif status == "completed":
            statement = statement.where(Task.completed == True)
        return session.exec(statement).all()

# With pagination
def get_tasks_paginated(
    user_id: str, skip: int = 0, limit: int = 10
) -> list[Task]:
    with Session(engine) as session:
        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return session.exec(statement).all()
```

### 4.3 Update

```python
def update_task(task_id: int, task_update: TaskUpdate) -> Optional[Task]:
    with Session(engine) as session:
        db_task = session.get(Task, task_id)
        if not db_task:
            return None
        task_data = task_update.model_dump(exclude_unset=True)
        db_task.sqlmodel_update(task_data)
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task
```

### 4.4 Delete

```python
def delete_task(task_id: int) -> bool:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            return False
        session.delete(task)
        session.commit()
        return True
```

## 5. Relationships

### 5.1 One-to-Many

```python
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship: One conversation has many messages
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship: Each message belongs to one conversation
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

### 5.2 Querying with Relationships

```python
def get_conversation_with_messages(conversation_id: int) -> Optional[Conversation]:
    with Session(engine) as session:
        conversation = session.get(Conversation, conversation_id)
        if conversation:
            # Access messages via relationship
            _ = conversation.messages  # Lazy load
        return conversation
```

## 6. FastAPI Integration

### 6.1 Session Dependency

```python
from typing import Annotated
from fastapi import Depends, FastAPI
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.post("/tasks/", response_model=TaskRead)
def create_task(task: TaskCreate, session: SessionDep):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@app.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

### 6.2 Lifespan for Table Creation

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)
```

## 7. Async Support

### 7.1 Async Engine Setup

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Note: Use asyncpg driver for PostgreSQL
DATABASE_URL = "postgresql+asyncpg://user:password@host:5432/dbname"

async_engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)
```

### 7.2 Async Table Creation

```python
async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### 7.3 Async Session Dependency

```python
from typing import AsyncGenerator

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
```

### 7.4 Async CRUD Operations

```python
@app.post("/tasks/", response_model=TaskRead)
async def create_task(task: TaskCreate, session: AsyncSessionDep):
    db_task = Task.model_validate(task)
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=list[TaskRead])
async def read_tasks(session: AsyncSessionDep):
    result = await session.exec(select(Task))
    return result.all()

@app.get("/tasks/{task_id}", response_model=TaskRead)
async def read_task(task_id: int, session: AsyncSessionDep):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

### 7.5 Async with Relationships (Eager Loading)

```python
from sqlalchemy.orm import selectinload

@app.get("/conversations/{conv_id}")
async def get_conversation(conv_id: int, session: AsyncSessionDep):
    statement = (
        select(Conversation)
        .where(Conversation.id == conv_id)
        .options(selectinload(Conversation.messages))
    )
    result = await session.exec(statement)
    conversation = result.first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation
```

## 8. Phase III Database Models

Complete models for the Todo AI Chatbot:

```python
from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

# Task model
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

# Conversation model
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    messages: List["Message"] = Relationship(back_populates="conversation")

# Message model
class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

## 9. Session Methods Reference

```python
# Add single object
session.add(obj)

# Add multiple objects
session.add_all([obj1, obj2, obj3])

# Execute select statement
result = session.exec(statement)

# Get results from executed statement
first_item = result.first()    # Single result or None
all_items = result.all()       # List of all results
one_item = result.one()        # Single result, raises if not exactly one

# Get by primary key
obj = session.get(Model, pk_value)

# Commit changes
session.commit()

# CRITICAL: Refresh object from database (gets auto-generated IDs)
session.refresh(obj)

# Rollback transaction
session.rollback()

# Delete object
session.delete(obj)
```

**Important:** Always call `session.refresh(obj)` after `session.commit()` when you need to access auto-generated fields like `id`.

## 10. Common Patterns

### 10.1 Soft Delete

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    deleted_at: Optional[datetime] = None  # Soft delete marker

def soft_delete_task(task_id: int) -> bool:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            return False
        task.deleted_at = datetime.utcnow()
        session.add(task)
        session.commit()
        return True

def get_active_tasks(user_id: str) -> list[Task]:
    with Session(engine) as session:
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.deleted_at == None
        )
        return session.exec(statement).all()
```

### 10.2 Timestamps Mixin

```python
class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class Task(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
```

### 10.3 User Ownership Pattern

```python
def get_user_task(user_id: str, task_id: int) -> Optional[Task]:
    """Get task only if it belongs to user."""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if task and task.user_id == user_id:
            return task
        return None
```

## 11. Debugging Tips

- **Model not creating table**: Ensure `table=True` is set
- **Foreign key errors**: Check that referenced table exists
- **Relationship not loading**: Use `selectinload` for async, or access attribute for sync
- **Type errors**: Use `Optional[int]` for nullable primary keys with `default=None`
- **Connection pool exhaustion**: Use `pool_recycle` and `pool_pre_ping` for serverless
