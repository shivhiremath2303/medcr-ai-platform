import asyncio
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, List, Optional

from app.domain.models import Document, Page
from app.domain.repositories.document_repository import DocumentRepository


class FilesystemDocumentRepository(DocumentRepository):
    """
    Filesystem implementation of DocumentRepository using JSON for persistence.
    Updated for Multi-Tenancy (10.4.4).
    """

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def save(self, document: Document) -> Document:
        """
        Persist a document to the filesystem as JSON.
        """
        async with self._lock:
            file_path = self.storage_dir / f"{document.document_id}.json"
            data = asdict(document)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return document

    async def save_batch(self, documents: List[Document]) -> None:
        """Optimized batch save (10.3.6)."""
        tasks = [self.save(doc) for doc in documents]
        await asyncio.gather(*tasks)

    async def get_by_id(self, document_id: str) -> Document | None:
        """
        Retrieve a document by ID.
        """
        file_path = self.storage_dir / f"{document_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        return self._map_to_domain(data)

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Document]:
        """
        List all stored documents with basic pagination support.
        """
        all_files = sorted(self.storage_dir.glob("*.json"))
        paged_files = all_files[offset : offset + limit]

        documents = []
        for file_path in paged_files:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                documents.append(self._map_to_domain(data))
        return documents

    async def delete(self, document_id: str) -> bool:
        async with self._lock:
            file_path = self.storage_dir / f"{document_id}.json"
            if file_path.exists():
                file_path.unlink()
                return True
            return False

    def _map_to_domain(self, data: dict) -> Document:
        pages = [
            Page(page_number=p["page_number"], text=p["text"]) for p in data["pages"]
        ]
        doc = Document(
            document_id=data["document_id"], filename=data["filename"], pages=pages
        )
        # Handle optional fields from newer schema
        if "owner_id" in data:
            doc.owner_id = data["owner_id"]
        if "tenant_id" in data:
            doc.tenant_id = data["tenant_id"]
        return doc
