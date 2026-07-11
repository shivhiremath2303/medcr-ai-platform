from app.domain.models.search_result import SearchResult
from app.services.retrieval.retrieval_service import RetrievalService
from app.core.observability.metrics import NoOpMetricsProvider, MetricsRegistry
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

    metrics = MetricsRegistry(provider=NoOpMetricsProvider())

    service = RetrievalService(
        retriever=retriever,
        reranker=reranker,
        metrics=metrics,
        min_candidates=20,
        candidate_multiplier=4
    )

    results = service.retrieve(
        query="contract breach",
        k=5,
    )

    assert results == final_results

    assert retriever.queries == [
        "contract breach",
    ]

    # k * multiplier = 5 * 4 = 20. min_candidates = 20. max(20, 20) = 20.
    assert retriever.k_values == [
        20,
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
