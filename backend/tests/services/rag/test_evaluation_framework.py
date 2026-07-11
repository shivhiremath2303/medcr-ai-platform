import pytest
from app.services.rag.evaluation_engine import EvaluationEngine
from app.domain.models import SearchResult, ReasoningReport, LegalIssue
from tests.fixtures.chunk_factory import make_chunk

@pytest.fixture
def engine():
    return EvaluationEngine()

def test_evaluate_retrieval_perfect_match(engine):
    chunk1 = make_chunk("c1", "text")
    results = [SearchResult(chunk=chunk1, score=0.9, rank=1)]

    metrics = engine.evaluate_retrieval(results, expected_ids=["c1"])

    assert metrics.precision_at_k == 1.0
    assert metrics.recall_at_k == 1.0
    assert metrics.mrr == 1.0
    assert metrics.ndcg == 1.0

def test_evaluate_retrieval_no_match(engine):
    chunk1 = make_chunk("c1", "text")
    results = [SearchResult(chunk=chunk1, score=0.9, rank=1)]

    metrics = engine.evaluate_retrieval(results, expected_ids=["c2"])

    assert metrics.precision_at_k == 0.0
    assert metrics.recall_at_k == 0.0
    assert metrics.mrr == 0.0

def test_evaluate_performance(engine):
    metrics = engine.evaluate_performance(
        retrieval_ms=100.0,
        total_ms=500.0,
        tokens_in=1000,
        tokens_out=500
    )

    assert metrics.retrieval_latency_ms == 100.0
    assert metrics.llm_latency_ms == 400.0
    assert metrics.estimated_cost_usd > 0
    # (1000 * 0.1 / 1M) + (500 * 0.4 / 1M) = 0.0001 + 0.0002 = 0.0003
    assert metrics.estimated_cost_usd == 0.0003

def test_generate_report(engine):
    retrieval = engine.evaluate_retrieval([], [])
    grounding = engine.evaluate_grounding("answer", [], 0.8)
    reasoning = engine.evaluate_reasoning(ReasoningReport())
    performance = engine.evaluate_performance(10, 20, 10, 10)

    report = engine.generate_report("query", retrieval, grounding, reasoning, performance)

    assert report.query == "query"
    assert report.overall_score >= 0.0
    assert report.hallucination_rate == 0.0
