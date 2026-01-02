"""
Unit tests for QueryService (TaskQuerySkill implementation).

Tests task query operations per spec.md.
"""

import pytest
from src.services.query_service import QueryService
from src.state.store import TaskStore
from src.exceptions import TaskNotFoundError


class TestGetAllTasks:
    """Tests for get_all_tasks operation."""

    def test_get_all_tasks_empty(self) -> None:
        """Get all from empty store returns empty list."""
        store = TaskStore()
        service = QueryService(store)

        result = service.get_all_tasks()

        assert result == []

    def test_get_all_tasks_returns_all(self) -> None:
        """Get all returns all tasks."""
        store = TaskStore()
        store.add_task("Task 1")
        store.add_task("Task 2")
        store.add_task("Task 3")
        service = QueryService(store)

        result = service.get_all_tasks()

        assert len(result) == 3
        titles = [t.title for t in result]
        assert titles == ["Task 1", "Task 2", "Task 3"]

    def test_get_all_tasks_preserves_order(self) -> None:
        """Tasks are returned in insertion order."""
        store = TaskStore()
        store.add_task("First")
        store.add_task("Second")
        store.add_task("Third")
        service = QueryService(store)

        result = service.get_all_tasks()

        ids = [t.id for t in result]
        assert ids == [1, 2, 3]


class TestGetTask:
    """Tests for get_task operation."""

    def test_get_task_by_id(self) -> None:
        """Get existing task by ID."""
        store = TaskStore()
        store.add_task("Test task", "Description")
        service = QueryService(store)

        result = service.get_task(1)

        assert result.id == 1
        assert result.title == "Test task"
        assert result.description == "Description"

    def test_get_nonexistent_task_raises_error(self) -> None:
        """Getting non-existent task raises TaskNotFoundError."""
        store = TaskStore()
        service = QueryService(store)

        with pytest.raises(TaskNotFoundError) as exc_info:
            service.get_task(999)

        assert exc_info.value.task_id == 999

    def test_get_task_includes_all_attributes(self) -> None:
        """Retrieved task has all attributes."""
        store = TaskStore()
        store.add_task("Task", "Desc")
        store.complete_task(1)
        service = QueryService(store)

        result = service.get_task(1)

        assert result.id == 1
        assert result.title == "Task"
        assert result.description == "Desc"
        assert result.completed is True
        assert result.created_at is not None


class TestTaskExists:
    """Tests for task_exists operation."""

    def test_task_exists_true(self) -> None:
        """task_exists returns True for existing task."""
        store = TaskStore()
        store.add_task("Task")
        service = QueryService(store)

        assert service.task_exists(1) is True

    def test_task_exists_false(self) -> None:
        """task_exists returns False for non-existent task."""
        store = TaskStore()
        service = QueryService(store)

        assert service.task_exists(999) is False

    def test_task_exists_after_delete(self) -> None:
        """task_exists returns False after task is deleted."""
        store = TaskStore()
        store.add_task("Task")
        store.delete_task(1)
        service = QueryService(store)

        assert service.task_exists(1) is False
