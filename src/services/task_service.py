"""
TaskService - TaskManagementSkill implementation per spec.md.

Handles all task lifecycle operations. This skill is stateless and
delegates all state changes to the StateManagementAgent (TaskStore).
"""

from typing import Optional

from src.models.task import Task
from src.state.store import TaskStore


class TaskService:
    """
    Task management operations (TaskManagementSkill implementation).

    Constraints:
        - Skill MUST be stateless (uses injected store)
        - Skill MUST delegate state changes to TaskStore
        - Skill MUST validate inputs before requesting state changes
    """

    def __init__(self, store: TaskStore) -> None:
        """Initialize TaskService with a TaskStore.

        Args:
            store: The TaskStore instance for state management.
        """
        self._store = store

    def create_task(self, title: str, description: str = "") -> Task:
        """Create a new task.

        Args:
            title: Task title (required, non-empty).
            description: Task description (optional).

        Returns:
            The created Task with auto-generated ID.

        Raises:
            EmptyTitleError: If title is empty or whitespace-only.
        """
        return self._store.add_task(title, description)

    def complete_task(self, task_id: int) -> Task:
        """Mark a task as complete.

        Args:
            task_id: The task identifier.

        Returns:
            The updated Task.

        Raises:
            TaskNotFoundError: If no task with the ID exists.
        """
        return self._store.complete_task(task_id)

    def uncomplete_task(self, task_id: int) -> Task:
        """Mark a task as incomplete.

        Args:
            task_id: The task identifier.

        Returns:
            The updated Task.

        Raises:
            TaskNotFoundError: If no task with the ID exists.
        """
        return self._store.uncomplete_task(task_id)

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Task:
        """Update task attributes.

        Args:
            task_id: The task identifier.
            title: New title (optional, must be non-empty if provided).
            description: New description (optional).

        Returns:
            The updated Task.

        Raises:
            TaskNotFoundError: If no task with the ID exists.
            EmptyTitleError: If new title is empty or whitespace-only.
        """
        return self._store.update_task(task_id, title, description)

    def delete_task(self, task_id: int) -> bool:
        """Delete a task.

        Args:
            task_id: The task identifier.

        Returns:
            True if deletion was successful.

        Raises:
            TaskNotFoundError: If no task with the ID exists.
        """
        return self._store.delete_task(task_id)
