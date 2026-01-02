"""
Contract tests for 'complete' command per cli-contract.md.

CT-COMP-001 through CT-COMP-003
"""

import pytest
from src.state.store import TaskStore
from src.services.task_service import TaskService
from src.cli.commands import CompleteCommand


class TestCompleteCommandContract:
    """Contract tests for complete command."""

    def test_ct_comp_001_valid_id_marks_task_complete(self) -> None:
        """CT-COMP-001: Valid ID marks task complete."""
        store = TaskStore()
        store.add_task("Task to complete")
        service = TaskService(store)
        command = CompleteCommand(service)

        result = command.execute(1)

        assert "[OK]" in result
        assert "Task 1 marked as complete" in result
        assert store.get_task(1).completed is True

    def test_ct_comp_002_already_complete_task_stays_complete(self) -> None:
        """CT-COMP-002: Already complete task stays complete."""
        store = TaskStore()
        store.add_task("Already complete")
        store.complete_task(1)
        service = TaskService(store)
        command = CompleteCommand(service)

        result = command.execute(1)

        assert "[OK]" in result
        assert store.get_task(1).completed is True

    def test_ct_comp_003_nonexistent_id_returns_error(self) -> None:
        """CT-COMP-003: Non-existent ID returns error."""
        store = TaskStore()
        service = TaskService(store)
        command = CompleteCommand(service)

        result = command.execute(999)

        assert "[ERROR]" in result
        assert "Task not found: 999" in result
