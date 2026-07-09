from app.models.chunk import Chunk
from rank_bm25 import BM25Okapi


class BM25Retriever:
    """
    Keyword-based retriever using the BM25 algorithm.
    """

    def __init__(self):
        self.chunks: list[Chunk] = []
        self.tokenized_documents: list[list[str]] = []
        self.bm25: BM25Okapi | None = None

    # ----------------------------------------------------------
    # Index
    # ----------------------------------------------------------

    def index(
        self,
        chunks: list[Chunk],
    ) -> None:
        """
        Build the BM25 index.
        """

        self.chunks = chunks

        self.tokenized_documents = [chunk.text.split() for chunk in chunks]

        self.bm25 = BM25Okapi(
            self.tokenized_documents,
        )

    # ----------------------------------------------------------
    # Search
    # ----------------------------------------------------------

    def search(
        self,
        query: str,
        k: int = 5,
    ) -> list[Chunk]:
        """
        Search the indexed chunks.
        """

        if self.bm25 is None:
            return []

        query_tokens = query.split()

        return self.bm25.get_top_n(
            query_tokens,
            self.chunks,
            n=k,
        )
