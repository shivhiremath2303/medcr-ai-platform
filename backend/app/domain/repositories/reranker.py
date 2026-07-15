from abc import ABC, abstractmethod
from typing import List

from app.domain.models import SearchResult


class Reranker(ABC):
    """
    Enterprise Interface for reranking search results.
    Updated to support async for horizontal scaling (10.3.3).
    """

    @abstractmethod
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        k: int,
    ) -> List[SearchResult]:
        """Rerank the results based on the query."""
