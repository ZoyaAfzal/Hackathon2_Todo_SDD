"""
Contract tests for 'help' command per cli-contract.md.

CT-HELP-001
"""

import pytest
from src.cli.commands import HelpCommand


class TestHelpCommandContract:
    """Contract tests for help command."""

    def test_ct_help_001_displays_all_commands(self) -> None:
        """CT-HELP-001: Displays all commands."""
        command = HelpCommand()

        result = command.execute()

        # Verify header
        assert "Todo Application - Phase I" in result

        # Verify all commands are listed
        assert "add <title> [description]" in result
        assert "list" in result
        assert "view <id>" in result
        assert "complete <id>" in result
        assert "uncomplete <id>" in result
        assert "update <id>" in result
        assert "--title" in result
        assert "--description" in result
        assert "delete <id>" in result
        assert "help" in result
        assert "exit" in result

        # Verify command descriptions
        assert "Create a new task" in result
        assert "View all tasks" in result
        assert "View a single task" in result
        assert "Mark task as complete" in result
        assert "Mark task as incomplete" in result
        assert "Update task attributes" in result
        assert "Remove a task" in result
        assert "Show this help message" in result
        assert "Exit the application" in result
