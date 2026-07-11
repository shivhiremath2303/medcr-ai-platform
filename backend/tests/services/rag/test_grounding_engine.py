import pytest
from app.services.rag.grounding_engine import GroundingEngine
from app.domain.models import Evidence, SearchResult, AnswerStatus, SufficiencyLevel
from tests.fixtures.chunk_factory import make_chunk

@pytest.fixture
def engine():
    return GroundingEngine()

def test_analyze_sufficiency_low_confidence(engine):
    results = [SearchResult(chunk=make_chunk("c1", "text"), score=0.1, rank=1)]
    level = engine.analyze_sufficiency(results, 0.1)
    assert level == SufficiencyLevel.INSUFFICIENT

def test_analyze_sufficiency_partial(engine):
    results = [SearchResult(chunk=make_chunk("c1", "text"), score=0.4, rank=1)]
    level = engine.analyze_sufficiency(results, 0.4)
    assert level == SufficiencyLevel.PARTIAL

def test_analyze_sufficiency_sufficient(engine):
    results = [
        SearchResult(chunk=make_chunk("c1", "text"), score=0.8, rank=1),
        SearchResult(chunk=make_chunk("c2", "text"), score=0.7, rank=2),
        SearchResult(chunk=make_chunk("c3", "text"), score=0.7, rank=3)
    ]
    level = engine.analyze_sufficiency(results, 0.8)
    assert level == SufficiencyLevel.SUFFICIENT

def test_calculate_grounding_score_with_citations(engine):
    evidence = [
        Evidence("d1", "n1", 1, "c1", "t1", 0.9, confidence=0.9, rank=1),
        Evidence("d2", "n2", 1, "c2", "t2", 0.8, confidence=0.8, rank=2)
    ]
    citations = ["[Evidence 1]", "[Evidence 2]"]
    score = engine.calculate_grounding_score(evidence, citations, SufficiencyLevel.SUFFICIENT, [])
    assert score > 0.8

def test_calculate_grounding_score_contradiction_penalty(engine):
    evidence = [Evidence("d1", "n1", 1, "c1", "t1", 0.9, confidence=0.9, rank=1)]
    score_no_conflict = engine.calculate_grounding_score(evidence, ["[Evidence 1]"], SufficiencyLevel.SUFFICIENT, [])
    score_with_conflict = engine.calculate_grounding_score(evidence, ["[Evidence 1]"], SufficiencyLevel.SUFFICIENT, ["Conflict info"])
    assert score_with_conflict < score_no_conflict

def test_detect_contradictions(engine):
    answer = "Analysis: Something here. Conflict: Evidence 1 says yes but Evidence 2 says no."
    conflicts = engine.detect_contradictions(answer)
    assert len(conflicts) == 1
    assert "Evidence 1 says yes" in conflicts[0]

def test_detect_missing_evidence(engine):
    answer = "I can't answer. Missing Evidence: The amendment from 2024."
    missing = engine.detect_missing_evidence(answer)
    assert len(missing) == 1
    assert "The amendment from 2024" in missing[0]

def test_validate_answer_invalid_citation(engine):
    evidence = [Evidence("d1", "n1", 1, "c1", "t1", 0.9, confidence=0.9, rank=1)]
    answer = "The user is correct [Evidence 1] and also [Evidence 2]."
    errors = engine.validate_answer(answer, evidence)
    assert len(errors) == 1
    assert "[Evidence 2]" in errors[0]
