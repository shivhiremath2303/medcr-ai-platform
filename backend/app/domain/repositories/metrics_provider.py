from abc import ABC, abstractmethod
from typing import Dict, Optional


class MetricsProvider(ABC):
    """
    Interface for tracking application metrics.
    """

    @abstractmethod
    def increment_counter(
        self, name: str, labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Increment a counter metric."""

    @abstractmethod
    def observe_histogram(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Observe a value in a histogram metric."""
