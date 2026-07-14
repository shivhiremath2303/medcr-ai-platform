import asyncio
from typing import List

from rank_bm25 import BM25Okapi  # type: ignore

from app.domain.models.chunk import Chunk
from app.domain.repositories.keyword_retriever import KeywordRetriever


class BM25Adapter(KeywordRetriever):
    """
    Adapter for BM25 retrieval with async scaling support.
    Implements Milestone 10.3.3.
    """

    def __init__(self):
        self.chunks: List[Chunk] = []
        self.bm25: BM25Okapi | None = None

    async def index(self, chunks: List[Chunk]) -> None:
        self.chunks = chunks
        # BM25 indexing is CPU intensive, but usually fast for small collections.
        # We assume this runs in worker pods (10.3.2).
        tokenized_documents = [chunk.text.split() for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_documents)

    async def search(self, query: str, k: int = 5) -> List[Chunk]:
        if self.bm25 is None:
            return []

        query_tokens = query.split()
        # Non-blocking return (BM25 calculation is extremely fast)
        return self.bm25.get_top_n(
            query_tokens,
            self.chunks,
            n=k,
        )
