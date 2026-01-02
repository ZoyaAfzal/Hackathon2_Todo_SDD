"""
Unit tests for TaskStore (StateManagementAgent implementation).

Tests state management operations per data-model.md specification.
"""

import pytest
from src.state.store import TaskStore
from src.models.task import Task
from src.exceptions import TaskNotFoundError, EmptyTitleError


class TestTaskStoreInitialization:
    """Tests for TaskStore initialization per Phase I constraints."""

    def test_store_initializes_empty(self) -> None:
        """TaskStore starts with empty task collection."""
        store = TaskStore()
        assert store.get_all_tasks() == []

    def test_store_next_id_starts_at_one(self) -> None:
        """First task gets ID 1."""
        store = TaskStore()
        task = store.add_task("First task")
        assert task.id == 1


class TestTaskStoreAddTask:
    """Tests for adding tasks to TaskStore."""

    def test_add_task_with_title(self) -> None:
        """Add task with title only returns task with generated ID."""
        store = TaskStore()
        task = store.add_task("Buy groceries")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.completed is False

    def test_add_task_with_description(self) -> None:
        """Add task with title and description."""
        store = TaskStore()
        task = store.add_task("Buy groceries", "Milk, eggs")

        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs"

    def test_add_multiple_tasks_increments_id(self) -> None:
        """Each new task gets sequential ID."""
        store = TaskStore()
        task1 = store.add_task("Task 1")
        task2 = store.add_task("Task 2")
        task3 = store.add_task("Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_task_empty_title_raises_error(self) -> None:
        """Adding task with empty title raises EmptyTitleError."""
        store = TaskStore()
        with pytest.raises(EmptyTitleError):
            store.add_task("")


class TestTaskStoreGetTask:
    """Tests for retrieving individual tasks."""

    def test_get_task_by_id(self) -> None:
        """Get existing task by ID."""
        store = TaskStore()
        created = store.add_task("Test task")
        retrieved = store.get_task(1)

        assert retrieved.id == created.id
        assert retrieved.title == created.title

    def test_get_nonexistent_task_raises_error(self) -> None:
        """Getting non-existent task raises TaskNotFoundError."""
        store = TaskStore()
        with pytest.raises(TaskNotFoundError) as exc_info:
            store.get_task(999)
        assert exc_info.value.task_id == 999


class TestTaskStoreGetAllTasks:
    """Tests for retrieving all tasks."""

    def test_get_all_tasks_empty(self) -> None:
        """Get all tasks from empty store returns empty list."""
        store = TaskStore()
        assert store.get_all_tasks() == []

    def test_get_all_tasks_returns_all(self) -> None:
        """Get all tasks returns all added tasks."""
        store = TaskStore()
        store.add_task("Task 1")
        store.add_task("Task 2")
        store.add_task("Task 3")

        tasks = store.get_all_tasks()
        assert len(tasks) == 3
        assert [t.title for t in tasks] == ["Task 1", "Task 2", "Task 3"]


class TestTaskStoreUpdateTask:
    """Tests for updating tasks."""

    def test_update_task_title(self) -> None:
        """Update task title."""
        store = TaskStore()
        store.add_task("Original")
        updated = store.update_task(1, title="Updated")

        assert updated.title == "Updated"
        assert store.get_task(1).title == "Updated"

    def test_update_task_description(self) -> None:
        """Update task description."""
        store = TaskStore()
        store.add_task("Task", "Original")
        updated = store.update_task(1, description="Updated")

        assert updated.description == "Updated"

    def test_update_task_both_fields(self) -> None:
        """Update both title and description."""
        store = TaskStore()
        store.add_task("Original", "Old desc")
        updated = store.update_task(1, title="New title", description="New desc")

        assert updated.title == "New title"
        assert updated.description == "New desc"

    def test_update_nonexistent_task_raises_error(self) -> None:
        """Updating non-existent task raises TaskNotFoundError."""
        store = TaskStore()
        with pytest.raises(TaskNotFoundError):
            store.update_task(999, title="New")

    def test_update_to_empty_title_raises_error(self) -> None:
        """Updating to empty title raises EmptyTitleError."""
        store = TaskStore()
        store.add_task("Original")
        with pytest.raises(EmptyTitleError):
            store.update_task(1, title="")


class TestTaskStoreDeleteTask:
    """Tests for deleting tasks."""

    def test_delete_task(self) -> None:
        """Delete existing task."""
        store = TaskStore()
        store.add_task("Task to delete")
        result = store.delete_task(1)

        assert result is True
        assert store.get_all_tasks() == []

    def test_delete_nonexistent_task_raises_error(self) -> None:
        """Deleting non-existent task raises TaskNotFoundError."""
        store = TaskStore()
        with pytest.raises(TaskNotFoundError):
            store.delete_task(999)

    def test_delete_preserves_other_tasks(self) -> None:
        """Deleting one task preserves others."""
        store = TaskStore()
        store.add_task("Task 1")
        store.add_task("Task 2")
        store.add_task("Task 3")

        store.delete_task(2)

        tasks = store.get_all_tasks()
        assert len(tasks) == 2
        assert [t.id for t in tasks] == [1, 3]


class TestTaskStoreCompleteTask:
    """Tests for marking tasks complete/incomplete."""

    def test_complete_task(self) -> None:
        """Mark task as complete."""
        store = TaskStore()
        store.add_task("Task")
        updated = store.complete_task(1)

        assert updated.completed is True
        assert store.get_task(1).completed is True

    def test_complete_already_complete_task(self) -> None:
        """Completing already complete task is idempotent."""
        store = TaskStore()
        store.add_task("Task")
        store.complete_task(1)
        updated = store.complete_task(1)

        assert updated.completed is True

    def test_uncomplete_task(self) -> None:
        """Mark task as incomplete."""
        store = TaskStore()
        store.add_task("Task")
        store.complete_task(1)
        updated = store.uncomplete_task(1)

        assert updated.completed is False

    def test_uncomplete_already_incomplete_task(self) -> None:
        """Uncompleting already incomplete task is idempotent."""
        store = TaskStore()
        store.add_task("Task")
        updated = store.uncomplete_task(1)

        assert updated.completed is False

    def test_complete_nonexistent_task_raises_error(self) -> None:
        """Completing non-existent task raises TaskNotFoundError."""
        store = TaskStore()
        with pytest.raises(TaskNotFoundError):
            store.complete_task(999)

    def test_uncomplete_nonexistent_task_raises_error(self) -> None:
        """Uncompleting non-existent task raises TaskNotFoundError."""
        store = TaskStore()
        with pytest.raises(TaskNotFoundError):
            store.uncomplete_task(999)


class TestTaskStoreTaskExists:
    """Tests for task existence check."""

    def test_task_exists_true(self) -> None:
        """task_exists returns True for existing task."""
        store = TaskStore()
        store.add_task("Task")
        assert store.task_exists(1) is True

    def test_task_exists_false(self) -> None:
        """task_exists returns False for non-existent task."""
        store = TaskStore()
        assert store.task_exists(999) is False

    def test_task_exists_after_delete(self) -> None:
        """task_exists returns False after task is deleted."""
        store = TaskStore()
        store.add_task("Task")
        store.delete_task(1)
        assert store.task_exists(1) is False
