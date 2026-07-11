import pytest
from app.services.rag.rag_service import RAGService
from app.services.retrieval.context_builder import ContextBuilder
from app.services.rag.query_rewriter import QueryRewriter
from app.infrastructure.storage.memory_conversation_repository import MemoryConversationRepository
from tests.fixtures.fake_hybrid_retriever import FakeHybridRetriever
from tests.fixtures.fake_llm_provider import FakeLLMProvider
from tests.fixtures.chunk_factory import make_chunk
from app.domain.models.search_result import SearchResult

def test_rag_service_returns_structured_evidence():
    # Setup
    chunk = make_chunk("chunk-1", "Evidence text about liability.")
    results = [SearchResult(chunk=chunk, score=0.9, rank=1, retrieval_score=0.9)]

    retriever = FakeHybridRetriever(results=results)
    llm = FakeLLMProvider(answer="Summary: liability found. Analysis: found in [Evidence 1]. Conclusion: liable.")
    memory = MemoryConversationRepository(max_messages=10)
    context_builder = ContextBuilder()
    rewriter = QueryRewriter(llm_provider=llm)

    service = RAGService(
        retrieval_service=retriever,
        llm_provider=llm,
        query_rewriter=rewriter,
        memory=memory,
        context_builder=context_builder
    )

    # Execute
    response = service.answer_question("Is there liability?", k=1)

    # Assert
    assert "answer" in response
    assert "summary" in response
    assert response["summary"] == "liability found."
    assert "citations" in response
    assert "[Evidence 1]" in response["citations"]
    assert len(response["evidence"]) == 1
    assert response["evidence"][0].chunk_text == "Evidence text about liability."
    assert response["confidence"] > 0.6
    assert response["sources"][0]["filename"] == "contract.pdf"

def test_rag_service_handles_missing_evidence():
    # Setup
    retriever = FakeHybridRetriever(results=[])
    llm = FakeLLMProvider()
    memory = MemoryConversationRepository(max_messages=10)
    context_builder = ContextBuilder()
    rewriter = QueryRewriter(llm_provider=llm)

    service = RAGService(
        retrieval_service=retriever,
        llm_provider=llm,
        query_rewriter=rewriter,
        memory=memory,
        context_builder=context_builder
    )

    # Execute
    response = service.answer_question("Where is the gold?", k=1)

    # Assert
    assert "No supporting evidence" in response["answer"]
    assert response["confidence"] == 0.0
    assert len(response["evidence"]) == 0
    assert response["citations"] == []

def test_confidence_calculation_with_reranker():
    # Setup
    context_builder = ContextBuilder()
    chunk = make_chunk("chunk-1", "text")

    # High reranker score
    res_high = SearchResult(chunk=chunk, score=5.0, rank=1, reranker_score=5.0)
    conf_high = context_builder._calculate_confidence(res_high)

    # Low reranker score
    res_low = SearchResult(chunk=chunk, score=-5.0, rank=1, reranker_score=-5.0)
    conf_low = context_builder._calculate_confidence(res_low)

    assert conf_high > 0.9
    assert conf_low < 0.1
