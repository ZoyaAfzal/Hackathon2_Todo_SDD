"""
Contract tests for 'delete' command per cli-contract.md.

CT-DEL-001 through CT-DEL-003
"""

import pytest
from src.state.store import TaskStore
from src.services.task_service import TaskService
from src.cli.commands import DeleteCommand


class TestDeleteCommandContract:
    """Contract tests for delete command."""

    def test_ct_del_001_valid_id_deletes_task(self) -> None:
        """CT-DEL-001: Valid ID deletes task."""
        store = TaskStore()
        store.add_task("Task to delete")
        service = TaskService(store)
        command = DeleteCommand(service)

        result = command.execute(1)

        assert "[OK]" in result
        assert "Task 1 deleted" in result
        assert not store.task_exists(1)

    def test_ct_del_002_nonexistent_id_returns_error(self) -> None:
        """CT-DEL-002: Non-existent ID returns error."""
        store = TaskStore()
        service = TaskService(store)
        command = DeleteCommand(service)

        result = command.execute(999)

        assert "[ERROR]" in result
        assert "Task not found: 999" in result

    def test_ct_del_003_deleted_task_not_in_list(self) -> None:
        """CT-DEL-003: Deleted task not in list."""
        store = TaskStore()
        store.add_task("Task 1")
        store.add_task("Task 2")
        store.add_task("Task 3")
        service = TaskService(store)
        command = DeleteCommand(service)

        command.execute(2)

        tasks = store.get_all_tasks()
        task_ids = [t.id for t in tasks]
        assert 2 not in task_ids
        assert 1 in task_ids
        assert 3 in task_ids
