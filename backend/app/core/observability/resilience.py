import asyncio
import functools
import inspect
import logging
import time
from datetime import datetime, timedelta
from enum import Enum, StrEnum
from typing import Any, Callable, Dict, Optional, TypeVar

from app.core.observability.metrics import MetricsRegistry

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(StrEnum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, traffic stopped
    HALF_OPEN = "half_open"  # Testing for recovery


class CircuitBreaker:
    """
    Enterprise Circuit Breaker (Milestone 10.3.8).
    Prevents cascading failures by stopping traffic to failing dependencies.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        metrics: MetricsRegistry | None = None,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.metrics = metrics

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: float | None = None

    def __call__(self, func: Callable[..., Any]) -> Any:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self.call(func, *args, **kwargs)

        return wrapper

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if self.state == CircuitState.OPEN:
            if self.last_failure_time and (
                time.time() - self.last_failure_time > self.recovery_timeout
            ):
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit Breaker [{self.name}] moving to HALF_OPEN")
            else:
                if self.metrics:
                    self.metrics.increment_counter(
                        "resilience_circuit_tripped_total", {"name": self.name}
                    )
                raise RuntimeError(
                    f"Circuit Breaker [{self.name}] is OPEN. Dependency is unreachable."
                )

        try:
            # Execution
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Success logic
            if self.state == CircuitState.HALF_OPEN:
                logger.info(
                    f"Circuit Breaker [{self.name}] moving to CLOSED (Recovered)"
                )
                self.state = CircuitState.CLOSED
                self.failure_count = 0

            return result

        except Exception as e:
            # Failure logic
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                if self.state != CircuitState.OPEN:
                    logger.error(
                        f"Circuit Breaker [{self.name}] TRIPPED (OPEN). Failures: {self.failure_count}"
                    )
                    self.state = CircuitState.OPEN

            if self.metrics:
                self.metrics.increment_counter(
                    "resilience_dependency_failure_total",
                    {"name": self.name, "error": type(e).__name__},
                )

            raise e


class ResiliencePolicy:
    """
    Standard resilience configuration for the enterprise platform.
    """

    @staticmethod
    def get_llm_retry():
        from tenacity import (
            retry,
            retry_if_exception_type,
            stop_after_attempt,
            wait_exponential,
        )

        return retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type(
                (TimeoutError, ConnectionError, RuntimeError)
            ),
            reraise=True,
        )
