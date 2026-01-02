"""
Output formatting utilities per cli-contract.md.

Provides consistent output formatting for CLI commands.
"""

from datetime import datetime
from typing import List

from src.models.task import Task


def format_success(message: str) -> str:
    """Format a success message.

    Args:
        message: The success message content.

    Returns:
        Formatted success string: [OK] <message>
    """
    return f"[OK] {message}"


def format_error(message: str) -> str:
    """Format an error message.

    Args:
        message: The error message content.

    Returns:
        Formatted error string: [ERROR] <message>
    """
    return f"[ERROR] {message}"


def format_task_created(task: Task) -> str:
    """Format task creation confirmation.

    Args:
        task: The created task.

    Returns:
        Formatted success message for task creation.
    """
    return format_success(f'Task {task.id} created: "{task.title}"')


def format_task_updated(task_id: int) -> str:
    """Format task update confirmation.

    Args:
        task_id: The updated task ID.

    Returns:
        Formatted success message for task update.
    """
    return format_success(f"Task {task_id} updated")


def format_task_deleted(task_id: int) -> str:
    """Format task deletion confirmation.

    Args:
        task_id: The deleted task ID.

    Returns:
        Formatted success message for task deletion.
    """
    return format_success(f"Task {task_id} deleted")


def format_task_completed(task_id: int) -> str:
    """Format task completion confirmation.

    Args:
        task_id: The completed task ID.

    Returns:
        Formatted success message for task completion.
    """
    return format_success(f"Task {task_id} marked as complete")


def format_task_uncompleted(task_id: int) -> str:
    """Format task uncompletion confirmation.

    Args:
        task_id: The uncompleted task ID.

    Returns:
        Formatted success message for task uncompletion.
    """
    return format_success(f"Task {task_id} marked as incomplete")


def format_timestamp(dt: datetime) -> str:
    """Format datetime for display.

    Args:
        dt: The datetime to format.

    Returns:
        Formatted timestamp: YYYY-MM-DD HH:MM:SS
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_task_list_item(task: Task) -> str:
    """Format a single task for list display.

    Args:
        task: The task to format.

    Returns:
        Formatted task string for list view.
    """
    status = "[x]" if task.completed else "[ ]"
    lines = [f"[{task.id}] {status} {task.title}"]

    if task.description:
        lines.append(f"        {task.description}")

    lines.append(f"        Created: {format_timestamp(task.created_at)}")

    return "\n".join(lines)


def format_task_list(tasks: List[Task]) -> str:
    """Format all tasks for list display.

    Args:
        tasks: List of tasks to display.

    Returns:
        Formatted task list string, or "No tasks found." if empty.
    """
    if not tasks:
        return "No tasks found."

    formatted_tasks = [format_task_list_item(task) for task in tasks]
    return "Tasks:\n" + "\n\n".join(formatted_tasks)


def format_task_detail(task: Task) -> str:
    """Format a single task for detail view.

    Args:
        task: The task to format.

    Returns:
        Formatted task detail string.
    """
    status = "Complete" if task.completed else "Incomplete"
    lines = [
        f"Task {task.id}:",
        f"  Title: {task.title}",
        f"  Description: {task.description}",
        f"  Status: {status}",
        f"  Created: {format_timestamp(task.created_at)}"
    ]
    return "\n".join(lines)


def format_help() -> str:
    """Format help message.

    Returns:
        Help text showing all available commands.
    """
    return """Todo Application - Phase I

Commands:
  add <title> [description]       Create a new task
  list                            View all tasks
  view <id>                       View a single task
  complete <id>                   Mark task as complete
  uncomplete <id>                 Mark task as incomplete
  update <id> [options]           Update task attributes
    --title <text>                New title
    --description <text>          New description
  delete <id>                     Remove a task
  help                            Show this help message
  exit                            Exit the application"""


def format_goodbye() -> str:
    """Format goodbye message.

    Returns:
        Farewell message for application exit.
    """
    return "Goodbye!"
