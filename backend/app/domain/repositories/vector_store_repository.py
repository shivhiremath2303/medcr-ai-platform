from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models import Chunk, SearchResult


class VectorStoreRepository(ABC):
    """
    Enterprise Repository contract for chunk vector storage and search.
    Updated for Multi-Tenant Isolation (10.4.6).
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
    async def similarity_search(
        self,
        query: str,
        k: int = 3,
        tenant_id: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search the vector index for the most similar chunks.
        Strictly filters by tenant_id if provided.
        """

    @abstractmethod
    async def get_all_chunks(self, tenant_id: Optional[str] = None) -> List[Chunk]:
        """Return chunks from the index, optionally filtered by tenant."""

    @abstractmethod
    async def optimize(self) -> None:
        """Perform background optimization/compaction of the index."""

    @property
    @abstractmethod
    def is_ready(self) -> bool:
        """Check if the index is loaded and ready for search."""
