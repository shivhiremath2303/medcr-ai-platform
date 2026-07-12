from rank_bm25 import BM25Okapi

from app.domain.models.chunk import Chunk
from app.domain.repositories.keyword_retriever import KeywordRetriever


class BM25Adapter(KeywordRetriever):
    """
    Adapter for BM25 retrieval.
    """

    def __init__(self):
        self.chunks: list[Chunk] = []
        self.bm25: BM25Okapi | None = None

    def index(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        tokenized_documents = [chunk.text.split() for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_documents)

    def search(self, query: str, k: int = 5) -> list[Chunk]:
        if self.bm25 is None:
            return []

        query_tokens = query.split()
        return self.bm25.get_top_n(
            query_tokens,
            self.chunks,
            n=k,
        )
