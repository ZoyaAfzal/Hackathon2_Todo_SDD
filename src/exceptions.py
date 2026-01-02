"""
Custom exception hierarchy for Todo Application Phase I.

All exceptions inherit from TodoError to enable consistent error handling
and formatted error output per CLI contract specification.
"""


class TodoError(Exception):
    """Base exception for all Todo application errors."""

    def __init__(self, message: str) -> None:
        """Initialize TodoError with a message.

        Args:
            message: Human-readable error description.
        """
        self.message = message
        super().__init__(self.message)


class TaskNotFoundError(TodoError):
    """Raised when a task with the specified ID does not exist."""

    def __init__(self, task_id: int) -> None:
        """Initialize TaskNotFoundError.

        Args:
            task_id: The ID that was not found.
        """
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")


class EmptyTitleError(TodoError):
    """Raised when task title is empty or contains only whitespace."""

    def __init__(self) -> None:
        """Initialize EmptyTitleError."""
        super().__init__("Title cannot be empty")


class InvalidIdError(TodoError):
    """Raised when task ID is not a valid positive integer."""

    def __init__(self, invalid_id: str) -> None:
        """Initialize InvalidIdError.

        Args:
            invalid_id: The invalid ID string that was provided.
        """
        self.invalid_id = invalid_id
        super().__init__(f"Invalid task ID: {invalid_id}")


class NoUpdatesError(TodoError):
    """Raised when update command is called without any update options."""

    def __init__(self) -> None:
        """Initialize NoUpdatesError."""
        super().__init__("No updates specified")


class UnknownCommandError(TodoError):
    """Raised when an unrecognized command is entered."""

    def __init__(self, command: str) -> None:
        """Initialize UnknownCommandError.

        Args:
            command: The unrecognized command string.
        """
        self.command = command
        super().__init__(f"Unknown command: {command}")
