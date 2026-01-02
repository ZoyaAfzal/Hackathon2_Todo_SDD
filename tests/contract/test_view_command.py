"""
Contract tests for 'view' command per cli-contract.md.

CT-VIEW-001 through CT-VIEW-003
"""

import pytest
from src.state.store import TaskStore
from src.services.query_service import QueryService
from src.services.validation import validate_id
from src.cli.commands import ViewCommand
from src.cli.formatter import format_error
from src.exceptions import InvalidIdError


class TestViewCommandContract:
    """Contract tests for view command."""

    def test_ct_view_001_valid_id_shows_task_details(self) -> None:
        """CT-VIEW-001: Valid ID shows task details."""
        store = TaskStore()
        store.add_task("Buy groceries", "Milk, eggs, bread")
        service = QueryService(store)
        command = ViewCommand(service)

        result = command.execute(1)

        assert "Task 1:" in result
        assert "Title: Buy groceries" in result
        assert "Description: Milk, eggs, bread" in result
        assert "Status: Incomplete" in result
        assert "Created:" in result

    def test_ct_view_002_invalid_id_returns_error(self) -> None:
        """CT-VIEW-002: Invalid ID returns error."""
        # Test validation separately since command expects int
        with pytest.raises(InvalidIdError) as exc_info:
            validate_id("abc")

        assert "Invalid task ID: abc" in str(exc_info.value.message)

    def test_ct_view_003_nonexistent_id_returns_not_found(self) -> None:
        """CT-VIEW-003: Non-existent ID returns not found."""
        store = TaskStore()
        service = QueryService(store)
        command = ViewCommand(service)

        result = command.execute(999)

        assert "[ERROR]" in result
        assert "Task not found: 999" in result

    def test_view_completed_task_shows_complete_status(self) -> None:
        """View completed task shows 'Complete' status."""
        store = TaskStore()
        store.add_task("Task")
        store.complete_task(1)
        service = QueryService(store)
        command = ViewCommand(service)

        result = command.execute(1)

        assert "Status: Complete" in result
