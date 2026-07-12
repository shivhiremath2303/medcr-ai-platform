from typing import Dict, Optional, Any
from prometheus_client import Counter, Histogram, Registry, CollectorRegistry
from app.domain.repositories.metrics_provider import MetricsProvider

class PrometheusMetricsProvider(MetricsProvider):
    """
    Prometheus implementation of the MetricsProvider.
    """
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or Registry()
        self.metrics: Dict[str, Any] = {}

    def _get_or_create_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> Counter:
        if name not in self.metrics:
            label_names = list(labels.keys()) if labels else []
            self.metrics[name] = Counter(name, f"Counter for {name}", labelnames=label_names, registry=self.registry)
        return self.metrics[name]

    def _get_or_create_histogram(self, name: str, labels: Optional[Dict[str, str]] = None) -> Histogram:
        if name not in self.metrics:
            label_names = list(labels.keys()) if labels else []
            self.metrics[name] = Histogram(name, f"Histogram for {name}", labelnames=label_names, registry=self.registry)
        return self.metrics[name]

    def increment_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> None:
        counter = self._get_or_create_counter(name, labels)
        if labels:
            counter.labels(**labels).inc()
        else:
            counter.inc()

    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        histogram = self._get_or_create_histogram(name, labels)
        if labels:
            histogram.labels(**labels).observe(value)
        else:
            histogram.observe(value)
