"""
Shared pytest fixtures for Todo Application Phase I tests.

This module provides reusable fixtures for testing the in-memory
todo application across unit, integration, and contract tests.
"""

import pytest
from datetime import datetime
from typing import Generator

from src.state.store import TaskStore
from src.models.task import Task


@pytest.fixture
def empty_store() -> Generator[TaskStore, None, None]:
    """Provide a fresh, empty TaskStore for each test."""
    store = TaskStore()
    yield store


@pytest.fixture
def store_with_tasks(empty_store: TaskStore) -> TaskStore:
    """Provide a TaskStore pre-populated with sample tasks."""
    empty_store.add_task("Buy groceries", "Milk, eggs, bread")
    empty_store.add_task("Call dentist", "")
    empty_store.add_task("Finish report", "Due by Friday")
    return empty_store


@pytest.fixture
def sample_task() -> Task:
    """Provide a sample Task instance for testing."""
    return Task(
        id=1,
        title="Sample Task",
        description="A sample task for testing",
        completed=False,
        created_at=datetime.now()
    )


@pytest.fixture
def completed_task() -> Task:
    """Provide a completed Task instance for testing."""
    return Task(
        id=2,
        title="Completed Task",
        description="A completed task for testing",
        completed=True,
        created_at=datetime.now()
    )
