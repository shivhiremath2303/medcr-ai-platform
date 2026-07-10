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
        retriever: HybridRetriever | None = None,
        reranker: Reranker | None = None,
    ):
        """
        Initialize the retrieval service.

        Args:
            retriever:
                Optional HybridRetriever.
                Mainly used for testing.

            reranker:
                Optional Reranker.
                Mainly used for testing.
        """

        if retriever is None:
            from app.di import get_hybrid_retriever

            self.retriever = get_hybrid_retriever()
        else:
            self.retriever = retriever

        if reranker is None:
            from app.di import get_reranker

            self.reranker = get_reranker()
        else:
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
