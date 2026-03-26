"""Structured JSON logging configuration.

Provides consistent, parseable logging for the application.
"""

import logging
import sys
from datetime import datetime
from typing import Any, Optional

import json


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging.

    Outputs log records as JSON objects with consistent fields.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "operation"):
            log_data["operation"] = record.operation

        # Add any extra attributes from the record
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "created",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "request_id",
                "user_id",
                "operation",
            ):
                if not key.startswith("_"):
                    log_data[key] = value

        return json.dumps(log_data)


def setup_logging(
    level: str = "INFO",
    json_format: bool = True,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Set up application logging.

    Configures the root logger with appropriate handlers and formatters.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON formatting
        log_file: Optional file path for file logging

    Returns:
        Configured root logger
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding extra fields to log records.

    Example:
        with LogContext(request_id="abc123", user_id="user1"):
            logger.info("Processing request")
    """

    def __init__(self, **kwargs: Any):
        """Initialize with extra fields.

        Args:
            **kwargs: Extra fields to add to log records
        """
        self.extra = kwargs
        self._old_factory = None

    def __enter__(self) -> "LogContext":
        """Enter the context, adding extra fields to records."""
        self._old_factory = logging.getLogRecordFactory()

        extra = self.extra

        def record_factory(*args, **kwargs):
            record = self._old_factory(*args, **kwargs)
            for key, value in extra.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, *args) -> None:
        """Exit the context, restoring the original factory."""
        if self._old_factory:
            logging.setLogRecordFactory(self._old_factory)
