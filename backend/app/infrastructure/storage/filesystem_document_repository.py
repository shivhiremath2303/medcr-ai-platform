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
    Enhanced for Multi-Tenancy (10.4.4) with physical directory isolation.
    """

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    def _get_tenant_dir(self, tenant_id: str | None) -> Path:
        """Resolve tenant-specific metadata directory."""
        tenant_path = self.storage_dir / (tenant_id or "global")
        tenant_path.mkdir(parents=True, exist_ok=True)
        return tenant_path

    async def save(self, document: Document) -> Document:
        """
        Persist a document to the filesystem as JSON in a tenant-isolated directory.
        """
        async with self._lock:
            tenant_dir = self._get_tenant_dir(document.tenant_id)
            file_path = tenant_dir / f"{document.document_id}.json"
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
        Note: In a high-scale tenant architecture, we should ideally know the tenant_id
        to locate the file faster. This implementation searches all tenant dirs
        if tenant_id isn't known, or we can assume document_ids are globally unique
        and use a global index (future). For now, we search specifically if possible.
        """
        # Search globally across all tenant directories
        for tenant_dir in self.storage_dir.iterdir():
            if tenant_dir.is_dir():
                file_path = tenant_dir / f"{document_id}.json"
                if file_path.exists():
                    with open(file_path, encoding="utf-8") as f:
                        data = json.load(f)
                    return self._map_to_domain(data)
        return None

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Document]:
        """
        List all stored documents across all tenants (Administrative).
        """
        all_files = sorted(self.storage_dir.rglob("*.json"))
        paged_files = all_files[offset : offset + limit]

        documents = []
        for file_path in paged_files:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                documents.append(self._map_to_domain(data))
        return documents

    async def list_by_tenant(
        self, tenant_id: str, limit: int = 100, offset: int = 0
    ) -> List[Document]:
        """
        List documents for a specific tenant.
        """
        tenant_dir = self._get_tenant_dir(tenant_id)
        all_files = sorted(tenant_dir.glob("*.json"))
        paged_files = all_files[offset : offset + limit]

        documents = []
        for file_path in paged_files:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                documents.append(self._map_to_domain(data))
        return documents

    async def delete(self, document_id: str) -> bool:
        async with self._lock:
            # Search and delete
            for tenant_dir in self.storage_dir.iterdir():
                if tenant_dir.is_dir():
                    file_path = tenant_dir / f"{document_id}.json"
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
        # Handle optional fields
        doc.owner_id = data.get("owner_id")
        doc.tenant_id = data.get("tenant_id")
        return doc
