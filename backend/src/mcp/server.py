"""MCP server exposing todo task management tools.

This server runs as a stdio subprocess spawned by the OpenAI Agents SDK
via MCPServerStdio. It exposes 5 tools for task CRUD operations.

Usage:
    python -m src.mcp.server

Environment:
    DATABASE_URL: PostgreSQL connection string
    MCP_USER_ID: UUID of the authenticated user (set by ChatService)
"""

import json
import os
import sys
import uuid
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("Todo Task Manager")


def _get_user_id() -> uuid.UUID:
    """Get the current user ID from environment variable."""
    user_id_str = os.environ.get("MCP_USER_ID", "")
    if not user_id_str:
        raise ValueError("MCP_USER_ID environment variable not set")
    return uuid.UUID(user_id_str)


def _get_db_session():
    """Create a database session for tool operations."""
    from sqlmodel import Session, create_engine

    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    engine = create_engine(database_url, pool_pre_ping=True)
    return Session(engine)


def _task_to_dict(task) -> dict:
    """Convert a Task object to a serializable dictionary."""
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "version": task.version,
    }


@mcp.tool()
def add_task(title: str, description: str = "") -> str:
    """Create a new todo task for the user.

    Args:
        title: The task title (required)
        description: Optional task description
    """
    from src.services.task_service import TaskService

    user_id = _get_user_id()
    session = _get_db_session()
    try:
        service = TaskService(session)
        task = service.create(
            user_id=user_id,
            title=title,
            description=description or None,
        )
        return json.dumps({
            "status": "success",
            "message": f"Task '{task.title}' created successfully.",
            "task": _task_to_dict(task),
        })
    finally:
        session.close()


@mcp.tool()
def list_tasks(filter: str = "all") -> str:
    """List the user's todo tasks.

    Args:
        filter: Filter tasks by status. Options: "all", "pending", "completed"
    """
    from src.services.task_service import TaskService

    user_id = _get_user_id()
    session = _get_db_session()
    try:
        service = TaskService(session)
        tasks, _, _ = service.list_by_user(user_id=user_id, limit=100)

        if filter == "pending":
            tasks = [t for t in tasks if not t.completed]
        elif filter == "completed":
            tasks = [t for t in tasks if t.completed]

        return json.dumps({
            "status": "success",
            "count": len(tasks),
            "tasks": [_task_to_dict(t) for t in tasks],
        })
    finally:
        session.close()


@mcp.tool()
def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """Update an existing task's title or description.

    Args:
        task_id: The UUID of the task to update
        title: New title (if changing)
        description: New description (if changing)
    """
    from src.services.task_service import TaskService

    user_id = _get_user_id()
    session = _get_db_session()
    try:
        service = TaskService(session)
        task_uuid = uuid.UUID(task_id)

        # Get current version for optimistic locking
        existing = service.get_by_id(task_uuid, user_id)
        if not existing:
            return json.dumps({
                "status": "error",
                "message": f"Task with ID {task_id} not found.",
            })

        task = service.update(
            task_id=task_uuid,
            user_id=user_id,
            expected_version=existing.version,
            title=title,
            description=description,
        )
        if not task:
            return json.dumps({
                "status": "error",
                "message": f"Task with ID {task_id} not found.",
            })

        return json.dumps({
            "status": "success",
            "message": f"Task '{task.title}' updated successfully.",
            "task": _task_to_dict(task),
        })
    except ValueError as e:
        if str(e) == "version_conflict":
            return json.dumps({
                "status": "error",
                "message": "Task was modified by another request. Please retry.",
            })
        return json.dumps({
            "status": "error",
            "message": f"Invalid task ID: {task_id}",
        })
    finally:
        session.close()


@mcp.tool()
def complete_task(task_id: str) -> str:
    """Mark a task as completed.

    Args:
        task_id: The UUID of the task to complete
    """
    from src.services.task_service import TaskService

    user_id = _get_user_id()
    session = _get_db_session()
    try:
        service = TaskService(session)
        task_uuid = uuid.UUID(task_id)

        existing = service.get_by_id(task_uuid, user_id)
        if not existing:
            return json.dumps({
                "status": "error",
                "message": f"Task with ID {task_id} not found.",
            })

        if existing.completed:
            return json.dumps({
                "status": "info",
                "message": f"Task '{existing.title}' is already completed.",
                "task": _task_to_dict(existing),
            })

        task = service.complete(
            task_id=task_uuid,
            user_id=user_id,
            expected_version=existing.version,
        )
        return json.dumps({
            "status": "success",
            "message": f"Task '{task.title}' marked as completed.",
            "task": _task_to_dict(task),
        })
    except ValueError:
        return json.dumps({
            "status": "error",
            "message": f"Invalid task ID: {task_id}",
        })
    finally:
        session.close()


@mcp.tool()
def delete_task(task_id: str) -> str:
    """Delete a task permanently.

    Args:
        task_id: The UUID of the task to delete
    """
    from src.services.task_service import TaskService

    user_id = _get_user_id()
    session = _get_db_session()
    try:
        service = TaskService(session)
        task_uuid = uuid.UUID(task_id)

        existing = service.get_by_id(task_uuid, user_id)
        if not existing:
            return json.dumps({
                "status": "error",
                "message": f"Task with ID {task_id} not found.",
            })

        task_title = existing.title
        deleted = service.delete(task_uuid, user_id)
        if deleted:
            return json.dumps({
                "status": "success",
                "message": f"Task '{task_title}' deleted successfully.",
            })
        return json.dumps({
            "status": "error",
            "message": f"Failed to delete task with ID {task_id}.",
        })
    except ValueError:
        return json.dumps({
            "status": "error",
            "message": f"Invalid task ID: {task_id}",
        })
    finally:
        session.close()


def main():
    """Run the MCP server via stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
