"""
TaskStore - StateManagementAgent implementation per data-model.md.

Owns all in-memory state for the application. The TaskStore is the single
source of truth for task data. All state reads and writes MUST go through
this component.
"""

from typing import Dict, List, Optional

from src.models.task import Task
from src.exceptions import TaskNotFoundError, EmptyTitleError


class TaskStore:
    """
    In-memory storage for tasks (StateManagementAgent implementation).

    Invariants:
        - tasks dict keys MUST match their Task.id
        - next_id MUST be greater than all existing task IDs
        - tasks MUST be empty on initialization
        - No duplicate IDs permitted

    Phase I Constraints:
        - State resides in memory only
        - State is lost on application exit
        - Single-threaded access only
    """

    def __init__(self) -> None:
        """Initialize empty TaskStore.

        State is initialized to empty per Constitution Principle IV.
        """
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """Add a new task to the store.

        Args:
            title: Task title (required, non-empty).
            description: Task description (optional).

        Returns:
            The created Task with auto-generated ID.

        Raises:
            EmptyTitleError: If title is empty or whitespace-only.
        """
        # Validation happens in Task.__post_init__
        task = Task(
            id=self._next_id,
            title=title,
            description=description
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id: int) -> Task:
        """Get a task by ID.

        Args:
            task_id: The task identifier.

        Returns:
            The Task with the specified ID.

        Raises:
            TaskNotFoundError: If no task with the ID exists.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        return self._tasks[task_id]

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks in the store.

        Returns:
            List of all tasks, ordered by ID (insertion order).
        """
        return list(self._tasks.values())

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
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        task = self._tasks[task_id]

        if title is not None:
            stripped_title = title.strip()
            if not stripped_title:
                raise EmptyTitleError()
            task.title = stripped_title

        if description is not None:
            task.description = description.strip()

        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task from the store.

        Args:
            task_id: The task identifier.

        Returns:
            True if deletion was successful.

        Raises:
            TaskNotFoundError: If no task with the ID exists.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        del self._tasks[task_id]
        return True

    def complete_task(self, task_id: int) -> Task:
        """Mark a task as complete.

        Args:
            task_id: The task identifier.

        Returns:
            The updated Task.

        Raises:
            TaskNotFoundError: If no task with the ID exists.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        task = self._tasks[task_id]
        task.completed = True
        return task

    def uncomplete_task(self, task_id: int) -> Task:
        """Mark a task as incomplete.

        Args:
            task_id: The task identifier.

        Returns:
            The updated Task.

        Raises:
            TaskNotFoundError: If no task with the ID exists.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        task = self._tasks[task_id]
        task.completed = False
        return task

    def task_exists(self, task_id: int) -> bool:
        """Check if a task exists.

        Args:
            task_id: The task identifier.

        Returns:
            True if task exists, False otherwise.
        """
        return task_id in self._tasks
