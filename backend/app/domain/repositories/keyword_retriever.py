from abc import ABC, abstractmethod
from app.domain.models import Chunk


class KeywordRetriever(ABC):
    """
    Interface for keyword-based retrieval.
    """

    @abstractmethod
    def index(self, chunks: list[Chunk]) -> None:
        """Index the provided chunks."""

    @abstractmethod
    def search(self, query: str, k: int = 5) -> list[Chunk]:
        """Search the indexed chunks."""
