import functools
import logging
from typing import Any, Callable, Optional

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio

logger = logging.getLogger(__name__)


def setup_telemetry(
    app: FastAPI,
    service_name: str,
    service_version: str = "1.0.0",
    otel_endpoint: Optional[str] = None,
    environment: str = "development",
    sample_rate: float = 1.0,
) -> None:
    """
    Sets up Enterprise-grade OpenTelemetry tracing for the FastAPI application.
    Implements Milestone 10.2.1: Distributed Request Tracing.
    """
    try:
        resource = Resource(
            attributes={
                SERVICE_NAME: service_name,
                SERVICE_VERSION: service_version,
                "deployment.environment": environment,
            }
        )

        # Sampling: Always sample in dev/test, use ratio in production if needed
        sampler = ParentBasedTraceIdRatio(sample_rate)
        provider = TracerProvider(resource=resource, sampler=sampler)

        if otel_endpoint:
            # OTLP Exporter for production (e.g., Jaeger, Tempo, Honeycomb)
            exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)
        elif environment == "development":
            # Console Exporter for local debugging
            console_exporter = ConsoleSpanExporter()
            processor = BatchSpanProcessor(console_exporter)
            provider.add_span_processor(processor)

        trace.set_tracer_provider(provider)

        # 1. Instrument FastAPI
        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=provider,
            excluded_urls="health,metrics,version",
        )

        # 2. Instrument HTTP Clients (for LLM API calls and external services)
        HTTPXClientInstrumentor().instrument()

        # 3. Instrument Redis (for caching and rate limiting)
        RedisInstrumentor().instrument()

        logger.info(
            f"OpenTelemetry initialized for {service_name} (env: {environment}, endpoint: {otel_endpoint})"
        )

    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}", exc_info=True)


def get_tracer(name: str):
    """
    Returns a tracer for the given name.
    """
    return trace.get_tracer(name)


def traced(span_name: Optional[str] = None, attributes: Optional[dict] = None):
    """
    Decorator for automatic span creation and error recording.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = span_name or func.__name__
            tracer = trace.get_tracer(func.__module__)
            with tracer.start_as_current_span(name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = span_name or func.__name__
            tracer = trace.get_tracer(func.__module__)
            with tracer.start_as_current_span(name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise

        return async_wrapper if functools.iscoroutinefunction(func) else wrapper

    return decorator
