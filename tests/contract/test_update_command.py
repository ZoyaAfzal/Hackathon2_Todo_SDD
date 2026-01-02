"""
Contract tests for 'update' command per cli-contract.md.

CT-UPD-001 through CT-UPD-005
"""

import pytest
from src.state.store import TaskStore
from src.services.task_service import TaskService
from src.cli.commands import UpdateCommand


class TestUpdateCommandContract:
    """Contract tests for update command."""

    def test_ct_upd_001_valid_title_update_succeeds(self) -> None:
        """CT-UPD-001: Valid title update succeeds."""
        store = TaskStore()
        store.add_task("Original title")
        service = TaskService(store)
        command = UpdateCommand(service)

        result = command.execute(1, title="New title")

        assert "[OK]" in result
        assert "Task 1 updated" in result
        assert store.get_task(1).title == "New title"

    def test_ct_upd_002_valid_description_update_succeeds(self) -> None:
        """CT-UPD-002: Valid description update succeeds."""
        store = TaskStore()
        store.add_task("Task", "Original description")
        service = TaskService(store)
        command = UpdateCommand(service)

        result = command.execute(1, description="New description")

        assert "[OK]" in result
        assert store.get_task(1).description == "New description"

    def test_ct_upd_003_empty_title_update_returns_error(self) -> None:
        """CT-UPD-003: Empty title update returns error."""
        store = TaskStore()
        store.add_task("Original")
        service = TaskService(store)
        command = UpdateCommand(service)

        result = command.execute(1, title="")

        assert "[ERROR]" in result
        assert "Title cannot be empty" in result
        # Original title preserved
        assert store.get_task(1).title == "Original"

    def test_ct_upd_004_nonexistent_id_returns_error(self) -> None:
        """CT-UPD-004: Non-existent ID returns error."""
        store = TaskStore()
        service = TaskService(store)
        command = UpdateCommand(service)

        result = command.execute(999, title="New")

        assert "[ERROR]" in result
        assert "Task not found: 999" in result

    def test_ct_upd_005_no_options_returns_error(self) -> None:
        """CT-UPD-005: No options returns error."""
        store = TaskStore()
        store.add_task("Task")
        service = TaskService(store)
        command = UpdateCommand(service)

        result = command.execute(1)  # No title or description

        assert "[ERROR]" in result
        assert "No updates specified" in result
