"""
Integration tests for CLI operations.

Tests full workflow scenarios through the CLI interface.
"""

import pytest
from src.state.store import TaskStore
from src.cli.parser import TodoParser


class TestCLIWorkflows:
    """Integration tests for complete CLI workflows."""

    def setup_method(self) -> None:
        """Set up fresh store and parser for each test."""
        self.store = TaskStore()
        self.parser = TodoParser(self.store)

    def test_full_task_lifecycle(self) -> None:
        """Test complete task lifecycle: create -> view -> complete -> delete."""
        # Create a task
        result, should_exit = self.parser.parse_and_execute(
            ["add", "Buy groceries", "Milk and eggs"]
        )
        assert "[OK]" in result
        assert "Task 1 created" in result
        assert not should_exit

        # View the task
        result, should_exit = self.parser.parse_and_execute(["view", "1"])
        assert "Task 1:" in result
        assert "Buy groceries" in result
        assert "Milk and eggs" in result
        assert "Incomplete" in result
        assert not should_exit

        # Mark as complete
        result, should_exit = self.parser.parse_and_execute(["complete", "1"])
        assert "[OK]" in result
        assert "marked as complete" in result
        assert not should_exit

        # Verify completion in view
        result, should_exit = self.parser.parse_and_execute(["view", "1"])
        assert "Complete" in result
        assert not should_exit

        # Delete the task
        result, should_exit = self.parser.parse_and_execute(["delete", "1"])
        assert "[OK]" in result
        assert "deleted" in result
        assert not should_exit

        # Verify deletion
        result, should_exit = self.parser.parse_and_execute(["view", "1"])
        assert "[ERROR]" in result
        assert "not found" in result
        assert not should_exit

    def test_multiple_tasks_workflow(self) -> None:
        """Test workflow with multiple tasks."""
        # Create multiple tasks
        self.parser.parse_and_execute(["add", "Task One"])
        self.parser.parse_and_execute(["add", "Task Two"])
        self.parser.parse_and_execute(["add", "Task Three"])

        # List all tasks
        result, _ = self.parser.parse_and_execute(["list"])
        assert "Tasks:" in result
        assert "[1]" in result
        assert "[2]" in result
        assert "[3]" in result
        assert "Task One" in result
        assert "Task Two" in result
        assert "Task Three" in result

    def test_update_workflow(self) -> None:
        """Test task update workflow."""
        # Create a task
        self.parser.parse_and_execute(["add", "Original title", "Original desc"])

        # Update title
        result, _ = self.parser.parse_and_execute(
            ["update", "1", "--title", "Updated title"]
        )
        assert "[OK]" in result
        assert "updated" in result

        # Verify update
        result, _ = self.parser.parse_and_execute(["view", "1"])
        assert "Updated title" in result
        assert "Original desc" in result

        # Update description
        self.parser.parse_and_execute(
            ["update", "1", "--description", "Updated desc"]
        )
        result, _ = self.parser.parse_and_execute(["view", "1"])
        assert "Updated title" in result
        assert "Updated desc" in result

    def test_complete_uncomplete_workflow(self) -> None:
        """Test toggling task completion status."""
        # Create a task
        self.parser.parse_and_execute(["add", "Toggle task"])

        # Initially incomplete
        result, _ = self.parser.parse_and_execute(["view", "1"])
        assert "Incomplete" in result

        # Mark complete
        self.parser.parse_and_execute(["complete", "1"])
        result, _ = self.parser.parse_and_execute(["view", "1"])
        assert "Complete" in result

        # Mark incomplete again
        self.parser.parse_and_execute(["uncomplete", "1"])
        result, _ = self.parser.parse_and_execute(["view", "1"])
        assert "Incomplete" in result

    def test_error_handling_workflow(self) -> None:
        """Test error handling in various scenarios."""
        # View non-existent task
        result, _ = self.parser.parse_and_execute(["view", "999"])
        assert "[ERROR]" in result
        assert "not found" in result

        # Complete non-existent task
        result, _ = self.parser.parse_and_execute(["complete", "999"])
        assert "[ERROR]" in result
        assert "not found" in result

        # Delete non-existent task
        result, _ = self.parser.parse_and_execute(["delete", "999"])
        assert "[ERROR]" in result
        assert "not found" in result

        # Invalid ID
        result, _ = self.parser.parse_and_execute(["view", "abc"])
        assert "[ERROR]" in result
        assert "Invalid task ID" in result

    def test_empty_input_shows_help(self) -> None:
        """Test that empty input shows help."""
        result, should_exit = self.parser.parse_and_execute([])
        assert "Todo Application - Phase I" in result
        assert not should_exit

    def test_unknown_command_error(self) -> None:
        """Test unknown command handling."""
        result, should_exit = self.parser.parse_and_execute(["unknown_cmd"])
        assert "[ERROR]" in result
        assert "Unknown command" in result
        assert not should_exit

    def test_help_command(self) -> None:
        """Test help command integration."""
        result, should_exit = self.parser.parse_and_execute(["help"])
        assert "Todo Application - Phase I" in result
        assert "add" in result
        assert "list" in result
        assert not should_exit

    def test_exit_command(self) -> None:
        """Test exit command signals termination."""
        result, should_exit = self.parser.parse_and_execute(["exit"])
        assert "Goodbye!" in result
        assert should_exit

    def test_add_empty_title_error(self) -> None:
        """Test that empty title produces error."""
        result, _ = self.parser.parse_and_execute(["add", ""])
        assert "[ERROR]" in result
        assert "Title cannot be empty" in result

    def test_list_empty_state(self) -> None:
        """Test list command on empty state."""
        result, _ = self.parser.parse_and_execute(["list"])
        assert "No tasks found" in result

    def test_update_no_options_error(self) -> None:
        """Test update without options produces error."""
        self.parser.parse_and_execute(["add", "Test task"])
        result, _ = self.parser.parse_and_execute(["update", "1"])
        assert "[ERROR]" in result
        assert "No updates specified" in result

    def test_deterministic_parsing(self) -> None:
        """Ensure parsing is deterministic - no NLP interpretation."""
        # Commands must be exact matches
        result, _ = self.parser.parse_and_execute(["ADD", "Test"])
        assert "[ERROR]" in result or "Unknown command" in result

        # Natural language should not work
        result, _ = self.parser.parse_and_execute(["please", "add", "a", "task"])
        assert "[ERROR]" in result or "Unknown command" in result
