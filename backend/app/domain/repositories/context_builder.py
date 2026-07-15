from abc import ABC, abstractmethod

from app.domain.models import Evidence, SearchResult


class ContextBuilder(ABC):
    """
    Interface for building LLM context from retrieval results.
    """

    @abstractmethod
    def build(
        self,
        results: list[SearchResult],
        query: str | None = None,
    ) -> str:
        """
        Convert retrieval results into a context string.
        Optionally uses the query for dynamic pruning (10.5.3).
        """

    @abstractmethod
    def results_to_evidence(self, results: list[SearchResult]) -> list[Evidence]:
        """
        Convert search results to domain Evidence objects.
        """
