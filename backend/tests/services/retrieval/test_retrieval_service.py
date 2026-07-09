from app.core.constants import (
    MIN_RETRIEVAL_CANDIDATES,
)
from app.models.search_result import SearchResult
from app.services.retrieval.retrieval_service import RetrievalService
from tests.fixtures.chunk_factory import make_chunk
from tests.fixtures.fake_hybrid_retriever import FakeHybridRetriever
from tests.fixtures.fake_reranker import FakeReranker

def test_retrieve_delegates_to_retriever_and_reranker():
    chunk_1 = make_chunk(
        "chunk-1",
        "The plaintiff signed the agreement.",
    )

    chunk_2 = make_chunk(
        "chunk-2",
        "The defendant breached the contract.",
    )

    candidates = [
        SearchResult(
            chunk=chunk_1,
            score=0.90,
            rank=1,
        ),
        SearchResult(
            chunk=chunk_2,
            score=0.80,
            rank=2,
        ),
    ]

    final_results = [
        candidates[1],
        candidates[0],
    ]

    retriever = FakeHybridRetriever(
        results=candidates,
    )

    reranker = FakeReranker(
        results=final_results,
    )

    service = RetrievalService(
        retriever=retriever,
        reranker=reranker,
    )

    results = service.retrieve(
        query="contract breach",
        k=5,
    )

    assert results == final_results

    assert retriever.queries == [
        "contract breach",
    ]

    assert retriever.k_values == [
        MIN_RETRIEVAL_CANDIDATES,
    ]

    assert reranker.queries == [
        "contract breach",
    ]

    assert reranker.received_results == [
        candidates,
    ]

    assert reranker.k_values == [
        5,
    ]
