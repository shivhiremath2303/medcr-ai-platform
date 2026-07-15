import asyncio
from typing import List, Optional

from rank_bm25 import BM25Okapi

from app.domain.models.chunk import Chunk
from app.domain.repositories.keyword_retriever import KeywordRetriever


class BM25Adapter(KeywordRetriever):
    """
    Adapter for BM25 retrieval with async scaling support.
    Enhanced with Multi-Tenant logical isolation (10.4.6).
    """

    def __init__(self):
        self.chunks: List[Chunk] = []
        self.bm25: BM25Okapi | None = None

    async def index(self, chunks: List[Chunk]) -> None:
        self.chunks = chunks
        # BM25 indexing is CPU intensive, but usually fast for small collections.
        tokenized_documents = [chunk.text.split() for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_documents)

    async def search(
        self,
        query: str,
        k: int = 5,
        tenant_id: Optional[str] = None
    ) -> List[Chunk]:
        if self.bm25 is None:
            return []

        # Multi-Tenant Filtering: Filter the chunk pool before searching
        # Note: For high performance at scale, we would use a tenant-indexed BM25 map.
        target_chunks = self.chunks
        if tenant_id:
            target_chunks = [
                c for c in self.chunks
                if getattr(c.metadata, "tenant_id", None) == tenant_id
            ]

        if not target_chunks:
            return []

        # Re-tokenize only the relevant subset for accurate scoring within tenant silo
        tokenized_subset = [chunk.text.split() for chunk in target_chunks]
        temp_bm25 = BM25Okapi(tokenized_subset)

        query_tokens = query.split()
        return temp_bm25.get_top_n(
            query_tokens,
            target_chunks,
            n=k,
        )
