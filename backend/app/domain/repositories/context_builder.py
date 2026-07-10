from abc import ABC, abstractmethod
from app.domain.models import SearchResult


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
