"""
Unit tests for Task dataclass model.

Tests Task creation, validation, and invariants per data-model.md specification.
"""

import pytest
from datetime import datetime
from src.models.task import Task
from src.exceptions import EmptyTitleError


class TestTaskCreation:
    """Tests for Task creation and initialization."""

    def test_create_task_with_title_only(self) -> None:
        """Task can be created with just a title."""
        task = Task(id=1, title="Buy groceries")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.completed is False
        assert isinstance(task.created_at, datetime)

    def test_create_task_with_title_and_description(self) -> None:
        """Task can be created with title and description."""
        task = Task(id=1, title="Buy groceries", description="Milk, eggs, bread")

        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"

    def test_create_task_with_all_attributes(self) -> None:
        """Task can be created with all explicit attributes."""
        created = datetime(2026, 1, 2, 10, 30, 0)
        task = Task(
            id=5,
            title="Complete report",
            description="Annual review",
            completed=True,
            created_at=created
        )

        assert task.id == 5
        assert task.title == "Complete report"
        assert task.description == "Annual review"
        assert task.completed is True
        assert task.created_at == created


class TestTaskTitleValidation:
    """Tests for Task title validation per VR-001, VR-002."""

    def test_empty_title_raises_error(self) -> None:
        """Creating task with empty title raises EmptyTitleError."""
        with pytest.raises(EmptyTitleError):
            Task(id=1, title="")

    def test_whitespace_only_title_raises_error(self) -> None:
        """Creating task with whitespace-only title raises EmptyTitleError."""
        with pytest.raises(EmptyTitleError):
            Task(id=1, title="   ")

    def test_title_is_stripped(self) -> None:
        """Title whitespace is trimmed on creation."""
        task = Task(id=1, title="  Buy groceries  ")
        assert task.title == "Buy groceries"

    def test_description_is_stripped(self) -> None:
        """Description whitespace is trimmed on creation."""
        task = Task(id=1, title="Task", description="  Some details  ")
        assert task.description == "Some details"


class TestTaskInvariants:
    """Tests for Task invariants per data-model.md."""

    def test_id_must_be_positive(self) -> None:
        """Task ID must be a positive integer."""
        # Valid positive IDs
        task1 = Task(id=1, title="Task 1")
        task2 = Task(id=100, title="Task 100")

        assert task1.id == 1
        assert task2.id == 100

    def test_completed_is_boolean(self) -> None:
        """Completed must be exactly True or False."""
        task_incomplete = Task(id=1, title="Task", completed=False)
        task_complete = Task(id=2, title="Task", completed=True)

        assert task_incomplete.completed is False
        assert task_complete.completed is True

    def test_created_at_is_datetime(self) -> None:
        """Created_at must be a valid datetime object."""
        task = Task(id=1, title="Task")
        assert isinstance(task.created_at, datetime)

    def test_description_defaults_to_empty_string(self) -> None:
        """Description defaults to empty string, never None."""
        task = Task(id=1, title="Task")
        assert task.description == ""
        assert task.description is not None


class TestTaskMutability:
    """Tests for Task attribute mutability per data-model.md."""

    def test_title_is_mutable(self) -> None:
        """Title can be changed after creation."""
        task = Task(id=1, title="Original")
        task.title = "Updated"
        assert task.title == "Updated"

    def test_description_is_mutable(self) -> None:
        """Description can be changed after creation."""
        task = Task(id=1, title="Task", description="Original")
        task.description = "Updated"
        assert task.description == "Updated"

    def test_completed_is_mutable(self) -> None:
        """Completed status can be toggled."""
        task = Task(id=1, title="Task", completed=False)
        task.completed = True
        assert task.completed is True
        task.completed = False
        assert task.completed is False
