from abc import ABC, abstractmethod
from app.domain.models import Chunk, SearchResult


class Retriever(ABC):
    """
    Interface for retrieval operations.
    """

    @abstractmethod
    def retrieve(self, query: str, k: int = 5) -> list[SearchResult]:
        """Retrieve relevant results for a query."""
