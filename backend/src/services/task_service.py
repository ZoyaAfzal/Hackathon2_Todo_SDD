"""Task service for CRUD operations on tasks.

Handles task creation, retrieval, listing, updates, completion, and deletion.
All operations are scoped to a specific user for isolation.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from src.models.task import Task


class TaskService:
    """Service for task management operations.

    All operations require a user_id to ensure task isolation.
    Tasks from other users are never returned or modified.
    """

    def __init__(self, session: Session):
        """Initialize task service with database session.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def create(
        self,
        user_id: uuid.UUID,
        title: str,
        description: Optional[str] = None,
    ) -> Task:
        """Create a new task for a user.

        Args:
            user_id: ID of the task owner
            title: Task title
            description: Optional task description

        Returns:
            Created task entity
        """
        now = datetime.utcnow()
        task = Task(
            id=uuid.uuid4(),
            title=title,
            description=description,
            completed=False,
            created_at=now,
            updated_at=now,
            version=1,
            user_id=user_id,
        )

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def get_by_id(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[Task]:
        """Get a task by ID, filtered by user.

        Returns None if task doesn't exist or belongs to another user.
        This prevents user enumeration attacks.

        Args:
            task_id: ID of the task to retrieve
            user_id: ID of the requesting user

        Returns:
            Task if found and owned by user, None otherwise
        """
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
        )
        return self.session.exec(statement).first()

    def list_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 20,
        after_id: Optional[uuid.UUID] = None,
    ) -> tuple[list[Task], bool, Optional[uuid.UUID]]:
        """List tasks for a user with cursor-based pagination.

        Tasks are ordered by created_at descending (newest first).

        Args:
            user_id: ID of the user whose tasks to list
            limit: Maximum number of tasks to return (default 20, max 100)
            after_id: Cursor for pagination (task ID to start after)

        Returns:
            Tuple of (tasks, has_more, next_cursor)
        """
        # Clamp limit
        limit = min(max(1, limit), 100)

        statement = select(Task).where(Task.user_id == user_id)

        # Apply cursor pagination
        if after_id:
            cursor_task = self.session.get(Task, after_id)
            if cursor_task:
                # Get tasks created before the cursor task
                # Using created_at for ordering with id as tiebreaker
                statement = statement.where(
                    (Task.created_at < cursor_task.created_at)
                    | (
                        (Task.created_at == cursor_task.created_at)
                        & (Task.id > after_id)
                    )
                )

        # Order by created_at descending, id ascending for stable sorting
        statement = statement.order_by(
            Task.created_at.desc(), Task.id
        ).limit(limit + 1)

        results = list(self.session.exec(statement).all())

        # Check if there are more results
        has_more = len(results) > limit
        tasks = results[:limit]

        # Get next cursor
        next_cursor = tasks[-1].id if has_more and tasks else None

        return tasks, has_more, next_cursor

    def update(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        expected_version: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> Optional[Task]:
        """Update a task with optimistic locking.

        Args:
            task_id: ID of the task to update
            user_id: ID of the requesting user
            expected_version: Version expected for optimistic locking
            title: New title (if provided)
            description: New description (if provided)
            completed: New completion status (if provided)

        Returns:
            Updated task if successful, None if not found

        Raises:
            ValueError: If version mismatch (optimistic lock conflict)
        """
        task = self.get_by_id(task_id, user_id)
        if not task:
            return None

        # Check version for optimistic locking
        if task.version != expected_version:
            raise ValueError("version_conflict")

        # Apply updates
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if completed is not None:
            task.completed = completed

        task.version += 1
        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def complete(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        expected_version: int,
    ) -> Optional[Task]:
        """Mark a task as complete.

        Args:
            task_id: ID of the task to complete
            user_id: ID of the requesting user
            expected_version: Version for optimistic locking

        Returns:
            Updated task if successful, None if not found

        Raises:
            ValueError: If version mismatch
        """
        return self.update(
            task_id=task_id,
            user_id=user_id,
            expected_version=expected_version,
            completed=True,
        )

    def uncomplete(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        expected_version: int,
    ) -> Optional[Task]:
        """Mark a task as incomplete.

        Args:
            task_id: ID of the task to uncomplete
            user_id: ID of the requesting user
            expected_version: Version for optimistic locking

        Returns:
            Updated task if successful, None if not found

        Raises:
            ValueError: If version mismatch
        """
        return self.update(
            task_id=task_id,
            user_id=user_id,
            expected_version=expected_version,
            completed=False,
        )

    def delete(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Permanently delete a task (hard delete).

        Args:
            task_id: ID of the task to delete
            user_id: ID of the requesting user

        Returns:
            True if deleted, False if not found
        """
        task = self.get_by_id(task_id, user_id)
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()

        return True


def get_task_service(session: Session) -> TaskService:
    """Factory function to create TaskService instance.

    Args:
        session: Database session

    Returns:
        TaskService instance
    """
    return TaskService(session)
