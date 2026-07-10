from abc import ABC, abstractmethod
from app.domain.models import Document


class DocumentParser(ABC):
    """
    Interface for document parsing.
    """

    @abstractmethod
    def parse_document(self, file_path: str) -> Document:
        """
        Parse a document from a file path and return a Document domain model.
        """
