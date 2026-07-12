import pytest

from app.core.observability.metrics import MetricsRegistry, NoOpMetricsProvider
from app.domain.models.retrieval import QueryIntent, QueryUnderstanding
from app.domain.models.search_result import SearchResult
from app.services.retrieval.retrieval_service import RetrievalService
from tests.fixtures.chunk_factory import make_chunk
from tests.fixtures.fake_embeddings import FakeEmbeddingService
from tests.fixtures.fake_hybrid_retriever import FakeHybridRetriever
from tests.fixtures.fake_reranker import FakeReranker


@pytest.fixture
def service():
    metrics = MetricsRegistry(provider=NoOpMetricsProvider())
    retriever = FakeHybridRetriever(results=[])
    reranker = FakeReranker(results=[])
    return RetrievalService(retriever, reranker, metrics)


def test_dynamic_top_k_for_comparison(service):
    understanding = QueryUnderstanding(
        original_query="compare a and b",
        rewritten_query="compare a and b",
        intent=QueryIntent.COMPARISON,
        is_multi_doc=True,
    )
    k = service._calculate_dynamic_top_k(understanding, 5)
    assert k == 7  # 5 * 1.5


def test_strategy_for_definition(service):
    understanding = QueryUnderstanding(
        original_query="what is liability",
        rewritten_query="what is liability",
        intent=QueryIntent.DEFINITION,
    )
    strategy, weights = service._determine_strategy(understanding)
    assert strategy == "semantic_heavy"
    assert weights["vector"] == 0.9


def test_remove_duplicates(service):
    chunk = make_chunk("c1", "The quick brown fox.")
    results = [
        SearchResult(chunk=chunk, score=0.9, rank=1),
        SearchResult(chunk=chunk, score=0.8, rank=2),  # Duplicate
    ]
    unique = service._remove_duplicates(results)
    assert len(unique) == 1


def test_intelligent_retrieval_diagnostics(service):
    # Setup
    chunk = make_chunk("c1", "test")
    results = [SearchResult(chunk=chunk, score=0.9, rank=1)]
    service.retriever.results = results
    service.reranker.results = results

    understanding = QueryUnderstanding(
        original_query="termination clause",
        rewritten_query="termination clause",
        intent=QueryIntent.CLAUSE_LOOKUP,
        expanded_terms=["dismissal"],
    )

    final = service.retrieve_intelligent(understanding, k=5)

    assert len(final) == 1
    assert service.last_diagnostics is not None
    assert service.last_diagnostics.query_type == "clause_lookup"
    assert "dismissal" in service.last_diagnostics.expanded_terms
