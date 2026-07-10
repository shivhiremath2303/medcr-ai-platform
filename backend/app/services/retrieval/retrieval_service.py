from app.core.constants import (
    MIN_RETRIEVAL_CANDIDATES,
    RETRIEVAL_CANDIDATE_MULTIPLIER,
)
from app.domain.models import SearchResult
from app.services.retrieval.hybrid_retriever import HybridRetriever
from app.services.retrieval.reranker import Reranker


class RetrievalService:
    """
    Retrieves and reranks the most relevant chunks.
    """

    def __init__(
        self,
        retriever: 'HybridRetriever',
        reranker: 'Reranker',
    ):
        """
        Initialize the retrieval service with required collaborators.

        Args:
            retriever: HybridRetriever implementation (injected)
            reranker: Reranker implementation (injected)
        """

        self.retriever = retriever
        self.reranker = reranker

    # ----------------------------------------------------------
    # Retrieval
    # ----------------------------------------------------------

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
