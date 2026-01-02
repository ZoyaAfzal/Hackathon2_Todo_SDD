"""
Unit tests for TaskService (TaskManagementSkill implementation).

Tests task lifecycle operations per spec.md and data-model.md.
"""

import pytest
from src.services.task_service import TaskService
from src.state.store import TaskStore
from src.exceptions import TaskNotFoundError, EmptyTitleError


class TestCreateTask:
    """Tests for create_task operation (User Story 1)."""

    def test_create_task_with_title(self) -> None:
        """Create task with title only."""
        store = TaskStore()
        service = TaskService(store)

        task = service.create_task("Buy groceries")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.completed is False

    def test_create_task_with_description(self) -> None:
        """Create task with title and description."""
        store = TaskStore()
        service = TaskService(store)

        task = service.create_task("Buy groceries", "Milk, eggs, bread")

        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"

    def test_create_multiple_tasks_sequential_ids(self) -> None:
        """Multiple tasks get sequential IDs."""
        store = TaskStore()
        service = TaskService(store)

        task1 = service.create_task("Task 1")
        task2 = service.create_task("Task 2")
        task3 = service.create_task("Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_create_task_empty_title_raises_error(self) -> None:
        """Creating with empty title raises EmptyTitleError."""
        store = TaskStore()
        service = TaskService(store)

        with pytest.raises(EmptyTitleError):
            service.create_task("")

    def test_create_task_whitespace_title_raises_error(self) -> None:
        """Creating with whitespace-only title raises EmptyTitleError."""
        store = TaskStore()
        service = TaskService(store)

        with pytest.raises(EmptyTitleError):
            service.create_task("   ")


class TestCompleteTask:
    """Tests for complete_task operation (User Story 3)."""

    def test_complete_task(self) -> None:
        """Mark task as complete."""
        store = TaskStore()
        service = TaskService(store)
        service.create_task("Task")

        result = service.complete_task(1)

        assert result.completed is True

    def test_complete_already_complete_task(self) -> None:
        """Completing already complete task is idempotent."""
        store = TaskStore()
        service = TaskService(store)
        service.create_task("Task")
        service.complete_task(1)

        result = service.complete_task(1)

        assert result.completed is True

    def test_complete_nonexistent_task_raises_error(self) -> None:
        """Completing non-existent task raises TaskNotFoundError."""
        store = TaskStore()
        service = TaskService(store)

        with pytest.raises(TaskNotFoundError):
            service.complete_task(999)


class TestUncompleteTask:
    """Tests for uncomplete_task operation (User Story 6)."""

    def test_uncomplete_task(self) -> None:
        """Mark completed task as incomplete."""
        store = TaskStore()
        service = TaskService(store)
        service.create_task("Task")
        service.complete_task(1)

        result = service.uncomplete_task(1)

        assert result.completed is False

    def test_uncomplete_already_incomplete_task(self) -> None:
        """Uncompleting already incomplete task is idempotent."""
        store = TaskStore()
        service = TaskService(store)
        service.create_task("Task")

        result = service.uncomplete_task(1)

        assert result.completed is False

    def test_uncomplete_nonexistent_task_raises_error(self) -> None:
        """Uncompleting non-existent task raises TaskNotFoundError."""
        store = TaskStore()
        service = TaskService(store)

        with pytest.raises(TaskNotFoundError):
            service.uncomplete_task(999)


class TestUpdateTask:
    """Tests for update_task operation (User Story 4)."""

    def test_update_task_title(self) -> None:
        """Update task title."""
        store = TaskStore()
        service = TaskService(store)
        service.create_task("Original")

        result = service.update_task(1, title="Updated")

        assert result.title == "Updated"

    def test_update_task_description(self) -> None:
        """Update task description."""
        store = TaskStore()
        service = TaskService(store)
        service.create_task("Task", "Original")

        result = service.update_task(1, description="Updated")

        assert result.description == "Updated"

    def test_update_task_both_fields(self) -> None:
        """Update both title and description."""
        store = TaskStore()
        service = TaskService(store)
        service.create_task("Original", "Old")

        result = service.update_task(1, title="New", description="Updated")

        assert result.title == "New"
        assert result.description == "Updated"

    def test_update_nonexistent_task_raises_error(self) -> None:
        """Updating non-existent task raises TaskNotFoundError."""
        store = TaskStore()
        service = TaskService(store)

        with pytest.raises(TaskNotFoundError):
            service.update_task(999, title="New")

    def test_update_to_empty_title_raises_error(self) -> None:
        """Updating to empty title raises EmptyTitleError."""
        store = TaskStore()
        service = TaskService(store)
        service.create_task("Original")

        with pytest.raises(EmptyTitleError):
            service.update_task(1, title="")


class TestDeleteTask:
    """Tests for delete_task operation (User Story 5)."""

    def test_delete_task(self) -> None:
        """Delete existing task."""
        store = TaskStore()
        service = TaskService(store)
        service.create_task("Task to delete")

        result = service.delete_task(1)

        assert result is True
        assert not store.task_exists(1)

    def test_delete_nonexistent_task_raises_error(self) -> None:
        """Deleting non-existent task raises TaskNotFoundError."""
        store = TaskStore()
        service = TaskService(store)

        with pytest.raises(TaskNotFoundError):
            service.delete_task(999)

    def test_delete_preserves_other_tasks(self) -> None:
        """Deleting one task preserves others."""
        store = TaskStore()
        service = TaskService(store)
        service.create_task("Task 1")
        service.create_task("Task 2")
        service.create_task("Task 3")

        service.delete_task(2)

        assert store.task_exists(1)
        assert not store.task_exists(2)
        assert store.task_exists(3)
