import pickle
from pathlib import Path
from typing import List, Optional

from app.core.config import settings
from app.domain.models import Document
from app.domain.repositories.document_repository import DocumentRepository


class FilesystemDocumentRepository(DocumentRepository):
    """
    Filesystem implementation of DocumentRepository.
    Stores documents as pickled files in the metadata directory.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or settings.metadata_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, document: Document) -> Document:
        """
        Persist a document to the filesystem.
        """
        file_path = self.storage_dir / f"{document.document_id}.pkl"
        with open(file_path, "wb") as f:
            pickle.dump(document, f)
        return document

    def get_by_id(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a document by ID.
        """
        file_path = self.storage_dir / f"{document_id}.pkl"
        if not file_path.exists():
            return None

        with open(file_path, "rb") as f:
            return pickle.load(f)

    def list_all(self) -> List[Document]:
        """
        List all stored documents.
        """
        documents = []
        for file_path in self.storage_dir.glob("*.pkl"):
            with open(file_path, "rb") as f:
                documents.append(pickle.load(f))
        return documents
