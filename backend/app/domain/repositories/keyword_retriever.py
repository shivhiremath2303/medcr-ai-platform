from abc import ABC, abstractmethod
from typing import List

from app.domain.models import Chunk


class KeywordRetriever(ABC):
    """
    Enterprise Interface for keyword-based retrieval.
    Updated for horizontal scaling (10.3.3).
    """

    @abstractmethod
    async def index(self, chunks: List[Chunk]) -> None:
        """Index the provided chunks."""

    @abstractmethod
    async def search(self, query: str, k: int = 5) -> List[Chunk]:
        """Search the indexed chunks."""
