import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, List, Optional

from app.domain.models import Document, Page
from app.domain.repositories.document_repository import DocumentRepository


class FilesystemDocumentRepository(DocumentRepository):
    """
    Filesystem implementation of DocumentRepository using JSON for persistence.
    """

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, document: Document) -> Document:
        """
        Persist a document to the filesystem as JSON.
        """
        file_path = self.storage_dir / f"{document.document_id}.json"

        data = asdict(document)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return document

    def get_by_id(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a document by ID.
        """
        file_path = self.storage_dir / f"{document_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        return self._map_to_domain(data)

    def list_all(self) -> List[Document]:
        """
        List all stored documents.
        """
        documents = []
        for file_path in self.storage_dir.glob("*.json"):
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                documents.append(self._map_to_domain(data))
        return documents

    def _map_to_domain(self, data: dict) -> Document:
        pages = [
            Page(page_number=p["page_number"], text=p["text"]) for p in data["pages"]
        ]
        return Document(
            document_id=data["document_id"], filename=data["filename"], pages=pages
        )
