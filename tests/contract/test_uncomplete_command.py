"""
Contract tests for 'uncomplete' command per cli-contract.md.

CT-UNCOMP-001 through CT-UNCOMP-003
"""

import pytest
from src.state.store import TaskStore
from src.services.task_service import TaskService
from src.cli.commands import UncompleteCommand


class TestUncompleteCommandContract:
    """Contract tests for uncomplete command."""

    def test_ct_uncomp_001_valid_id_marks_task_incomplete(self) -> None:
        """CT-UNCOMP-001: Valid ID marks task incomplete."""
        store = TaskStore()
        store.add_task("Task to uncomplete")
        store.complete_task(1)
        service = TaskService(store)
        command = UncompleteCommand(service)

        result = command.execute(1)

        assert "[OK]" in result
        assert "Task 1 marked as incomplete" in result
        assert store.get_task(1).completed is False

    def test_ct_uncomp_002_already_incomplete_task_stays_incomplete(self) -> None:
        """CT-UNCOMP-002: Already incomplete task stays incomplete."""
        store = TaskStore()
        store.add_task("Already incomplete")
        service = TaskService(store)
        command = UncompleteCommand(service)

        result = command.execute(1)

        assert "[OK]" in result
        assert store.get_task(1).completed is False

    def test_ct_uncomp_003_nonexistent_id_returns_error(self) -> None:
        """CT-UNCOMP-003: Non-existent ID returns error."""
        store = TaskStore()
        service = TaskService(store)
        command = UncompleteCommand(service)

        result = command.execute(999)

        assert "[ERROR]" in result
        assert "Task not found: 999" in result
