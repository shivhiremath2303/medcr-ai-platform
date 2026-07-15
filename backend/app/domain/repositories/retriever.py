from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.domain.models import SearchResult


class Retriever(ABC):
    """
    Enterprise Interface for retrieval operations.
    Updated for Multi-Tenant Isolation (10.4.6).
    """

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        k: int = 5,
        params: Dict[str, Any] | None = None,
        tenant_id: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Retrieve relevant results for a query.
        Strictly filters by tenant_id if provided.
        """
