from app.core.constants import (
    MIN_RETRIEVAL_CANDIDATES,
    RETRIEVAL_CANDIDATE_MULTIPLIER,
)
from app.domain.models import SearchResult
from app.domain.repositories.retriever import Retriever
from app.domain.repositories.reranker import Reranker


class RetrievalService(Retriever):
    """
    Retrieves and reranks the most relevant chunks.
    Implements the Retriever interface.
    """

    def __init__(
        self,
        retriever: Retriever,
        reranker: Reranker,
    ):
        self.retriever = retriever
        self.reranker = reranker

    def retrieve(
        self,
        query: str,
        k: int = 5,
    ) -> list[SearchResult]:
        """
        Retrieve candidate results and rerank them.
        """

        candidate_count = max(
            k * RETRIEVAL_CANDIDATE_MULTIPLIER,
            MIN_RETRIEVAL_CANDIDATES,
        )

        candidates = self.retriever.retrieve(
            query=query,
            k=candidate_count,
        )

        return self.reranker.rerank(
            query=query,
            results=candidates,
            k=k,
        )
