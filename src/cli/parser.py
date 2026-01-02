"""
CLI command parser using argparse per cli-contract.md.

Parses structured CLI commands and routes to appropriate handlers.
"""

import argparse
import sys
from typing import Optional, List, Tuple

from src.state.store import TaskStore
from src.services.task_service import TaskService
from src.services.query_service import QueryService
from src.services.validation import validate_id
from src.cli.commands import (
    AddCommand,
    ListCommand,
    ViewCommand,
    CompleteCommand,
    UncompleteCommand,
    UpdateCommand,
    DeleteCommand,
    HelpCommand,
    ExitCommand
)
from src.cli.formatter import format_error
from src.exceptions import InvalidIdError


class TodoParser:
    """CLI parser for todo application commands."""

    def __init__(self, store: TaskStore) -> None:
        """Initialize parser with dependencies.

        Args:
            store: TaskStore for state management.
        """
        self._store = store
        self._task_service = TaskService(store)
        self._query_service = QueryService(store)
        self._setup_parser()

    def _setup_parser(self) -> None:
        """Set up argparse with subcommands."""
        self._parser = argparse.ArgumentParser(
            prog="todo",
            description="Todo Application - Phase I",
            add_help=False
        )
        self._subparsers = self._parser.add_subparsers(dest="command")

        # add command
        add_parser = self._subparsers.add_parser("add", help="Create a new task")
        add_parser.add_argument("title", type=str, help="Task title")
        add_parser.add_argument(
            "description",
            type=str,
            nargs="?",
            default="",
            help="Task description"
        )

        # list command
        self._subparsers.add_parser("list", help="View all tasks")

        # view command
        view_parser = self._subparsers.add_parser("view", help="View a single task")
        view_parser.add_argument("id", type=str, help="Task ID")

        # complete command
        complete_parser = self._subparsers.add_parser(
            "complete",
            help="Mark task as complete"
        )
        complete_parser.add_argument("id", type=str, help="Task ID")

        # uncomplete command
        uncomplete_parser = self._subparsers.add_parser(
            "uncomplete",
            help="Mark task as incomplete"
        )
        uncomplete_parser.add_argument("id", type=str, help="Task ID")

        # update command
        update_parser = self._subparsers.add_parser(
            "update",
            help="Update task attributes"
        )
        update_parser.add_argument("id", type=str, help="Task ID")
        update_parser.add_argument("--title", type=str, help="New title")
        update_parser.add_argument("--description", type=str, help="New description")

        # delete command
        delete_parser = self._subparsers.add_parser("delete", help="Remove a task")
        delete_parser.add_argument("id", type=str, help="Task ID")

        # help command
        self._subparsers.add_parser("help", help="Show help message")

        # exit command
        self._subparsers.add_parser("exit", help="Exit the application")

    def parse_and_execute(self, args: List[str]) -> Tuple[str, bool]:
        """Parse command and execute.

        Args:
            args: Command line arguments.

        Returns:
            Tuple of (result message, should_exit flag).
        """
        if not args:
            return HelpCommand().execute(), False

        try:
            parsed = self._parser.parse_args(args)
        except SystemExit:
            return format_error(f"Unknown command: {args[0]}"), False

        command = parsed.command

        if command is None:
            return HelpCommand().execute(), False

        if command == "add":
            cmd = AddCommand(self._task_service)
            return cmd.execute(parsed.title, parsed.description), False

        elif command == "list":
            cmd = ListCommand(self._query_service)
            return cmd.execute(), False

        elif command == "view":
            try:
                task_id = validate_id(parsed.id)
                cmd = ViewCommand(self._query_service)
                return cmd.execute(task_id), False
            except InvalidIdError as e:
                return format_error(e.message), False

        elif command == "complete":
            try:
                task_id = validate_id(parsed.id)
                cmd = CompleteCommand(self._task_service)
                return cmd.execute(task_id), False
            except InvalidIdError as e:
                return format_error(e.message), False

        elif command == "uncomplete":
            try:
                task_id = validate_id(parsed.id)
                cmd = UncompleteCommand(self._task_service)
                return cmd.execute(task_id), False
            except InvalidIdError as e:
                return format_error(e.message), False

        elif command == "update":
            try:
                task_id = validate_id(parsed.id)
                cmd = UpdateCommand(self._task_service)
                return cmd.execute(task_id, parsed.title, parsed.description), False
            except InvalidIdError as e:
                return format_error(e.message), False

        elif command == "delete":
            try:
                task_id = validate_id(parsed.id)
                cmd = DeleteCommand(self._task_service)
                return cmd.execute(task_id), False
            except InvalidIdError as e:
                return format_error(e.message), False

        elif command == "help":
            return HelpCommand().execute(), False

        elif command == "exit":
            return ExitCommand().execute(), True

        else:
            return format_error(f"Unknown command: {command}"), False
