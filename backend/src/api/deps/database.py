"""Database session dependency for FastAPI."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from src.core.database import engine


def get_session() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    This creates a new SQLModel Session for each request and ensures
    it is properly closed after the request completes.

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        yield session


# Type alias for dependency injection
SessionDep = Annotated[Session, Depends(get_session)]
