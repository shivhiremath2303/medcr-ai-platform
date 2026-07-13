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
    Implements Milestone 10.3.3 and 10.3.4.
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
        owner_id: Optional[str] = None,
    ) -> dict:
        """
        Parse, clean, chunk and incrementally index a document.
        """
        extension = Path(file_path).suffix.lower()
        logger.info("Starting document ingestion: %s", file_path)

        with tracer.start_as_current_span("document_ingestion") as span:
            span.set_attribute("doc.path", file_path)
            if owner_id:
                span.set_attribute("doc.owner_id", owner_id)

            try:
                # 1. Parse
                document: Document = self.parser.parse_document(file_path)
                document.owner_id = owner_id

                # 2. Clean
                for page in document.pages:
                    page.text = TextCleaner.clean(page.text)

                # 3. Chunk
                chunks = self.chunker.split_document(document)

                # 4. Incremental Indexing (10.3.4)
                # We use add_chunks instead of create to support large-scale ingestion.
                await self.vector_store.add_chunks(chunks)
                await self.vector_store.save()

                # 5. Metadata persistence
                self.document_repository.save(document)

                # Operational Analytics
                self.metrics.track_document_processed(
                    extension=extension,
                    pages=document.page_count
                )

                # Infrastructure Analytics (Async)
                all_chunks = await self.vector_store.get_all_chunks()
                self.metrics.track_vector_store_size(
                    index_name="legal_documents",
                    count=len(all_chunks)
                )

                return {
                    "document_id": document.document_id,
                    "filename": document.filename,
                    "page_count": document.page_count,
                    "chunk_count": len(chunks),
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
        return await self.vector_store.similarity_search(
            query=query,
            k=k,
        )

    def get_document(self, document_id: str) -> Document | None:
        return self.document_repository.get_by_id(document_id)

    async def list_documents(self, limit: int = 100, offset: int = 0) -> list[Document]:
        """Return documents with pagination support (10.3.7)."""
        return await self.document_repository.list_all(limit=limit, offset=offset)
