"""Error response schemas for consistent API error formatting."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Structured error details.

    Attributes:
        code: Machine-readable error code (e.g., 'validation_error', 'not_found')
        message: Human-readable error message
        details: Additional error details (e.g., field-level validation errors)
    """

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "validation_error",
                    "message": "Request validation failed",
                    "details": {"title": ["Title is required"]},
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response wrapper.

    All API errors follow this format for consistency.

    Attributes:
        error: Structured error details
    """

    error: ErrorDetail

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": {
                        "code": "not_found",
                        "message": "Task not found",
                        "details": None,
                    }
                }
            ]
        }
    }
