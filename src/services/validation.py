"""
ValidationSkill implementation per spec.md.

Handles all input validation operations. This skill is stateless
and deterministic, providing consistent validation across the application.
"""

from typing import Optional

from src.exceptions import EmptyTitleError, InvalidIdError


def validate_title(title: str) -> str:
    """Validate and normalize task title.

    Args:
        title: The title string to validate.

    Returns:
        The stripped, validated title.

    Raises:
        EmptyTitleError: If title is empty or contains only whitespace.
    """
    if not title or not title.strip():
        raise EmptyTitleError()
    return title.strip()


def validate_id(id_str: str) -> int:
    """Validate and convert task ID from string.

    Args:
        id_str: The ID string to validate.

    Returns:
        The validated ID as a positive integer.

    Raises:
        InvalidIdError: If ID is not a valid positive integer.
    """
    try:
        task_id = int(id_str)
        if task_id <= 0:
            raise InvalidIdError(id_str)
        return task_id
    except ValueError:
        raise InvalidIdError(id_str)


def validate_description(description: Optional[str]) -> str:
    """Validate and normalize task description.

    Description validation always passes in Phase I.
    This function normalizes the input by stripping whitespace
    and handling None values.

    Args:
        description: The description string to validate (may be None).

    Returns:
        The stripped description, or empty string if None/whitespace-only.
    """
    if description is None:
        return ""
    return description.strip()
