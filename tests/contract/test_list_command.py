"""
Contract tests for 'list' command per cli-contract.md.

CT-LIST-001 through CT-LIST-004
"""

import pytest
from src.state.store import TaskStore
from src.services.query_service import QueryService
from src.cli.commands import ListCommand


class TestListCommandContract:
    """Contract tests for list command."""

    def test_ct_list_001_empty_list_shows_no_tasks_found(self) -> None:
        """CT-LIST-001: Empty list shows 'No tasks found'."""
        store = TaskStore()
        service = QueryService(store)
        command = ListCommand(service)

        result = command.execute()

        assert "No tasks found" in result

    def test_ct_list_002_tasks_display_with_correct_format(self) -> None:
        """CT-LIST-002: Tasks display with correct format."""
        store = TaskStore()
        store.add_task("Buy groceries", "Milk, eggs")
        store.add_task("Call dentist")
        service = QueryService(store)
        command = ListCommand(service)

        result = command.execute()

        assert "Tasks:" in result
        assert "[1]" in result
        assert "Buy groceries" in result
        assert "Milk, eggs" in result
        assert "[2]" in result
        assert "Call dentist" in result
        assert "Created:" in result

    def test_ct_list_003_completed_tasks_show_x(self) -> None:
        """CT-LIST-003: Completed tasks show [x]."""
        store = TaskStore()
        store.add_task("Completed task")
        store.complete_task(1)
        service = QueryService(store)
        command = ListCommand(service)

        result = command.execute()

        assert "[x]" in result

    def test_ct_list_004_incomplete_tasks_show_empty_brackets(self) -> None:
        """CT-LIST-004: Incomplete tasks show [ ]."""
        store = TaskStore()
        store.add_task("Incomplete task")
        service = QueryService(store)
        command = ListCommand(service)

        result = command.execute()

        assert "[ ]" in result
