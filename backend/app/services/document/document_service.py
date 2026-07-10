from app.core.logger import get_logger
from app.domain.models import Document
from app.domain.repositories.document_repository import DocumentRepository
from app.domain.repositories.chunker import Chunker
from app.domain.repositories.document_parser import DocumentParser
from app.domain.repositories.vector_store_repository import VectorStoreRepository
from app.services.document.cleaner import TextCleaner

logger = get_logger(__name__)


class DocumentService:
    """
    Coordinates the complete document ingestion pipeline.
    """

    def __init__(
        self,
        chunker: Chunker,
        vector_store: VectorStoreRepository,
        parser: DocumentParser,
        document_repository: DocumentRepository,
    ):
        self.chunker = chunker
        self.vector_store = vector_store
        self.parser = parser
        self.document_repository = document_repository

        loaded = self.vector_store.load()
        if loaded:
            logger.info("Loaded existing vector index.")
        else:
            logger.info("No existing vector index found. A new index will be created.")

    def ingest_document(
        self,
        file_path: str,
    ) -> dict:
        """
        Parse, clean, chunk and index a document.
        """

        logger.info("Starting document ingestion: %s", file_path)

        # Parse into the domain model.
        document: Document = self.parser.parse_document(file_path)

        logger.info(
            "Parsed document '%s' (%d pages).",
            document.filename,
            document.page_count,
        )

        # Clean every page independently.
        for page in document.pages:
            page.text = TextCleaner.clean(page.text)

        logger.info("Document cleaned successfully.")

        # Produce metadata-aware domain chunks.
        chunks = self.chunker.split_document(document)

        logger.info(
            "Created %d chunks from document.",
            len(chunks),
        )

        # Create / update the vector index.
        self.vector_store.create(chunks)

        logger.info("Vector index created.")

        # Persist the index.
        self.vector_store.save()

        logger.info("Vector index saved successfully.")

        # Persist document metadata.
        self.document_repository.save(document)

        logger.info(
            "Completed ingestion of '%s'.",
            document.filename,
        )

        return {
            "document_id": document.document_id,
            "filename": document.filename,
            "page_count": document.page_count,
            "chunk_count": len(chunks),
        }

    def search(
        self,
        query: str,
        k: int = 3,
    ):
        logger.info(
            "Executing similarity search (k=%d).",
            k,
        )

        return self.vector_store.similarity_search(
            query=query,
            k=k,
        )

    def get_document(self, document_id: str) -> Document | None:
        return self.document_repository.get_by_id(document_id)

    def list_documents(self) -> list[Document]:
        return self.document_repository.list_all()
