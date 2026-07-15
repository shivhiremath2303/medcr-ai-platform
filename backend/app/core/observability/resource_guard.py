import gc
import logging
import os
from typing import Optional

import psutil

from app.core.observability.metrics import MetricsRegistry

logger = logging.getLogger(__name__)


class ResourceGuard:
    """
    Enterprise Resource Manager (Milestone 10.3.9).
    Monitors system resources and triggers adaptive actions (GC, Eviction, Shedding).
    """

    def __init__(
        self,
        metrics: MetricsRegistry,
        memory_limit_mb: float = 2048.0,  # Target limit for the pod
        pressure_threshold: float = 0.85,  # 85% usage triggers pressure mode
    ):
        self.metrics = metrics
        self.memory_limit_mb = memory_limit_mb
        self.pressure_threshold = pressure_threshold
        self.process = psutil.Process(os.getpid())

    def get_current_usage_mb(self) -> float:
        """Get current RSS memory usage."""
        return self.process.memory_info().rss / (1024 * 1024)

    def is_under_pressure(self) -> bool:
        """Check if memory usage exceeds the pressure threshold."""
        usage = self.get_current_usage_mb()
        ratio = usage / self.memory_limit_mb

        self.metrics.set_gauge("resource_memory_usage_mb", usage)
        self.metrics.set_gauge("resource_memory_ratio", ratio)

        return ratio > self.pressure_threshold

    def perform_emergency_cleanup(self):
        """Triggers GC and logs warning when under pressure."""
        usage_before = self.get_current_usage_mb()
        logger.warning(
            f"Resource pressure detected ({usage_before:.2f}MB). Triggering emergency cleanup."
        )

        # 1. Manual Garbage Collection
        collected = gc.collect()

        # 2. Log efficiency
        usage_after = self.get_current_usage_mb()
        freed = usage_before - usage_after

        logger.info(
            f"Cleanup complete. Freed {freed:.2f}MB. Collected {collected} objects."
        )
        self.metrics.increment_counter("resource_cleanup_total", {"status": "success"})

    def should_reject_task(self, priority: str = "default") -> bool:
        """
        Logic for Load Shedding.
        Rejects low-priority tasks if resources are critical.
        """
        usage_ratio = self.get_current_usage_mb() / self.memory_limit_mb

        # Severe pressure (>95%): Reject all but high priority
        if usage_ratio > 0.95 and priority != "high":
            return True

        # Moderate pressure (>85%): Reject low priority
        if usage_ratio > 0.85 and priority == "low":
            return True

        return False
