import time
from app.domain.models import SearchResult
from app.domain.repositories.retriever import Retriever
from app.domain.repositories.reranker import Reranker
from app.core.observability.metrics import MetricsRegistry


class RetrievalService(Retriever):
    """
    Retrieves and reranks the most relevant chunks.
    Implements the Retriever interface.
    """

    def __init__(
        self,
        retriever: Retriever,
        reranker: Reranker,
        metrics: MetricsRegistry,
        candidate_multiplier: int = 4,
        min_candidates: int = 20,
    ):
        self.retriever = retriever
        self.reranker = reranker
        self.metrics = metrics
        self.candidate_multiplier = candidate_multiplier
        self.min_candidates = min_candidates

    def retrieve(
        self,
        query: str,
        k: int = 5,
    ) -> list[SearchResult]:
        """
        Retrieve candidate results and rerank them.
        """
        start_time = time.perf_counter()

        candidate_count = max(
            k * self.candidate_multiplier,
            self.min_candidates,
        )

        candidates = self.retriever.retrieve(
            query=query,
            k=candidate_count,
        )

        results = self.reranker.rerank(
            query=query,
            results=candidates,
            k=k,
        )

        duration = time.perf_counter() - start_time
        self.metrics.track_retrieval("hybrid", duration)

        return results
