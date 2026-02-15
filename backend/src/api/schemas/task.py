"""Pydantic schemas for task endpoints.

Defines request and response schemas for task CRUD operations.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for task creation request.

    Attributes:
        title: Task title (required, 1-255 characters)
        description: Optional task description
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Task title (required)",
        json_schema_extra={"example": "Buy groceries"},
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional task description",
        json_schema_extra={"example": "Milk, eggs, bread"},
    )


class TaskUpdate(BaseModel):
    """Schema for task update request.

    All fields are optional except version for optimistic locking.

    Attributes:
        title: New task title (1-255 characters)
        description: New task description
        completed: New completion status
        version: Expected version for optimistic locking (required)
    """

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New task title",
    )
    description: Optional[str] = Field(
        default=None,
        description="New task description",
    )
    completed: Optional[bool] = Field(
        default=None,
        description="New completion status",
    )
    version: int = Field(
        ...,
        description="Expected version for optimistic locking",
        json_schema_extra={"example": 1},
    )


class VersionRequest(BaseModel):
    """Schema for complete/uncomplete requests.

    Requires version for optimistic locking.

    Attributes:
        version: Expected version for optimistic locking
    """

    version: int = Field(
        ...,
        description="Expected version for optimistic locking",
        json_schema_extra={"example": 1},
    )


class TaskResponse(BaseModel):
    """Schema for task response.

    Attributes:
        id: Task's unique identifier
        title: Task title
        description: Task description (may be null)
        completed: Completion status
        created_at: When the task was created
        updated_at: When the task was last modified
        version: Current version for optimistic locking
    """

    id: uuid.UUID = Field(..., description="Task's unique identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(..., description="Completion status")
    created_at: datetime = Field(..., description="When the task was created")
    updated_at: datetime = Field(..., description="When the task was last modified")
    version: int = Field(..., description="Version for optimistic locking")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-01-07T10:00:00Z",
                "updated_at": "2026-01-07T10:00:00Z",
                "version": 1,
            }
        },
    }


class TaskListResponse(BaseModel):
    """Schema for task list response with pagination.

    Attributes:
        tasks: List of tasks
        has_more: Whether there are more tasks to fetch
        next_cursor: Cursor for next page (task ID)
    """

    tasks: list[TaskResponse] = Field(..., description="List of tasks")
    has_more: bool = Field(..., description="Whether there are more tasks")
    next_cursor: Optional[uuid.UUID] = Field(
        None, description="Cursor for next page"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "tasks": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "created_at": "2026-01-07T10:00:00Z",
                        "updated_at": "2026-01-07T10:00:00Z",
                        "version": 1,
                    }
                ],
                "has_more": True,
                "next_cursor": "123e4567-e89b-12d3-a456-426614174001",
            }
        },
    }
