from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LangChainDocument

from app.domain.models import Chunk, Metadata, SearchResult
from app.domain.repositories.embedding_repository import EmbeddingRepository
from app.domain.repositories.vector_store_repository import VectorStoreRepository


class FAISSVectorRepository(VectorStoreRepository):
    """
    FAISS implementation of VectorStoreRepository.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingRepository,
        faiss_dir: Path,
        index_name: str,
        default_top_k: int,
    ):
        self.embedding_provider = embedding_provider
        self.faiss_dir = faiss_dir
        self.index_name = index_name
        self.default_top_k = default_top_k
        self.vector_store: Optional[FAISS] = None

    def create(self, chunks: List[Chunk]) -> None:
        texts = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "filename": chunk.metadata.filename,
                "page_number": chunk.metadata.page_number,
                "section": chunk.metadata.section,
            }
            for chunk in chunks
        ]

        self.vector_store = FAISS.from_texts(
            texts=texts,
            embedding=self.embedding_provider,
            metadatas=metadatas,
        )

    def similarity_search(
        self, query: str, k: Optional[int] = None
    ) -> List[SearchResult]:
        if self.vector_store is None:
            raise ValueError("Vector store has not been created.")

        k = k or self.default_top_k
        docs_and_scores = self.vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=k,
        )

        results = []
        for rank, (doc, score) in enumerate(docs_and_scores, start=1):
            results.append(self._document_to_search_result(doc, score, rank))

        return results

    def _document_to_search_result(
        self, document: LangChainDocument, score: float, rank: int
    ) -> SearchResult:
        return SearchResult(
            chunk=Chunk(
                chunk_id=document.metadata["chunk_id"],
                document_id=document.metadata["document_id"],
                text=document.page_content,
                metadata=Metadata(
                    filename=document.metadata["filename"],
                    page_number=document.metadata["page_number"],
                    section=document.metadata.get("section"),
                ),
            ),
            score=score,
            rank=rank,
            retrieval_score=score,
        )

    def save(self) -> None:
        if self.vector_store is None:
            raise ValueError("Vector store has not been created.")

        self.faiss_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(
            folder_path=str(self.faiss_dir),
            index_name=self.index_name,
        )

    def load(self) -> bool:
        index_file = self.faiss_dir / f"{self.index_name}.faiss"
        if not index_file.exists():
            return False

        self.vector_store = FAISS.load_local(
            folder_path=str(self.faiss_dir),
            embeddings=self.embedding_provider,
            index_name=self.index_name,
            allow_dangerous_deserialization=True,
        )
        return True

    def get_all_chunks(self) -> List[Chunk]:
        if self.vector_store is None:
            raise ValueError("Vector store has not been created.")

        chunks = []
        docstore = self.vector_store.docstore
        # This is a bit internal to FAISS LangChain implementation
        for doc_id in self.vector_store.index_to_docstore_id.values():
            doc = docstore.search(doc_id)
            if isinstance(doc, LangChainDocument):
                chunks.append(
                    Chunk(
                        chunk_id=doc.metadata["chunk_id"],
                        document_id=doc.metadata["document_id"],
                        text=doc.page_content,
                        metadata=Metadata(
                            filename=doc.metadata["filename"],
                            page_number=doc.metadata["page_number"],
                            section=doc.metadata.get("section"),
                        ),
                    )
                )
        return chunks
