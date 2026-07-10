from abc import ABC, abstractmethod
from app.domain.models import SearchResult


class Reranker(ABC):
    """
    Interface for reranking search results.
    """

    @abstractmethod
    def rerank(
        self,
        query: str,
        results: list[SearchResult],
        k: int,
    ) -> list[SearchResult]:
        """Rerank the results based on the query."""
