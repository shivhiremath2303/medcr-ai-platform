import asyncio
import logging
import time
from typing import Dict, Callable, Any

from app.domain.models.background_task import BackgroundTask, TaskStatus
from app.domain.repositories.background_tasks import BackgroundTaskProvider
from app.core.observability.telemetry import get_tracer
from app.core.observability.metrics import MetricsRegistry
from app.core.observability.resource_guard import ResourceGuard

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)

class WorkerService:
    """
    Enterprise Background Worker Service.
    Responsible for polling the distributed queue and executing registered handlers.
    Updated with Adaptive Resource Management (10.3.9).
    """

    def __init__(
        self,
        task_provider: BackgroundTaskProvider,
        metrics: MetricsRegistry,
        resource_guard: ResourceGuard
    ):
        self.provider = task_provider
        self.metrics = metrics
        self.resource_guard = resource_guard
        self.handlers: Dict[str, Callable] = {}
        self._running = False

    def register_handler(self, name: str, handler: Callable):
        """Registers a handler function for a specific task type."""
        self.handlers[name] = handler
        logger.info(f"Registered background task handler: {name}")

    async def start(self, polling_interval: float = 1.0):
        """Starts the worker loop."""
        self._running = True
        logger.info("Background Worker Service started with Resource Guard.")

        while self._running:
            try:
                # 10.3.9: Adaptive Load Shedding for workers
                if self.resource_guard.is_under_pressure():
                    logger.warning("Worker under pressure. Throttling polling interval.")
                    await asyncio.sleep(polling_interval * 5)

                tasks = await self.provider.get_pending_tasks(limit=5)
                if not tasks:
                    await asyncio.sleep(polling_interval)
                    continue

                execution_tasks = []
                for task in tasks:
                    # 10.3.9: Selective Load Shedding per task priority
                    if self.resource_guard.should_reject_task(priority=task.priority):
                        logger.warning(f"Shedding background task {task.task_id} ({task.priority})")
                        # Re-enqueue with delay or mark as deferred
                        # For 10.3.9 we just marks as failed with 'overload' error
                        await self.provider.update_task_status(
                            task.task_id,
                            TaskStatus.FAILED,
                            error="Dropped due to system resource pressure"
                        )
                        continue

                    execution_tasks.append(self._execute_task(task))

                if execution_tasks:
                    await asyncio.gather(*execution_tasks)

            except Exception as e:
                logger.error(f"Worker loop error: {e}", exc_info=True)
                await asyncio.sleep(polling_interval)

    async def stop(self):
        self._running = False
        logger.info("Background Worker Service stopping...")

    async def _execute_task(self, task: BackgroundTask):
        """Executes a single task with tracing and metrics."""
        handler = self.handlers.get(task.name)
        if not handler:
            error_msg = f"No handler registered for task: {task.name}"
            logger.error(error_msg)
            await self.provider.update_task_status(task.task_id, TaskStatus.FAILED, error=error_msg)
            return

        with tracer.start_as_current_span(f"worker_task:{task.name}") as span:
            span.set_attribute("task.id", task.task_id)
            span.set_attribute("task.priority", task.priority)

            start_time = time.perf_counter()
            await self.provider.update_task_status(task.task_id, TaskStatus.RUNNING)

            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(**task.payload)
                else:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, lambda: handler(**task.payload))

                await self.provider.update_task_status(task.task_id, TaskStatus.COMPLETED, result=result)

                duration = time.perf_counter() - start_time
                self.metrics.observe_histogram("jobs_duration_seconds", duration, {"name": task.name})
                logger.info(f"Task {task.task_id} ({task.name}) completed successfully in {duration:.2f}s")

            except Exception as e:
                logger.error(f"Task {task.task_id} ({task.name}) failed: {e}", exc_info=True)
                span.record_exception(e)
                await self.provider.update_task_status(task.task_id, TaskStatus.FAILED, error=str(e))
