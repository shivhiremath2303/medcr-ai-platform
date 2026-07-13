from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.domain.models import SearchResult


class Retriever(ABC):
    """
    Enterprise Interface for retrieval operations.
    Updated to support async for horizontal scaling (10.3.3).
    """

    @abstractmethod
    async def retrieve(
        self, query: str, k: int = 5, params: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Retrieve relevant results for a query."""
