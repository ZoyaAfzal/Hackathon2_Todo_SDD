"""Global exception handlers for consistent error responses."""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .schemas.error import ErrorDetail, ErrorResponse


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent error format.

    Args:
        request: The incoming request
        exc: The HTTP exception raised

    Returns:
        JSONResponse with ErrorResponse format
    """
    # Map status codes to error codes
    status_to_code = {
        status.HTTP_400_BAD_REQUEST: "bad_request",
        status.HTTP_401_UNAUTHORIZED: "unauthorized",
        status.HTTP_403_FORBIDDEN: "forbidden",
        status.HTTP_404_NOT_FOUND: "not_found",
        status.HTTP_409_CONFLICT: "conflict",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "validation_error",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "internal_error",
    }

    error_code = status_to_code.get(exc.status_code, "error")

    error_response = ErrorResponse(
        error=ErrorDetail(
            code=error_code,
            message=str(exc.detail),
            details=None,
        )
    )

    headers = getattr(exc, "headers", None)

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
        headers=headers,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors with detailed field information.

    Args:
        request: The incoming request
        exc: The validation exception

    Returns:
        JSONResponse with field-level validation details
    """
    # Group errors by field
    field_errors: dict[str, list[str]] = {}
    for error in exc.errors():
        # Get field name from location (body -> field_name)
        loc = error.get("loc", ())
        if len(loc) > 1:
            field_name = str(loc[-1])
        else:
            field_name = "body"

        message = error.get("msg", "Validation error")

        if field_name not in field_errors:
            field_errors[field_name] = []
        field_errors[field_name].append(message)

    error_response = ErrorResponse(
        error=ErrorDetail(
            code="validation_error",
            message="Request validation failed",
            details=field_errors,
        )
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response.model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions without exposing internal details.

    Args:
        request: The incoming request
        exc: The unexpected exception

    Returns:
        JSONResponse with generic error message
    """
    # Log the actual error for debugging (would use proper logging in production)
    # logger.error(f"Unexpected error: {exc}", exc_info=True)

    error_response = ErrorResponse(
        error=ErrorDetail(
            code="internal_error",
            message="An unexpected error occurred",
            details=None,
        )
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    # Uncomment to catch all unexpected errors (useful in production)
    # app.add_exception_handler(Exception, general_exception_handler)
