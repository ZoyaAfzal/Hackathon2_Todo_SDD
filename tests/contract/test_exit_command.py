"""
Contract tests for 'exit' command per cli-contract.md.

CT-EXIT-001
"""

import pytest
from src.cli.commands import ExitCommand


class TestExitCommandContract:
    """Contract tests for exit command."""

    def test_ct_exit_001_terminates_application(self) -> None:
        """CT-EXIT-001: Terminates application with goodbye message."""
        command = ExitCommand()

        result = command.execute()

        assert "Goodbye!" in result
