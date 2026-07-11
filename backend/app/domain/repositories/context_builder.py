from abc import ABC, abstractmethod
from app.domain.models import SearchResult, Evidence


class ContextBuilder(ABC):
    """
    Interface for building LLM context from retrieval results.
    """

    @abstractmethod
    def build(
        self,
        results: list[SearchResult],
    ) -> str:
        """
        Convert retrieval results into a context string.
        """

    @abstractmethod
    def results_to_evidence(self, results: list[SearchResult]) -> list[Evidence]:
        """
        Convert search results to domain Evidence objects.
        """
