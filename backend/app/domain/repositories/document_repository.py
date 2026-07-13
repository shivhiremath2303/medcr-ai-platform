from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import Document


class DocumentRepository(ABC):
    """
    Enterprise Repository contract for persisted documents.
    Updated to support batch operations and async for scalability (10.3.6).
    """

    @abstractmethod
    async def save(self, document: Document) -> Document:
        """Persist a single document."""

    @abstractmethod
    async def save_batch(self, documents: List[Document]) -> None:
        """Persist multiple documents in a single transaction."""

    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """Retrieve a document by identifier."""

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Document]:
        """Return documents with pagination support."""

    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """Remove a document and its metadata."""
