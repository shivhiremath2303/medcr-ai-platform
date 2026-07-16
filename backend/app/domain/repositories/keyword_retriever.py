from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models import Chunk


class KeywordRetriever(ABC):
    """
    Enterprise Interface for keyword-based retrieval.
    Updated for Multi-Tenant Isolation (10.4.6).
    """

    @abstractmethod
    async def index(self, chunks: List[Chunk]) -> None:
        """Index the provided chunks."""

    @abstractmethod
    async def search(
        self, query: str, k: int = 5, tenant_id: Optional[str] = None
    ) -> List[Chunk]:
        """
        Search the indexed chunks.
        Strictly filters by tenant_id if provided.
        """
