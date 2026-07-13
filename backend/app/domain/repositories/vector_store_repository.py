from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import Chunk, SearchResult


class VectorStoreRepository(ABC):
    """
    Enterprise Repository contract for chunk vector storage and search.
    Updated to support incremental updates and scaling (10.3.4).
    """

    @abstractmethod
    async def create(self, chunks: List[Chunk]) -> None:
        """Create or replace the vector index for the provided chunks."""

    @abstractmethod
    async def add_chunks(self, chunks: List[Chunk]) -> None:
        """Incrementally add chunks to the existing index."""

    @abstractmethod
    async def save(self) -> None:
        """Persist the vector index to storage."""

    @abstractmethod
    async def load(self) -> bool:
        """Load an existing persisted index if present."""

    @abstractmethod
    async def similarity_search(self, query: str, k: int = 3) -> List[SearchResult]:
        """Search the vector index for the most similar chunks."""

    @abstractmethod
    async def get_all_chunks(self) -> List[Chunk]:
        """Return every stored chunk from the index."""

    @abstractmethod
    async def optimize(self) -> None:
        """Perform background optimization/compaction of the index."""

    @property
    @abstractmethod
    def is_ready(self) -> bool:
        """Check if the index is loaded and ready for search."""
