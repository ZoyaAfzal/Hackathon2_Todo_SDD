"""
SQLModel Database Configuration Template

This template provides database engine setup for various environments.
Copy and customize for your project.
"""

import os
from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager

# ============================================================================
# Environment-based Configuration
# ============================================================================

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./database.db"  # Default to SQLite for development
)

# Determine if using SQLite or PostgreSQL
is_sqlite = DATABASE_URL.startswith("sqlite")

# ============================================================================
# Engine Configuration
# ============================================================================

if is_sqlite:
    # SQLite configuration (development)
    engine = create_engine(
        DATABASE_URL,
        echo=True,  # Set to False in production
        connect_args={"check_same_thread": False}  # Required for SQLite
    )
else:
    # PostgreSQL configuration (production / Neon)
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_recycle=300,      # Recycle connections every 5 minutes
        pool_pre_ping=True,    # Verify connection before use
        pool_size=5,           # Connection pool size
        max_overflow=10,       # Additional connections when pool is full
    )


# ============================================================================
# Database Initialization
# ============================================================================

def create_db_and_tables():
    """Create all tables defined in SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def drop_db_and_tables():
    """Drop all tables (use with caution!)."""
    SQLModel.metadata.drop_all(engine)


# ============================================================================
# Session Management
# ============================================================================

@contextmanager
def get_session():
    """Context manager for database sessions.

    Usage:
        with get_session() as session:
            session.add(obj)
            session.commit()
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def get_session_dependency():
    """FastAPI dependency for database sessions.

    Usage:
        from fastapi import Depends
        from typing import Annotated

        SessionDep = Annotated[Session, Depends(get_session_dependency)]

        @app.get("/items/")
        def get_items(session: SessionDep):
            ...
    """
    with Session(engine) as session:
        yield session


# ============================================================================
# Async Configuration (Optional)
# ============================================================================

# Uncomment for async support with PostgreSQL

# from sqlmodel.ext.asyncio.session import AsyncSession
# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# # Convert postgres:// to postgresql+asyncpg://
# ASYNC_DATABASE_URL = DATABASE_URL.replace(
#     "postgresql://", "postgresql+asyncpg://"
# ).replace(
#     "postgres://", "postgresql+asyncpg://"
# )

# async_engine = create_async_engine(
#     ASYNC_DATABASE_URL,
#     echo=False,
#     pool_recycle=300,
#     pool_pre_ping=True,
# )

# async_session_maker = async_sessionmaker(
#     async_engine,
#     class_=AsyncSession,
#     expire_on_commit=False
# )

# async def create_db_and_tables_async():
#     """Create tables asynchronously."""
#     async with async_engine.begin() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)

# async def get_async_session():
#     """FastAPI dependency for async sessions."""
#     async with async_session_maker() as session:
#         yield session
