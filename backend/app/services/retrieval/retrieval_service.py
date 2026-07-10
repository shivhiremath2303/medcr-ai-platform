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
        candidate_multiplier: int = 4,
        min_candidates: int = 20,
    ):
        self.retriever = retriever
        self.reranker = reranker
        self.candidate_multiplier = candidate_multiplier
        self.min_candidates = min_candidates

    def retrieve(
        self,
        query: str,
        k: int = 5,
    ) -> list[SearchResult]:
        """
        Retrieve candidate results and rerank them.
        """

        candidate_count = max(
            k * self.candidate_multiplier,
            self.min_candidates,
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
