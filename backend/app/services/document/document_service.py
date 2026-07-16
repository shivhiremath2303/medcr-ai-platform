import asyncio
from pathlib import Path
from typing import Optional

from app.core.observability.logger import get_logger
from app.core.observability.metrics import MetricsRegistry
from app.core.observability.telemetry import get_tracer
from app.domain.models import Document
from app.domain.repositories.chunker import Chunker
from app.domain.repositories.document_parser import DocumentParser
from app.domain.repositories.document_repository import DocumentRepository
from app.domain.repositories.vector_store_repository import VectorStoreRepository
from app.services.document.cleaner import TextCleaner

logger = get_logger(__name__)
tracer = get_tracer(__name__)


class DocumentService:
    """
    Coordinates the complete document ingestion pipeline with Operational Analytics and Scaling.
    Enhanced with Multi-Tenant support (10.4.4).
    """

    def __init__(
        self,
        chunker: Chunker,
        vector_store: VectorStoreRepository,
        parser: DocumentParser,
        document_repository: DocumentRepository,
        metrics: MetricsRegistry,
    ):
        self.chunker = chunker
        self.vector_store = vector_store
        self.parser = parser
        self.document_repository = document_repository
        self.metrics = metrics

    async def ingest_document(
        self,
        file_path: str,
        owner_id: str | None = None,
        tenant_id: str | None = None,
    ) -> dict:
        """
        Parse, clean, chunk and incrementally index a document.
        Ensures tenant isolation throughout the pipeline.
        """
        extension = Path(file_path).suffix.lower()
        logger.info(
            "Starting document ingestion: %s (Tenant: %s)", file_path, tenant_id
        )

        with tracer.start_as_current_span("document_ingestion") as span:
            span.set_attribute("doc.path", file_path)
            if owner_id:
                span.set_attribute("doc.owner_id", owner_id)
            if tenant_id:
                span.set_attribute("tenant.id", tenant_id)

            try:
                # 1. Parse
                document: Document = self.parser.parse_document(file_path)
                document.owner_id = owner_id
                document.tenant_id = tenant_id

                # 2. Clean
                for page in document.pages:
                    page.text = TextCleaner.clean(page.text)

                # 3. Chunk (Preserves tenant_id via Chunker implementation)
                chunks = self.chunker.split_document(document)

                # 4. Incremental Indexing (10.3.4)
                # Chunks now carry tenant_id in metadata for logical partitioning.
                await self.vector_store.add_chunks(chunks)
                await self.vector_store.save()

                # 5. Metadata persistence
                await self.document_repository.save(document)

                # Operational Analytics
                self.metrics.track_document_processed(
                    extension=extension, pages=document.page_count
                )

                # Infrastructure Analytics (Async)
                all_chunks = await self.vector_store.get_all_chunks()
                self.metrics.track_vector_store_size(
                    index_name="legal_documents", count=len(all_chunks)
                )

                return {
                    "document_id": document.document_id,
                    "filename": document.filename,
                    "page_count": document.page_count,
                    "chunk_count": len(chunks),
                    "tenant_id": tenant_id,
                }
            except Exception as e:
                logger.error(f"Failed to ingest document {file_path}: {str(e)}")
                span.record_exception(e)
                raise

    async def search(
        self,
        query: str,
        k: int = 3,
    ):
        """Perform similarity search on the vector store."""
        # Note: Vector search needs tenant-aware filtering in 10.4.6
        return await self.vector_store.similarity_search(
            query=query,
            k=k,
        )

    async def get_document(self, document_id: str) -> Document | None:
        return await self.document_repository.get_by_id(document_id)

    async def list_documents(
        self, limit: int = 100, offset: int = 0, tenant_id: str | None = None
    ) -> list[Document]:
        """
        Return documents with pagination and tenant filtering support.
        """
        if tenant_id:
            return await self.document_repository.list_by_tenant(
                tenant_id=tenant_id, limit=limit, offset=offset
            )
        return await self.document_repository.list_all(limit=limit, offset=offset)
