from abc import ABC, abstractmethod

from app.domain.models import Chunk, Document


class Chunker(ABC):
    """
    Interface for splitting documents into chunks.
    """

    @abstractmethod
    def split_document(self, document: Document) -> list[Chunk]:
        """
        Split a document into chunks.
        """
