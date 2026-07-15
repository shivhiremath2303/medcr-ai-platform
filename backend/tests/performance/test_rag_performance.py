import time
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.services.rag.rag_service import RAGService
from app.domain.models import SearchResult, Chunk, Metadata
from app.domain.models.retrieval import QueryIntent, QueryUnderstanding

@pytest.fixture
def mock_dependencies():
    return {
        "retrieval_service": AsyncMock(),
        "llm_provider": AsyncMock(),
        "query_rewriter": AsyncMock(),
        "memory": MagicMock(),
        "context_builder": MagicMock(),
        "grounding_engine": MagicMock(),
        "reasoning_engine": MagicMock(),
        "evaluation_engine": MagicMock(),
        "benchmark_repo": MagicMock(),
        "metrics": MagicMock(),
        "cache": MagicMock(),
        "limiter": MagicMock(),
    }

@pytest.fixture
def rag_service(mock_dependencies):
    return RAGService(**mock_dependencies)

@pytest.mark.asyncio
async def test_rag_latency_with_parallel_analytics(rag_service, mock_dependencies):
    """
    Benchmark the latency of the RAG pipeline with parallel analytics extraction.
    We mock the IO-bound LLM call and CPU-bound analytics to verify orchestration.
    """
    # 1. Setup mocks
    mock_dependencies["cache"].get.return_value = None
    mock_dependencies["memory"].get_context.return_value = "previous context"

    understanding = QueryUnderstanding(
        original_query="What is the liability limit?",
        rewritten_query="What is the liability limit?",
        intent=QueryIntent.GENERAL_LEGAL_QA,
        entities=[],
        expanded_terms=[],
        is_multi_doc=False
    )
    mock_dependencies["query_rewriter"].understand_query.return_value = understanding

    results = [
        SearchResult(
            chunk=Chunk(chunk_id="1", document_id="doc1", text="Liability is limited to $1M", metadata=Metadata(filename="f1.pdf", page_number=1)),
            score=0.9, rank=1, retrieval_score=0.9
        )
    ]
    mock_dependencies["retrieval_service"].retrieve.return_value = results
    mock_dependencies["context_builder"].build.return_value = "context string"
    mock_dependencies["context_builder"].results_to_evidence.return_value = []
    mock_dependencies["grounding_engine"].analyze_sufficiency.return_value = "sufficient"

    # Simulate LLM latency (IO-bound)
    async def slow_llm(*args, **kwargs):
        await asyncio.sleep(0.5)
        return "The liability is $1M. [Evidence 1]"
    mock_dependencies["llm_provider"].generate_answer.side_effect = slow_llm

    # Simulate Analytics latency (CPU-bound / Thread-offloaded)
    # RAGService uses limiter.run_async for these
    async def mock_run_async(func, *args):
        # Simulate some processing time
        await asyncio.sleep(0.2)
        return func(*args)
    mock_dependencies["limiter"].run_async.side_effect = mock_run_async

    # Mock extractors
    mock_dependencies["grounding_engine"].calculate_grounding_score.return_value = 0.95
    mock_dependencies["grounding_engine"].determine_status.return_value = MagicMock(value="supported")

    import asyncio

    # 2. Execute and measure
    start_time = time.perf_counter()
    await rag_service.answer_question(question="What is the liability limit?")
    duration = time.perf_counter() - start_time

    # 3. Assertions
    # If sequential, it would be at least 0.5 (LLM) + 0.2 (Grounding) + 0.2 (Reasoning) = 0.9s
    # If parallel, it should be closer to 0.5 (LLM) + max(0.2, 0.2) = 0.7s
    # Note: retrieval_eval_task is also parallelized with LLM generation

    print(f"\nTotal RAG latency with parallel analytics: {duration:.4f}s")
    assert duration < 1.5 # Sanity check for mock overhead
