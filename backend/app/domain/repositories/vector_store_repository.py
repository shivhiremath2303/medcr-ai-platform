from abc import ABC, abstractmethod

from app.domain.models import Chunk, SearchResult


class VectorStoreRepository(ABC):
    """
    Repository contract for chunk vector storage and search.
    """

    @abstractmethod
    def create(self, chunks: list[Chunk]) -> None:
        """Create or replace the vector index for the provided chunks."""

    @abstractmethod
    def save(self) -> None:
        """Persist the vector index to storage."""

    @abstractmethod
    def load(self) -> bool:
        """Load an existing persisted index if present."""

    @abstractmethod
    def similarity_search(self, query: str, k: int = 3) -> list[SearchResult]:
        """Search the vector index for the most similar chunks."""

    @abstractmethod
    def get_all_chunks(self) -> list[Chunk]:
        """Return every stored chunk from the index."""
