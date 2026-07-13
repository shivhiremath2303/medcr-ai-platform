import asyncio
import time

from sentence_transformers import CrossEncoder

from app.core.observability.concurrency import ConcurrencyLimiter
from app.core.observability.metrics import MetricsRegistry
from app.core.observability.telemetry import get_tracer
from app.domain.models import SearchResult
from app.domain.repositories.reranker import Reranker

tracer = get_tracer(__name__)


class CrossEncoderAdapter(Reranker):
    """
    Adapter for CrossEncoder reranking with Enterprise AI Observability and Horizontal Scaling.
    Offloads heavy inference to a dedicated thread pool.
    Implements Milestone 10.3.3.
    """

    def __init__(
        self, model_name: str, metrics: MetricsRegistry, limiter: ConcurrencyLimiter
    ):
        """
        Initialize with a model name, metrics registry, and concurrency limiter.
        """
        self.model_name = model_name
        self.metrics = metrics
        self.limiter = limiter
        # Lazy load model to avoid overhead during DI initialization
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = CrossEncoder(self.model_name)
        return self._model

    async def rerank(
        self,
        query: str,
        results: list[SearchResult],
        k: int,
    ) -> list[SearchResult]:
        if not results:
            return []

        start_time = time.perf_counter()
        with tracer.start_as_current_span("ai_rerank") as span:
            span.set_attribute("ai.reranker.model", self.model_name)
            span.set_attribute("ai.reranker.input_count", len(results))

            try:
                # 1. Parallelize: Offload CPU-bound prediction to thread pool (10.3.3)
                scores = await self.limiter.run_in_thread(self._predict, query, results)

                for result, score in zip(results, scores, strict=True):
                    result.reranker_score = float(score)
                    result.score = float(score)

                results.sort(key=lambda x: x.score, reverse=True)

                for rank, result in enumerate(results, start=1):
                    result.rank = rank

                final_results = results[:k]

                duration = time.perf_counter() - start_time
                self.metrics.track_reranker(self.model_name, duration)
                span.set_attribute("ai.reranker.duration", duration)

                return final_results

            except Exception as e:
                span.record_exception(e)
                raise RuntimeError(f"Reranking failed: {e}") from e

    def _predict(self, query: str, results: list[SearchResult]) -> list[float]:
        """Internal sync prediction method to be run in executor."""
        pairs = [(query, result.chunk.text) for result in results]
        return self.model.predict(pairs)
