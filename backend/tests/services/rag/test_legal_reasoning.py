import pytest
from app.services.rag.rag_service import RAGService
from app.services.retrieval.context_builder import ContextBuilder
from app.services.rag.query_rewriter import QueryRewriter
from app.services.rag.grounding_engine import GroundingEngine
from app.services.rag.reasoning_engine import ReasoningEngine
from app.services.rag.evaluation_engine import EvaluationEngine
from app.infrastructure.storage.memory_conversation_repository import (
    MemoryConversationRepository,
)
from app.infrastructure.storage.memory_benchmark_repository import (
    MemoryBenchmarkRepository,
)
from tests.fixtures.fake_hybrid_retriever import FakeHybridRetriever
from tests.fixtures.fake_llm_provider import FakeLLMProvider
from tests.fixtures.chunk_factory import make_chunk
from app.domain.models.search_result import SearchResult

from app.core.observability.metrics import NoOpMetricsProvider, MetricsRegistry


def test_rag_service_extracts_legal_issues():
    # Setup
    chunk = make_chunk("chunk-1", "Liability clause details.")
    results = [SearchResult(chunk=chunk, score=0.9, rank=1, retrieval_score=0.9)]

    retriever = FakeHybridRetriever(results=results)

    answer_text = """
### Summary
The user is liable.

### Facts
- The contract was signed in 2023. [Evidence 1]

### Issues & Risks
- Issue: Contract Breach | Severity: High | Description: The user failed to pay. [Evidence 1]

### Timeline
- 2023-01-01: Contract Signed [Evidence 1]

### Entity Relationships
- Company A -> Employer -> Person B: Employment relationship.
    """

    llm = FakeLLMProvider(answer=answer_text)
    memory = MemoryConversationRepository(max_messages=10)
    context_builder = ContextBuilder()
    rewriter = QueryRewriter(llm_provider=llm)
    grounding_engine = GroundingEngine()
    reasoning_engine = ReasoningEngine()
    evaluation_engine = EvaluationEngine()
    benchmark_repo = MemoryBenchmarkRepository()
    metrics = MetricsRegistry(NoOpMetricsProvider())

    service = RAGService(
        retrieval_service=retriever,
        llm_provider=llm,
        query_rewriter=rewriter,
        memory=memory,
        context_builder=context_builder,
        grounding_engine=grounding_engine,
        reasoning_engine=reasoning_engine,
        evaluation_engine=evaluation_engine,
        benchmark_repo=benchmark_repo,
        metrics=metrics,
    )

    # Execute
    response = service.answer_question("What are the risks?", k=1)

    # Assert
    assert "reasoning_metadata" in response
    metadata = response["reasoning_metadata"]

    # Issues
    assert len(metadata["issues"]) == 1
    assert metadata["issues"][0].title == "Contract Breach"
    assert metadata["issues"][0].severity == "high"

    # Timeline
    assert len(metadata["timeline"]) == 1
    assert metadata["timeline"][0].date == "2023-01-01"

    # Relationships
    assert len(metadata["relationships"]) == 1
    assert metadata["relationships"][0].source == "Company A"
    assert metadata["relationships"][0].target == "Person B"
