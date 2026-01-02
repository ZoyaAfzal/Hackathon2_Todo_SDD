"""
Contract tests for 'add' command per cli-contract.md.

CT-ADD-001 through CT-ADD-005
"""

import pytest
from src.state.store import TaskStore
from src.services.task_service import TaskService
from src.cli.commands import AddCommand
from src.cli.formatter import format_success, format_error
from src.exceptions import EmptyTitleError


class TestAddCommandContract:
    """Contract tests for add command."""

    def test_ct_add_001_valid_title_creates_task(self) -> None:
        """CT-ADD-001: Valid title creates task."""
        store = TaskStore()
        service = TaskService(store)
        command = AddCommand(service)

        result = command.execute("Buy groceries")

        assert "Task 1 created" in result
        assert "Buy groceries" in result
        assert store.task_exists(1)

    def test_ct_add_002_valid_title_and_description_creates_task(self) -> None:
        """CT-ADD-002: Valid title and description creates task."""
        store = TaskStore()
        service = TaskService(store)
        command = AddCommand(service)

        result = command.execute("Buy groceries", "Milk, eggs, bread")

        assert "Task 1 created" in result
        task = store.get_task(1)
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"

    def test_ct_add_003_empty_title_returns_error(self) -> None:
        """CT-ADD-003: Empty title returns error."""
        store = TaskStore()
        service = TaskService(store)
        command = AddCommand(service)

        result = command.execute("")

        assert "[ERROR]" in result
        assert "Title cannot be empty" in result
        assert not store.task_exists(1)

    def test_ct_add_004_whitespace_only_title_returns_error(self) -> None:
        """CT-ADD-004: Whitespace-only title returns error."""
        store = TaskStore()
        service = TaskService(store)
        command = AddCommand(service)

        result = command.execute("   ")

        assert "[ERROR]" in result
        assert "Title cannot be empty" in result
        assert not store.task_exists(1)

    def test_ct_add_005_assigned_id_is_unique_and_sequential(self) -> None:
        """CT-ADD-005: Assigned ID is unique and sequential."""
        store = TaskStore()
        service = TaskService(store)
        command = AddCommand(service)

        command.execute("Task 1")
        command.execute("Task 2")
        command.execute("Task 3")

        tasks = store.get_all_tasks()
        ids = [t.id for t in tasks]
        assert ids == [1, 2, 3]
