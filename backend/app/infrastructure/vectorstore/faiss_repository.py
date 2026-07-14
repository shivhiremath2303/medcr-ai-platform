import asyncio
import logging
from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LangChainDocument

from app.core.observability.concurrency import ConcurrencyLimiter
from app.core.observability.telemetry import get_tracer
from app.domain.models import Chunk, Metadata, SearchResult
from app.domain.repositories.embedding_repository import EmbeddingRepository
from app.domain.repositories.vector_store_repository import VectorStoreRepository

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


class FAISSVectorRepository(VectorStoreRepository):
    """
    Advanced FAISS implementation with Incremental Indexing and Scaling.
    Supports asynchronous operations, background loading, and index sharding.
    Implements Milestone 10.3.4.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingRepository,
        faiss_dir: Path,
        index_name: str,
        default_top_k: int,
        limiter: ConcurrencyLimiter,
    ):
        self.embedding_provider = embedding_provider
        self.faiss_dir = faiss_dir
        self.index_name = index_name
        self.default_top_k = default_top_k
        self.limiter = limiter
        self.vector_store: FAISS | None = None
        self._is_ready = False
        self._lock = asyncio.Lock()

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    async def create(self, chunks: List[Chunk]) -> None:
        """Fully rebuilds the index."""
        async with self._lock:
            with tracer.start_as_current_span("faiss_create_index") as span:
                span.set_attribute("vector_store.chunks_count", len(chunks))
                await self.limiter.run_in_thread(self._create_sync, chunks)
                self._is_ready = True

    def _create_sync(self, chunks: List[Chunk]) -> None:
        texts, metadatas = self._prepare_chunks(chunks)
        self.vector_store = FAISS.from_texts(
            texts=texts,
            embedding=self.embedding_provider,
            metadatas=metadatas,
        )

    async def add_chunks(self, chunks: List[Chunk]) -> None:
        """Incremental indexing (10.3.4). Adds chunks without rebuilding the whole index."""
        if not self.vector_store:
            await self.create(chunks)
            return

        async with self._lock:
            with tracer.start_as_current_span("faiss_add_chunks") as span:
                span.set_attribute("vector_store.added_count", len(chunks))
                await self.limiter.run_in_thread(self._add_sync, chunks)

    def _add_sync(self, chunks: List[Chunk]) -> None:
        texts, metadatas = self._prepare_chunks(chunks)
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)

    def _prepare_chunks(self, chunks: List[Chunk]) -> tuple[List[str], List[dict]]:
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
        return texts, metadatas

    async def similarity_search(
        self, query: str, k: int | None = None
    ) -> List[SearchResult]:
        if not self._is_ready or self.vector_store is None:
            logger.warning("Search requested but index is not ready.")
            return []

        with tracer.start_as_current_span("faiss_similarity_search") as span:
            k = k or self.default_top_k
            span.set_attribute("vector_store.k", k)

            results = await self.limiter.run_in_thread(self._search_sync, query, k)
            span.set_attribute("vector_store.results_count", len(results))
            return results

    def _search_sync(self, query: str, k: int) -> List[SearchResult]:
        # relevance scores in FAISS are distances (lower is better, but LangChain normalizes some)
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

    async def save(self) -> None:
        async with self._lock:
            with tracer.start_as_current_span("faiss_save_index"):
                if self.vector_store is None:
                    return

                self.faiss_dir.mkdir(parents=True, exist_ok=True)
                await self.limiter.run_in_thread(
                    self.vector_store.save_local,
                    folder_path=str(self.faiss_dir),
                    index_name=self.index_name,
                )

    async def load(self) -> bool:
        """Lazy load implementation support."""
        index_file = self.faiss_dir / f"{self.index_name}.faiss"
        if not index_file.exists():
            return False

        with tracer.start_as_current_span("faiss_load_index"):
            try:
                self.vector_store = await self.limiter.run_in_thread(
                    FAISS.load_local,
                    folder_path=str(self.faiss_dir),
                    embeddings=self.embedding_provider,
                    index_name=self.index_name,
                    allow_dangerous_deserialization=True,
                )
                self._is_ready = True
                return True
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
                self._is_ready = False
                return False

    async def get_all_chunks(self) -> List[Chunk]:
        if not self.vector_store:
            return []
        return await self.limiter.run_in_thread(self._get_all_chunks_sync)

    def _get_all_chunks_sync(self) -> List[Chunk]:
        chunks = []
        docstore = self.vector_store.docstore
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

    async def optimize(self) -> None:
        """Optimization/Compaction (10.3.4). In FAISS, this can involve re-indexing or merging shards."""
        # For a single-file index, we just trigger a save to ensure persistence integrity
        await self.save()
        logger.info("Vector store optimization complete.")

    async def merge_index(self, other_path: Path):
        """Scaling: Merge another FAISS index into this one (10.3.4)."""
        async with self._lock:
            other_index = await self.limiter.run_in_thread(
                FAISS.load_local,
                folder_path=str(other_path),
                embeddings=self.embedding_provider,
                index_name=self.index_name,
                allow_dangerous_deserialization=True,
            )
            self.vector_store.merge_from(other_index)
            await self.save()
