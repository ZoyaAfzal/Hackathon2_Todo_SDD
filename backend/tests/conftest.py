"""Pytest configuration and fixtures for Todo API tests."""

import uuid
from datetime import datetime, timedelta
from typing import Generator
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.api.deps.database import get_session
from src.core.config import settings
from src.main import app
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.task import Task
from src.models.user import User


@pytest.fixture(name="engine")
def engine_fixture():
    """Create an in-memory SQLite engine for testing."""
    # Import all models to register them with SQLModel.metadata
    # These imports are needed even though they appear unused
    _ = (Conversation, Message, Task, User)

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(engine, session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override."""

    def get_session_override() -> Generator[Session, None, None]:
        yield session

    # Override the get_session dependency
    app.dependency_overrides[get_session] = get_session_override

    # Also need to replace the database module's engine with test engine
    import src.core.database as db_module
    original_engine = db_module.engine
    db_module.engine = engine

    try:
        with TestClient(app) as client:
            yield client
    finally:
        # Restore original engine
        db_module.engine = original_engine
        app.dependency_overrides.clear()


@pytest.fixture
def test_user_id() -> uuid.UUID:
    """Generate a test user ID."""
    return uuid.uuid4()


@pytest.fixture
def test_user(session: Session) -> User:
    """Create a test user in the database."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash="hashed_password_placeholder",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def another_user(session: Session) -> User:
    """Create another test user for isolation tests."""
    user = User(
        id=uuid.uuid4(),
        email="another@example.com",
        password_hash="hashed_password_placeholder",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def test_task(session: Session, test_user: User) -> Task:
    """Create a test task in the database."""
    task = Task(
        id=uuid.uuid4(),
        title="Test Task",
        description="A test task description",
        completed=False,
        user_id=test_user.id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.fixture
def completed_task(session: Session, test_user: User) -> Task:
    """Create a completed test task."""
    task = Task(
        id=uuid.uuid4(),
        title="Completed Task",
        description="A completed task",
        completed=True,
        user_id=test_user.id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.fixture
def multiple_tasks(session: Session, test_user: User) -> list[Task]:
    """Create multiple test tasks for pagination testing."""
    tasks = []
    for i in range(15):
        task = Task(
            id=uuid.uuid4(),
            title=f"Task {i + 1}",
            description=f"Description for task {i + 1}",
            completed=i % 3 == 0,  # Every third task is completed
            user_id=test_user.id,
        )
        session.add(task)
        tasks.append(task)
    session.commit()
    for task in tasks:
        session.refresh(task)
    return tasks


@pytest.fixture
def valid_token(test_user: User) -> str:
    """Generate a valid JWT token for the test user."""
    payload = {
        "sub": str(test_user.id),
        "email": test_user.email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def expired_token(test_user: User) -> str:
    """Generate an expired JWT token."""
    payload = {
        "sub": str(test_user.id),
        "email": test_user.email,
        "iat": datetime.utcnow() - timedelta(hours=48),
        "exp": datetime.utcnow() - timedelta(hours=24),
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def invalid_token() -> str:
    """Generate an invalid JWT token (wrong secret)."""
    payload = {
        "sub": str(uuid.uuid4()),
        "email": "fake@example.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, "wrong-secret-key", algorithm="HS256")


@pytest.fixture
def auth_headers(valid_token: str) -> dict[str, str]:
    """Create authorization headers with valid token."""
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture
def another_user_token(another_user: User) -> str:
    """Generate a valid JWT token for another user."""
    payload = {
        "sub": str(another_user.id),
        "email": another_user.email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def another_user_headers(another_user_token: str) -> dict[str, str]:
    """Create authorization headers for another user."""
    return {"Authorization": f"Bearer {another_user_token}"}


# Task creation payloads
@pytest.fixture
def valid_task_payload() -> dict:
    """Valid task creation payload."""
    return {
        "title": "New Task",
        "description": "A new task description",
    }


@pytest.fixture
def minimal_task_payload() -> dict:
    """Minimal valid task payload (title only)."""
    return {"title": "Minimal Task"}


@pytest.fixture
def invalid_task_payload_empty_title() -> dict:
    """Invalid task payload with empty title."""
    return {"title": ""}


@pytest.fixture
def invalid_task_payload_long_title() -> dict:
    """Invalid task payload with title exceeding 255 chars."""
    return {"title": "x" * 256}


# Task update payloads
@pytest.fixture
def valid_update_payload() -> dict:
    """Valid task update payload."""
    return {
        "title": "Updated Task",
        "description": "Updated description",
        "completed": True,
    }


@pytest.fixture
def partial_update_payload() -> dict:
    """Partial task update payload (title only)."""
    return {"title": "Partially Updated"}


@pytest.fixture
def completion_update_payload() -> dict:
    """Task completion update payload."""
    return {"completed": True}
