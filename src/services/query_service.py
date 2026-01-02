"""
QueryService - TaskQuerySkill implementation per spec.md.

Handles all task retrieval operations. This skill is stateless and
delegates all state reads to the StateManagementAgent (TaskStore).
"""

from typing import List

from src.models.task import Task
from src.state.store import TaskStore


class QueryService:
    """
    Task query operations (TaskQuerySkill implementation).

    Constraints:
        - Skill MUST be stateless (uses injected store)
        - Skill MUST request state reads from TaskStore
        - Skill MUST NOT modify any state
    """

    def __init__(self, store: TaskStore) -> None:
        """Initialize QueryService with a TaskStore.

        Args:
            store: The TaskStore instance for state reads.
        """
        self._store = store

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks.

        Returns:
            List of all tasks in the store.
        """
        return self._store.get_all_tasks()

    def get_task(self, task_id: int) -> Task:
        """Get a task by ID.

        Args:
            task_id: The task identifier.

        Returns:
            The Task with the specified ID.

        Raises:
            TaskNotFoundError: If no task with the ID exists.
        """
        return self._store.get_task(task_id)

    def task_exists(self, task_id: int) -> bool:
        """Check if a task exists.

        Args:
            task_id: The task identifier.

        Returns:
            True if task exists, False otherwise.
        """
        return self._store.task_exists(task_id)
