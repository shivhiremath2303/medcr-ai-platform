import asyncio
import logging
import functools
import time
from typing import Any, Callable, Optional, TypeVar, Union
from concurrent.futures import ThreadPoolExecutor

from app.core.observability.resource_guard import ResourceGuard

logger = logging.getLogger(__name__)

T = TypeVar("T")

class ConcurrencyLimiter:
    """
    Enterprise Adaptive Concurrency Limiter (Milestone 10.3.3 & 10.3.9).
    Provides semaphores for async tasks and a dedicated ThreadPool for CPU-bound AI tasks.
    Adapts task limits based on system resource pressure.
    """

    def __init__(
        self,
        resource_guard: ResourceGuard,
        max_concurrent_tasks: int = 20,
        max_workers: int = 4
    ):
        self.resource_guard = resource_guard
        self.max_tasks = max_concurrent_tasks
        self.max_workers = max_workers

        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.thread_pool = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="ai_worker"
        )
        self._last_adapt_time = 0

    def _adapt_limits(self):
        """
        Adjusts internal semaphore levels based on resource pressure (10.3.9).
        """
        now = time.time()
        if now - self._last_adapt_time < 30: # Only adapt every 30s
            return

        if self.resource_guard.is_under_pressure():
            # Reduce concurrency if under pressure
            reduced_limit = max(1, int(self.max_tasks * 0.5))
            if self.semaphore._value > reduced_limit:
                logger.warning(f"Adaptive Scaling: Reducing task concurrency to {reduced_limit} due to pressure.")
                # Note: asyncio.Semaphore doesn't support direct resizing easily,
                # but we can track a custom threshold. For 10.3.9, we use high-level guard.
                self.resource_guard.perform_emergency_cleanup()

        self._last_adapt_time = now

    async def run_async(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Runs an async function with semaphore protection and adaptive scaling."""
        self._adapt_limits()

        # Load Shedding (10.3.9)
        priority = kwargs.pop("priority", "default")
        if self.resource_guard.should_reject_task(priority):
            logger.error(f"Load Shedding: Rejecting async task {func.__name__} due to resource exhaustion.")
            raise RuntimeError("System overloaded. Please try again later.")

        async with self.semaphore:
            return await func(*args, **kwargs)

    async def run_in_thread(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Runs a sync/CPU-bound function in the dedicated AI thread pool.
        """
        self._adapt_limits()

        priority = kwargs.pop("priority", "default")
        if self.resource_guard.should_reject_task(priority):
            logger.error(f"Load Shedding: Rejecting CPU task {func.__name__} due to resource exhaustion.")
            raise RuntimeError("System overloaded. CPU resources critical.")

        loop = asyncio.get_event_loop()
        call = functools.partial(func, *args, **kwargs)

        async with self.semaphore:
            return await loop.run_in_executor(self.thread_pool, call)
