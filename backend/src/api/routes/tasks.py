"""Task management routes.

Provides endpoints for task CRUD operations:
- GET /api/v1/tasks - List tasks with pagination
- GET /api/v1/tasks/{task_id} - Get task by ID
- POST /api/v1/tasks - Create task
- PUT /api/v1/tasks/{task_id} - Update task
- POST /api/v1/tasks/{task_id}/complete - Mark task complete
- POST /api/v1/tasks/{task_id}/uncomplete - Mark task incomplete
- DELETE /api/v1/tasks/{task_id} - Delete task
"""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from src.api.deps.auth import CurrentUser
from src.api.deps.database import get_session
from src.api.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
    VersionRequest,
)
from src.services.task_service import TaskService, get_task_service

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


def get_task_service_dep(
    session: Annotated[Session, Depends(get_session)],
) -> TaskService:
    """Dependency to get task service with session."""
    return get_task_service(session)


@router.get(
    "",
    response_model=TaskListResponse,
    responses={
        200: {"description": "List of tasks"},
        401: {"description": "Unauthorized"},
    },
)
async def list_tasks(
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends(get_task_service_dep)],
    limit: int = Query(default=20, ge=1, le=100, description="Number of tasks"),
    after_id: Optional[uuid.UUID] = Query(
        default=None, description="Cursor for pagination"
    ),
) -> TaskListResponse:
    """List all tasks for the authenticated user.

    Supports cursor-based pagination with limit and after_id parameters.
    Tasks are returned in descending order by creation date.

    Args:
        current_user: Authenticated user from JWT
        task_service: Task service instance
        limit: Maximum number of tasks to return (1-100, default 20)
        after_id: Task ID to start after for pagination

    Returns:
        TaskListResponse with tasks, has_more flag, and next cursor
    """
    tasks, has_more, next_cursor = task_service.list_by_user(
        user_id=current_user.user_id,
        limit=limit,
        after_id=after_id,
    )

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        has_more=has_more,
        next_cursor=next_cursor,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        200: {"description": "Task details"},
        401: {"description": "Unauthorized"},
        404: {"description": "Task not found"},
    },
)
async def get_task(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends(get_task_service_dep)],
) -> TaskResponse:
    """Get a task by ID.

    Returns 404 if task doesn't exist or belongs to another user.

    Args:
        task_id: UUID of the task to retrieve
        current_user: Authenticated user from JWT
        task_service: Task service instance

    Returns:
        Task details

    Raises:
        HTTPException 404: Task not found or not owned by user
    """
    task = task_service.get_by_id(task_id, current_user.user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "not_found",
                    "message": "Task not found",
                    "details": {},
                }
            },
        )

    return TaskResponse.model_validate(task)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Task created"},
        400: {"description": "Validation error"},
        401: {"description": "Unauthorized"},
    },
)
async def create_task(
    task_data: TaskCreate,
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends(get_task_service_dep)],
) -> TaskResponse:
    """Create a new task.

    Args:
        task_data: Task creation data (title, description)
        current_user: Authenticated user from JWT
        task_service: Task service instance

    Returns:
        Created task

    Raises:
        HTTPException 400: Validation error
    """
    task = task_service.create(
        user_id=current_user.user_id,
        title=task_data.title,
        description=task_data.description,
    )

    return TaskResponse.model_validate(task)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        200: {"description": "Task updated"},
        400: {"description": "Validation error"},
        401: {"description": "Unauthorized"},
        404: {"description": "Task not found"},
        409: {"description": "Version conflict"},
    },
)
async def update_task(
    task_id: uuid.UUID,
    task_data: TaskUpdate,
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends(get_task_service_dep)],
) -> TaskResponse:
    """Update an existing task.

    Requires version field for optimistic locking.

    Args:
        task_id: UUID of the task to update
        task_data: Update data with version
        current_user: Authenticated user from JWT
        task_service: Task service instance

    Returns:
        Updated task

    Raises:
        HTTPException 404: Task not found
        HTTPException 409: Version conflict
    """
    try:
        task = task_service.update(
            task_id=task_id,
            user_id=current_user.user_id,
            expected_version=task_data.version,
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
        )
    except ValueError as e:
        if str(e) == "version_conflict":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "conflict",
                        "message": "Task was modified by another request",
                        "details": {},
                    }
                },
            )
        raise

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "not_found",
                    "message": "Task not found",
                    "details": {},
                }
            },
        )

    return TaskResponse.model_validate(task)


@router.post(
    "/{task_id}/complete",
    response_model=TaskResponse,
    responses={
        200: {"description": "Task marked complete"},
        400: {"description": "Validation error"},
        401: {"description": "Unauthorized"},
        404: {"description": "Task not found"},
        409: {"description": "Version conflict"},
    },
)
async def complete_task(
    task_id: uuid.UUID,
    version_data: VersionRequest,
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends(get_task_service_dep)],
) -> TaskResponse:
    """Mark a task as complete.

    Args:
        task_id: UUID of the task
        version_data: Version for optimistic locking
        current_user: Authenticated user from JWT
        task_service: Task service instance

    Returns:
        Updated task

    Raises:
        HTTPException 404: Task not found
        HTTPException 409: Version conflict
    """
    try:
        task = task_service.complete(
            task_id=task_id,
            user_id=current_user.user_id,
            expected_version=version_data.version,
        )
    except ValueError as e:
        if str(e) == "version_conflict":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "conflict",
                        "message": "Task was modified by another request",
                        "details": {},
                    }
                },
            )
        raise

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "not_found",
                    "message": "Task not found",
                    "details": {},
                }
            },
        )

    return TaskResponse.model_validate(task)


@router.post(
    "/{task_id}/uncomplete",
    response_model=TaskResponse,
    responses={
        200: {"description": "Task marked incomplete"},
        400: {"description": "Validation error"},
        401: {"description": "Unauthorized"},
        404: {"description": "Task not found"},
        409: {"description": "Version conflict"},
    },
)
async def uncomplete_task(
    task_id: uuid.UUID,
    version_data: VersionRequest,
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends(get_task_service_dep)],
) -> TaskResponse:
    """Mark a task as incomplete.

    Args:
        task_id: UUID of the task
        version_data: Version for optimistic locking
        current_user: Authenticated user from JWT
        task_service: Task service instance

    Returns:
        Updated task

    Raises:
        HTTPException 404: Task not found
        HTTPException 409: Version conflict
    """
    try:
        task = task_service.uncomplete(
            task_id=task_id,
            user_id=current_user.user_id,
            expected_version=version_data.version,
        )
    except ValueError as e:
        if str(e) == "version_conflict":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "conflict",
                        "message": "Task was modified by another request",
                        "details": {},
                    }
                },
            )
        raise

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "not_found",
                    "message": "Task not found",
                    "details": {},
                }
            },
        )

    return TaskResponse.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Task deleted"},
        401: {"description": "Unauthorized"},
        404: {"description": "Task not found"},
    },
)
async def delete_task(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends(get_task_service_dep)],
) -> None:
    """Permanently delete a task.

    Args:
        task_id: UUID of the task to delete
        current_user: Authenticated user from JWT
        task_service: Task service instance

    Raises:
        HTTPException 404: Task not found
    """
    deleted = task_service.delete(task_id, current_user.user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "not_found",
                    "message": "Task not found",
                    "details": {},
                }
            },
        )
