from abc import ABC, abstractmethod
from typing import Dict, Optional


class MetricsProvider(ABC):
    """
    Enterprise Interface for tracking application metrics.
    Supports Counters, Histograms, and Gauges.
    """

    @abstractmethod
    def increment_counter(
        self, name: str, labels: Dict[str, str] | None = None, amount: float = 1.0
    ) -> None:
        """Increment a counter metric."""

    @abstractmethod
    def observe_histogram(
        self, name: str, value: float, labels: Dict[str, str] | None = None
    ) -> None:
        """Observe a value in a histogram metric."""

    @abstractmethod
    def set_gauge(
        self, name: str, value: float, labels: Dict[str, str] | None = None
    ) -> None:
        """Set a gauge metric to a specific value."""
