from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LangChainDocument

from app.core.config import settings
from app.core.constants import DEFAULT_TOP_K, FAISS_INDEX_NAME
from app.domain.models import Chunk, Metadata, SearchResult
from app.domain.repositories.vector_store_repository import VectorStoreRepository
from app.domain.repositories.embedding_repository import EmbeddingRepository


class FAISSVectorRepository(VectorStoreRepository):
    """
    FAISS implementation of the vector store repository.
    """

    INDEX_NAME = FAISS_INDEX_NAME

    def __init__(
        self,
        embedding_provider: EmbeddingRepository,
        faiss_dir: Path | None = None,
    ):
        self.embedding_provider = embedding_provider
        self.faiss_dir = faiss_dir if faiss_dir is not None else settings.faiss_dir
        self.vector_store = None

    def _chunk_to_metadata(self, chunk: Chunk) -> dict:
        return {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "filename": chunk.metadata.filename,
            "page_number": chunk.metadata.page_number,
            "section": chunk.metadata.section,
        }

    def _metadata_from_dict(self, metadata: dict) -> Metadata:
        return Metadata(
            filename=metadata["filename"],
            page_number=metadata["page_number"],
            section=metadata.get("section"),
        )

    def _document_to_chunk(self, document: LangChainDocument) -> Chunk:
        metadata = document.metadata
        return Chunk(
            chunk_id=metadata["chunk_id"],
            document_id=metadata["document_id"],
            text=document.page_content,
            metadata=self._metadata_from_dict(metadata),
        )

    def _document_to_search_result(self, document: LangChainDocument, rank: int) -> SearchResult:
        return SearchResult(
            chunk=self._document_to_chunk(document),
            score=0.0,
            rank=rank,
        )

    def create(self, chunks: list[Chunk]) -> None:
        texts = [chunk.text for chunk in chunks]
        metadatas = [self._chunk_to_metadata(chunk) for chunk in chunks]

        # Note: LangChain's FAISS needs an object with an `embed_documents` method.
        # Our EmbeddingRepository has it.
        self.vector_store = FAISS.from_texts(
            texts=texts,
            embedding=self.embedding_provider,
            metadatas=metadatas,
        )

    def save(self) -> None:
        if self.vector_store is None:
            raise ValueError("Vector store has not been created.")

        self.faiss_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(
            folder_path=str(self.faiss_dir),
            index_name=self.INDEX_NAME,
        )

    def load(self) -> bool:
        index_file = self.faiss_dir / f"{self.INDEX_NAME}.faiss"
        if not index_file.exists():
            return False

        self.vector_store = FAISS.load_local(
            folder_path=str(self.faiss_dir),
            embeddings=self.embedding_provider,
            index_name=self.INDEX_NAME,
            allow_dangerous_deserialization=True,
        )
        return True

    def similarity_search(self, query: str, k: int = DEFAULT_TOP_K) -> list[SearchResult]:
        if self.vector_store is None:
            raise ValueError("Vector store has not been created.")

        documents = self.vector_store.similarity_search(query=query, k=k)
        return [
            self._document_to_search_result(document=doc, rank=idx)
            for idx, doc in enumerate(documents, start=1)
        ]

    def get_all_chunks(self) -> list[Chunk]:
        if self.vector_store is None:
            raise ValueError("Vector store has not been created.")

        return [
            self._document_to_chunk(doc)
            for doc in self.vector_store.docstore._dict.values()
        ]
