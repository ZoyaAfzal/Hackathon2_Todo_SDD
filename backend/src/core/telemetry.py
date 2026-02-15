"""OpenTelemetry tracing instrumentation for FastAPI and SQLAlchemy.

Provides distributed tracing capabilities for monitoring and debugging.
"""

import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def setup_telemetry(
    service_name: str = "todo-api",
    environment: Optional[str] = None,
    otlp_endpoint: Optional[str] = None,
) -> TracerProvider:
    """Set up OpenTelemetry tracing.

    Configures the tracer provider with appropriate exporters based on
    the environment. In development, traces are logged to console.
    In production, traces are sent to an OTLP endpoint.

    Args:
        service_name: Name of the service for tracing
        environment: Current environment (development, production)
        otlp_endpoint: OTLP collector endpoint (optional)

    Returns:
        Configured TracerProvider
    """
    env = environment or os.getenv("ENVIRONMENT", "development")
    endpoint = otlp_endpoint or os.getenv("OTLP_ENDPOINT")

    # Create resource with service info
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.environment": env,
        }
    )

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Add exporters based on environment
    if endpoint:
        # Production: send to OTLP collector
        otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    else:
        # Development: log to console
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))

    # Set as global tracer provider
    trace.set_tracer_provider(provider)

    return provider


def instrument_fastapi(app) -> None:
    """Instrument a FastAPI application with OpenTelemetry.

    Automatically traces all incoming HTTP requests.

    Args:
        app: FastAPI application instance
    """
    FastAPIInstrumentor.instrument_app(app)


def instrument_sqlalchemy(engine) -> None:
    """Instrument SQLAlchemy with OpenTelemetry.

    Automatically traces all database queries.

    Args:
        engine: SQLAlchemy engine instance
    """
    SQLAlchemyInstrumentor().instrument(engine=engine)


def get_tracer(name: str = __name__) -> trace.Tracer:
    """Get a tracer for manual span creation.

    Args:
        name: Tracer name (usually module name)

    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)
