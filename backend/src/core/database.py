"""Database connection module for Neon PostgreSQL."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

from .config import settings

# Create engine with pool_pre_ping to handle Neon compute suspension
# pool_pre_ping validates connections before use
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Yields:
        Session: SQLModel database session

    Note:
        Session is automatically closed after request completes.
    """
    with Session(engine) as session:
        yield session


# Type alias for dependency injection
SessionDep = Annotated[Session, Depends(get_session)]
