from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from app.domain.models import Chunk, SearchResult


class Retriever(ABC):
    """
    Interface for retrieval operations.
    """

    @abstractmethod
    def retrieve(
        self,
        query: str,
        k: int = 5,
        params: Optional[Dict[str, Any]] = None
    ) -> list[SearchResult]:
        """Retrieve relevant results for a query."""
