"""Configuration module loading environment variables."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load .env file if present
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://localhost/todo",
        description="PostgreSQL connection string",
    )

    # Authentication
    BETTER_AUTH_SECRET: str = Field(
        default="change-me-in-production-minimum-32-chars",
        description="Shared secret for JWT signing/verification",
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_EXPIRATION_HOURS: int = Field(
        default=24, description="JWT token expiration in hours"
    )

    # AI / OpenAI
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key for Agents SDK",
    )
    OPENAI_MODEL: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model for chat agent",
    )

    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
            "https://zoya-todo-fullstack.vercel.app",
            "https://frontend-eosin-xi-26.vercel.app",
        ],
        description="Allowed CORS origins",
    )

    # OpenTelemetry
    OTEL_SERVICE_NAME: str = Field(default="todo-api", description="OTel service name")
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = Field(
        default=None, description="OTel OTLP endpoint"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
