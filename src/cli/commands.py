"""
CLI command handlers per cli-contract.md.

Each command class handles a specific CLI operation, delegating
business logic to the appropriate service and formatting output.
"""

from typing import Optional, List

from src.services.task_service import TaskService
from src.services.query_service import QueryService
from src.cli.formatter import (
    format_success,
    format_error,
    format_task_created,
    format_task_updated,
    format_task_deleted,
    format_task_completed,
    format_task_uncompleted,
    format_task_list,
    format_task_detail,
    format_help,
    format_goodbye
)
from src.exceptions import TodoError


class AddCommand:
    """Handler for 'add' command."""

    def __init__(self, service: TaskService) -> None:
        """Initialize AddCommand.

        Args:
            service: TaskService for task operations.
        """
        self._service = service

    def execute(self, title: str, description: str = "") -> str:
        """Execute add command.

        Args:
            title: Task title.
            description: Task description (optional).

        Returns:
            Formatted result message.
        """
        try:
            task = self._service.create_task(title, description)
            return format_task_created(task)
        except TodoError as e:
            return format_error(e.message)


class ListCommand:
    """Handler for 'list' command."""

    def __init__(self, service: QueryService) -> None:
        """Initialize ListCommand.

        Args:
            service: QueryService for query operations.
        """
        self._service = service

    def execute(self) -> str:
        """Execute list command.

        Returns:
            Formatted task list.
        """
        tasks = self._service.get_all_tasks()
        return format_task_list(tasks)


class ViewCommand:
    """Handler for 'view' command."""

    def __init__(self, service: QueryService) -> None:
        """Initialize ViewCommand.

        Args:
            service: QueryService for query operations.
        """
        self._service = service

    def execute(self, task_id: int) -> str:
        """Execute view command.

        Args:
            task_id: Task identifier.

        Returns:
            Formatted task detail or error.
        """
        try:
            task = self._service.get_task(task_id)
            return format_task_detail(task)
        except TodoError as e:
            return format_error(e.message)


class CompleteCommand:
    """Handler for 'complete' command."""

    def __init__(self, service: TaskService) -> None:
        """Initialize CompleteCommand.

        Args:
            service: TaskService for task operations.
        """
        self._service = service

    def execute(self, task_id: int) -> str:
        """Execute complete command.

        Args:
            task_id: Task identifier.

        Returns:
            Formatted result message.
        """
        try:
            self._service.complete_task(task_id)
            return format_task_completed(task_id)
        except TodoError as e:
            return format_error(e.message)


class UncompleteCommand:
    """Handler for 'uncomplete' command."""

    def __init__(self, service: TaskService) -> None:
        """Initialize UncompleteCommand.

        Args:
            service: TaskService for task operations.
        """
        self._service = service

    def execute(self, task_id: int) -> str:
        """Execute uncomplete command.

        Args:
            task_id: Task identifier.

        Returns:
            Formatted result message.
        """
        try:
            self._service.uncomplete_task(task_id)
            return format_task_uncompleted(task_id)
        except TodoError as e:
            return format_error(e.message)


class UpdateCommand:
    """Handler for 'update' command."""

    def __init__(self, service: TaskService) -> None:
        """Initialize UpdateCommand.

        Args:
            service: TaskService for task operations.
        """
        self._service = service

    def execute(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> str:
        """Execute update command.

        Args:
            task_id: Task identifier.
            title: New title (optional).
            description: New description (optional).

        Returns:
            Formatted result message.
        """
        if title is None and description is None:
            return format_error("No updates specified")

        try:
            self._service.update_task(task_id, title, description)
            return format_task_updated(task_id)
        except TodoError as e:
            return format_error(e.message)


class DeleteCommand:
    """Handler for 'delete' command."""

    def __init__(self, service: TaskService) -> None:
        """Initialize DeleteCommand.

        Args:
            service: TaskService for task operations.
        """
        self._service = service

    def execute(self, task_id: int) -> str:
        """Execute delete command.

        Args:
            task_id: Task identifier.

        Returns:
            Formatted result message.
        """
        try:
            self._service.delete_task(task_id)
            return format_task_deleted(task_id)
        except TodoError as e:
            return format_error(e.message)


class HelpCommand:
    """Handler for 'help' command."""

    def execute(self) -> str:
        """Execute help command.

        Returns:
            Help text.
        """
        return format_help()


class ExitCommand:
    """Handler for 'exit' command."""

    def execute(self) -> str:
        """Execute exit command.

        Returns:
            Goodbye message.
        """
        return format_goodbye()
