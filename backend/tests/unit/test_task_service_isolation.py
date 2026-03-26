"""Unit tests for task service user filtering.

Tests that task_service properly filters tasks by user_id.
"""

import uuid
from datetime import datetime

import pytest
from sqlmodel import Session

from src.models.task import Task
from src.models.user import User
from src.services.task_service import TaskService


class TestTaskServiceUserFiltering:
    """Test task service user_id filtering."""

    def test_get_by_id_with_wrong_user_returns_none(
        self, session: Session, test_user: User, another_user: User
    ):
        """get_by_id with wrong user_id returns None."""
        # Create a task for test_user
        task = Task(
            id=uuid.uuid4(),
            title="Test User's Task",
            user_id=test_user.id,
        )
        session.add(task)
        session.commit()

        # Try to get it as another_user
        service = TaskService(session)
        result = service.get_by_id(task.id, another_user.id)

        assert result is None

    def test_get_by_id_with_correct_user_returns_task(
        self, session: Session, test_user: User
    ):
        """get_by_id with correct user_id returns the task."""
        task = Task(
            id=uuid.uuid4(),
            title="Test User's Task",
            user_id=test_user.id,
        )
        session.add(task)
        session.commit()

        service = TaskService(session)
        result = service.get_by_id(task.id, test_user.id)

        assert result is not None
        assert result.id == task.id

    def test_list_by_user_only_returns_user_tasks(
        self, session: Session, test_user: User, another_user: User
    ):
        """list_by_user only returns tasks for that user."""
        # Create tasks for both users
        for i in range(3):
            task1 = Task(
                id=uuid.uuid4(),
                title=f"User1 Task {i}",
                user_id=test_user.id,
            )
            task2 = Task(
                id=uuid.uuid4(),
                title=f"User2 Task {i}",
                user_id=another_user.id,
            )
            session.add(task1)
            session.add(task2)
        session.commit()

        service = TaskService(session)

        # List user1's tasks
        user1_tasks, _, _ = service.list_by_user(test_user.id)
        user1_task_ids = [str(t.user_id) for t in user1_tasks]

        # All tasks should belong to user1
        for uid in user1_task_ids:
            assert uid == str(test_user.id)

        # List user2's tasks
        user2_tasks, _, _ = service.list_by_user(another_user.id)
        user2_task_ids = [str(t.user_id) for t in user2_tasks]

        # All tasks should belong to user2
        for uid in user2_task_ids:
            assert uid == str(another_user.id)

    def test_update_with_wrong_user_returns_none(
        self, session: Session, test_user: User, another_user: User
    ):
        """update with wrong user_id returns None."""
        task = Task(
            id=uuid.uuid4(),
            title="Original Title",
            user_id=test_user.id,
            version=1,
        )
        session.add(task)
        session.commit()

        service = TaskService(session)
        result = service.update(
            task_id=task.id,
            user_id=another_user.id,
            expected_version=1,
            title="Hacked Title",
        )

        assert result is None

        # Original task should be unchanged
        session.refresh(task)
        assert task.title == "Original Title"

    def test_delete_with_wrong_user_returns_false(
        self, session: Session, test_user: User, another_user: User
    ):
        """delete with wrong user_id returns False."""
        task = Task(
            id=uuid.uuid4(),
            title="Protected Task",
            user_id=test_user.id,
        )
        session.add(task)
        session.commit()

        service = TaskService(session)
        result = service.delete(task.id, another_user.id)

        assert result is False

        # Task should still exist
        assert session.get(Task, task.id) is not None

    def test_complete_with_wrong_user_returns_none(
        self, session: Session, test_user: User, another_user: User
    ):
        """complete with wrong user_id returns None."""
        task = Task(
            id=uuid.uuid4(),
            title="Incomplete Task",
            completed=False,
            user_id=test_user.id,
            version=1,
        )
        session.add(task)
        session.commit()

        service = TaskService(session)
        result = service.complete(
            task_id=task.id,
            user_id=another_user.id,
            expected_version=1,
        )

        assert result is None

        # Task should still be incomplete
        session.refresh(task)
        assert task.completed is False

    def test_create_assigns_correct_user_id(
        self, session: Session, test_user: User
    ):
        """create assigns the task to the correct user."""
        service = TaskService(session)
        task = service.create(
            user_id=test_user.id,
            title="New Task",
        )

        assert task.user_id == test_user.id
