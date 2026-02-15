"""Custom metrics for authentication and request monitoring.

Provides Prometheus-compatible metrics for:
- Authentication events (login, register, logout)
- Request latency and counts
- Task operations
"""

import time
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Generator

from prometheus_client import Counter, Histogram, Info

# Service info metric
SERVICE_INFO = Info("todo_api", "Todo API service information")
SERVICE_INFO.info({"version": "1.0.0", "name": "todo-api"})

# Authentication metrics
AUTH_REQUESTS = Counter(
    "auth_requests_total",
    "Total authentication requests",
    ["operation", "status"],
)

AUTH_FAILURES = Counter(
    "auth_failures_total",
    "Total authentication failures",
    ["operation", "reason"],
)

# Request metrics
REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint", "status"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

REQUEST_COUNT = Counter(
    "requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

# Task operation metrics
TASK_OPERATIONS = Counter(
    "task_operations_total",
    "Total task operations",
    ["operation", "status"],
)


def record_auth_event(operation: str, success: bool, reason: str = "") -> None:
    """Record an authentication event.

    Args:
        operation: Type of auth operation (login, register, logout)
        success: Whether the operation succeeded
        reason: Failure reason if unsuccessful
    """
    status = "success" if success else "failure"
    AUTH_REQUESTS.labels(operation=operation, status=status).inc()

    if not success and reason:
        AUTH_FAILURES.labels(operation=operation, reason=reason).inc()


def record_request(
    method: str,
    endpoint: str,
    status_code: int,
    latency: float,
) -> None:
    """Record an HTTP request.

    Args:
        method: HTTP method
        endpoint: Request endpoint path
        status_code: Response status code
        latency: Request latency in seconds
    """
    status = str(status_code)
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint, status=status).observe(
        latency
    )


def record_task_operation(operation: str, success: bool) -> None:
    """Record a task operation.

    Args:
        operation: Type of operation (create, update, delete, complete)
        success: Whether the operation succeeded
    """
    status = "success" if success else "failure"
    TASK_OPERATIONS.labels(operation=operation, status=status).inc()


@contextmanager
def track_request_latency(
    method: str, endpoint: str
) -> Generator[None, None, None]:
    """Context manager to track request latency.

    Args:
        method: HTTP method
        endpoint: Request endpoint path

    Yields:
        None
    """
    start_time = time.perf_counter()
    status_code = 200  # Default, will be updated
    try:
        yield
    except Exception:
        status_code = 500
        raise
    finally:
        latency = time.perf_counter() - start_time
        record_request(method, endpoint, status_code, latency)


def metrics_middleware(app):
    """FastAPI middleware for automatic request metrics.

    Note: This is a simple middleware. For production, consider
    using starlette-prometheus or similar libraries.

    Args:
        app: FastAPI application
    """
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import Response

    class MetricsMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next) -> Response:
            start_time = time.perf_counter()
            response = await call_next(request)
            latency = time.perf_counter() - start_time

            record_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                latency=latency,
            )

            return response

    app.add_middleware(MetricsMiddleware)
