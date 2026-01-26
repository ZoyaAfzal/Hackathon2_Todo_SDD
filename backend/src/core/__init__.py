"""Core module for configuration, database, and shared utilities."""

from .config import settings
from .database import engine, get_session

__all__ = ["settings", "engine", "get_session"]
