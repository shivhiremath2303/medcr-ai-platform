from abc import ABC, abstractmethod

from app.domain.models import Chunk


class ChunkRepository(ABC):
    """
    Repository contract for chunk storage and lookup.
    """

    @abstractmethod
    def save_many(self, chunks: list[Chunk]) -> None:
        """Persist a collection of chunks."""

    @abstractmethod
    def list_all(self) -> list[Chunk]:
        """Return all stored chunks."""
