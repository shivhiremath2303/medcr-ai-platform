import time
from typing import Dict, Optional
from app.domain.repositories.metrics_provider import MetricsProvider

class NoOpMetricsProvider(MetricsProvider):
    """
    Default implementation that does nothing.
    """
    def increment_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> None:
        pass

    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        pass

class MetricsRegistry:
    """
    High-level utility to help track metrics throughout the application.
    This acts as a facade over the MetricsProvider.
    """
    def __init__(self, provider: MetricsProvider):
        self.provider = provider

    def track_http_request(self, method: str, path: str, status_code: int, duration: float):
        self.provider.increment_counter(
            "http_requests_total",
            {"method": method, "path": path, "status": str(status_code)}
        )
        self.provider.observe_histogram(
            "http_request_duration_seconds",
            duration,
            {"method": method, "path": path}
        )

    def track_llm_call(self, provider: str, model: str, duration: float):
        self.provider.increment_counter(
            "llm_calls_total",
            {"provider": provider, "model": model}
        )
        self.provider.observe_histogram(
            "llm_call_duration_seconds",
            duration,
            {"provider": provider, "model": model}
        )

    def track_retrieval(self, type: str, duration: float):
        self.provider.increment_counter("retrievals_total", {"type": type})
        self.provider.observe_histogram("retrieval_duration_seconds", duration, {"type": type})

    def track_document_upload(self, extension: str, status: str):
        self.provider.increment_counter(
            "document_uploads_total",
            {"extension": extension, "status": status}
        )
