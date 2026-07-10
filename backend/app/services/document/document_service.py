from app.core.logger import get_logger
from app.domain.models import Document
from app.domain.repositories import DocumentRepository
from app.services.document.chunker import DocumentChunker
from app.services.document.cleaner import TextCleaner
from app.services.document.parser import DocumentParser
from app.services.document.vector_store import VectorStoreService

logger = get_logger(__name__)


class DocumentService(DocumentRepository):
    """
    Coordinates the complete document ingestion pipeline.
    """

    def __init__(self, vector_store: VectorStoreService | None = None):
        self.chunker = DocumentChunker()

        if vector_store is None:
            from app.di import get_vector_store

            self.vector_store = get_vector_store()

            loaded = self.vector_store.load()

            if loaded:
                logger.info("Loaded existing FAISS index.")
            else:
                logger.info("No existing FAISS index found. A new index will be created.")
        else:
            self.vector_store = vector_store

    def ingest_document(
        self,
        file_path: str,
    ) -> dict:
        """
        Parse, clean, chunk and index a document.
        """

        logger.info("Starting document ingestion: %s", file_path)

        # Parse into the domain model.
        document: Document = DocumentParser.parse_document(file_path)

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

    def save(self, document: Document) -> Document:
        return document

    def get_by_id(self, document_id: str) -> Document | None:
        return None

    def list_all(self) -> list[Document]:
        return []
