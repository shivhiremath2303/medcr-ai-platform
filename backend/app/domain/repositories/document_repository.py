from abc import ABC, abstractmethod

from app.domain.models import Document


class DocumentRepository(ABC):
    """
    Repository contract for persisted documents.
    """

    @abstractmethod
    def save(self, document: Document) -> Document:
        """Persist a document and return the stored representation."""

    @abstractmethod
    def get_by_id(self, document_id: str) -> Document | None:
        """Retrieve a document by identifier."""

    @abstractmethod
    def list_all(self) -> list[Document]:
        """Return all known documents."""
