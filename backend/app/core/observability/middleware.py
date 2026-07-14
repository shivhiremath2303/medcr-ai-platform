import cProfile
import io
import logging
import pstats
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

try:
    from opentelemetry import trace
    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False

from app import di
from app.core.config import get_settings
from app.core.observability.context import set_correlation_id, set_request_id
from app.core.observability.logger import get_logger
from app.core.observability.profiler import PerformanceProfiler

logger = get_logger(__name__)
settings = get_settings()


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Enterprise Observability Middleware.
    Handles Correlation IDs, Request IDs, Trace Context, Performance Profiling, and API Analytics.
    Implements Milestones 10.2.1, 10.2.3, 10.2.8, and 10.2.9.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        start_mem = PerformanceProfiler.get_memory_usage_mb()

        # Get metrics registry from DI
        metrics = di.get_metrics_registry()

        # 1. Extract or generate Correlation ID
        correlation_id = (
            request.headers.get("X-Correlation-ID")
            or request.headers.get("X-Trace-ID")
            or str(uuid.uuid4())
        )
        set_correlation_id(correlation_id)

        # 2. Generate unique Request ID
        request_id = str(uuid.uuid4())
        set_request_id(request_id)

        # 3. Profiling setup
        should_profile = settings.profiling_enabled and (
            request.headers.get("X-Enable-Profiler") == "true"
        )
        profiler = None
        if should_profile:
            profiler = cProfile.Profile()
            profiler.enable()

        # 4. Get OpenTelemetry Trace ID
        trace_id = "none"
        if HAS_OTEL:
            current_span = trace.get_current_span()
            if current_span and current_span.get_span_context().is_valid:
                trace_id = format(current_span.get_span_context().trace_id, "032x")

        # Process the request
        try:
            response = await call_next(request)

            process_time = time.perf_counter() - start_time
            end_mem = PerformanceProfiler.get_memory_usage_mb()
            mem_delta = end_mem - start_mem

            # 5. Inject observability headers into response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}s"
            response.headers["X-Memory-Delta"] = f"{mem_delta:.2f}MB"

            # 6. Enrich span with performance data
            if HAS_OTEL:
                current_span = trace.get_current_span()
                if current_span.is_recording():
                    current_span.set_attribute("http.memory_delta_mb", mem_delta)
                    current_span.set_attribute("http.duration_ms", process_time * 1000)

            # 7. Operational Analytics: API Usage (10.2.9)
            metrics.track_http_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=process_time,
            )

            # 8. Handle Profiling result
            profile_dump = None
            if profiler:
                profiler.disable()
                s = io.StringIO()
                ps = pstats.Stats(profiler, stream=s).sort_stats(
                    pstats.SortKey.CUMULATIVE
                )
                ps.print_stats(30)
                profile_dump = s.getvalue()

            # 9. Log success with performance context
            log_level = logging.INFO
            # Automatic warning for slow requests
            if (process_time * 1000) > settings.profiling_slow_threshold_ms:
                log_level = logging.WARNING

            logger.log(
                level=log_level,
                msg=f"Request finished: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "extra_data": {
                        "status_code": response.status_code,
                        "duration": process_time,
                        "request_id": request_id,
                        "correlation_id": correlation_id,
                        "trace_id": trace_id,
                        "memory_delta_mb": mem_delta,
                        "performance_profile": profile_dump if should_profile else None,
                    }
                },
            )

            return response

        except Exception as e:
            process_time = time.perf_counter() - start_time
            # Analytics: Track failed request
            metrics.track_http_request(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration=process_time,
            )

            logger.error(
                f"Request failed: {request.method} {request.url.path} - Error: {str(e)}",
                extra={
                    "extra_data": {
                        "duration": process_time,
                        "request_id": request_id,
                        "correlation_id": correlation_id,
                        "trace_id": trace_id,
                    }
                },
                exc_info=True,
            )
            if HAS_OTEL:
                current_span = trace.get_current_span()
                if current_span.is_recording():
                    current_span.record_exception(e)
                    current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise
