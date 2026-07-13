import cProfile
import pstats
import io
import time
import os
import psutil
import functools
import logging
from typing import Any, Callable, Dict, Optional
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class PerformanceProfiler:
    """
    Enterprise-grade Performance Profiler for CPU and Memory.
    Provides deep visibility into slow endpoints and background tasks.
    Implements Milestone 10.2.8.
    """

    def __init__(self, name: str, threshold_ms: float = 1000):
        self.name = name
        self.threshold = threshold_ms
        self.profiler = cProfile.Profile()
        self.start_time = 0
        self.start_mem = 0

    def __enter__(self):
        self.start_mem = PerformanceProfiler.get_memory_usage_mb()
        self.start_time = time.perf_counter()
        self.profiler.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profiler.disable()
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        end_mem = PerformanceProfiler.get_memory_usage_mb()
        mem_delta = end_mem - self.start_mem

        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute(f"profile.{self.name}.duration_ms", duration_ms)
            span.set_attribute(f"profile.{self.name}.memory_delta_mb", mem_delta)

        if duration_ms > self.threshold:
            s = io.StringIO()
            ps = pstats.Stats(self.profiler, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
            ps.print_stats(20)

            logger.warning(
                f"Slow execution detected in {self.name} ({duration_ms:.2f}ms). "
                f"Memory Delta: {mem_delta:.2f}MB.",
                extra={
                    "extra_data": {
                        "performance_profile": s.getvalue(),
                        "duration_ms": duration_ms,
                        "mem_delta_mb": mem_delta,
                        "is_slow": True
                    }
                }
            )

    @staticmethod
    def get_memory_usage_mb() -> float:
        """Returns the current resident set size (RSS) in MB."""
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0

    @staticmethod
    def profile_function(name: Optional[str] = None, slow_threshold_ms: float = 1000):
        """
        Decorator to profile a function.
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                with PerformanceProfiler(name or func.__name__, slow_threshold_ms):
                    return await func(*args, **kwargs)

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                with PerformanceProfiler(name or func.__name__, slow_threshold_ms):
                    return func(*args, **kwargs)

            return async_wrapper if functools.iscoroutinefunction(func) else sync_wrapper
        return decorator
