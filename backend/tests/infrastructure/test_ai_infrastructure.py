import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from typing import List

from app.infrastructure.llm.gemini_adapter import GeminiLLMAdapter
from app.infrastructure.embeddings.huggingface_adapter import HuggingFaceEmbeddingAdapter
from app.infrastructure.retrieval.cross_encoder_adapter import CrossEncoderAdapter
from app.domain.models import SearchResult, Chunk

@pytest.fixture
def mock_metrics():
    return MagicMock()

@pytest.fixture
def mock_limiter():
    limiter = AsyncMock()
    # limiter.run_in_thread just calls the function
    async def side_effect(func, *args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)
    limiter.run_in_thread.side_effect = side_effect
    return limiter

class TestGeminiLLMAdapter:
    @pytest.fixture
    def mock_client(self):
        return MagicMock()

    @pytest.fixture
    def adapter(self, mock_client, mock_metrics, mock_limiter):
        return GeminiLLMAdapter(
            client=mock_client,
            model_name="gemini-pro",
            metrics=mock_metrics,
            limiter=mock_limiter
        )

    @pytest.mark.asyncio
    async def test_generate_answer_success(self, adapter, mock_client):
        mock_response = MagicMock()
        mock_response.text = "Legal answer"
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 5
        mock_client.models.generate_content.return_value = mock_response

        answer = await adapter.generate_answer("What is law?", "Law is...")
        assert answer == "Legal answer"
        adapter.metrics.track_llm_call.assert_called()
        adapter.metrics.track_tokens.assert_called_with("gemini-pro", 10, 5)

    @pytest.mark.asyncio
    async def test_generate_answer_retry_success(self, adapter, mock_client):
        # Patch retry wait to speed up test
        with patch("tenacity.nap.time.sleep", return_value=None):
            mock_response = MagicMock()
            mock_response.text = "Eventually success"
            mock_response.usage_metadata = None

            # Fail twice, succeed third time
            mock_client.models.generate_content.side_effect = [
                RuntimeError("Transient error 1"),
                RuntimeError("Transient error 2"),
                mock_response
            ]

            answer = await adapter.generate_answer("Q", "C")
            assert answer == "Eventually success"
            assert mock_client.models.generate_content.call_count == 3

    @pytest.mark.asyncio
    async def test_generate_answer_circuit_breaker_trips(self, adapter, mock_client):
        with patch("tenacity.nap.time.sleep", return_value=None):
            mock_client.models.generate_content.side_effect = RuntimeError("Persistent failure")

            # Call enough times to trip the breaker (threshold=5)
            for _ in range(5):
                with pytest.raises(RuntimeError):
                    await adapter.generate_answer("Q", "C")

            # Next call should be blocked by circuit breaker without calling client
            with pytest.raises(RuntimeError, match="OPEN"):
                await adapter.generate_answer("Q", "C")

            assert mock_client.models.generate_content.call_count == 5

    @pytest.mark.asyncio
    async def test_stream_answer(self, adapter, mock_client):
        mock_chunk1 = MagicMock()
        mock_chunk1.text = "Part 1 "
        mock_chunk2 = MagicMock()
        mock_chunk2.text = "Part 2"

        async def mock_stream(*args, **kwargs):
            yield mock_chunk1
            yield mock_chunk2

        mock_client.aio.models.generate_content_stream.side_effect = mock_stream

        chunks = []
        async for chunk in adapter.stream_answer("Q", "C"):
            chunks.append(chunk)

        assert chunks == ["Part 1 ", "Part 2"]

    @pytest.mark.asyncio
    async def test_rewrite_question(self, adapter, mock_client):
        mock_response = MagicMock()
        mock_response.text = "Standalone question"
        mock_client.models.generate_content.return_value = mock_response

        rewritten = await adapter.rewrite_question("Q", "Context")
        assert rewritten == "Standalone question"

class TestHuggingFaceEmbeddingAdapter:
    @pytest.mark.asyncio
    async def test_aembed_documents(self, mock_limiter):
        with patch("app.infrastructure.embeddings.huggingface_adapter.HuggingFaceEmbeddings") as mock_hf_class:
            mock_hf_instance = mock_hf_class.return_value
            mock_hf_instance.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]

            adapter = HuggingFaceEmbeddingAdapter("model", mock_limiter)

            embeddings = await adapter.aembed_documents(["hi", "bye"])
            assert embeddings == [[0.1, 0.2], [0.3, 0.4]]
            mock_hf_instance.embed_documents.assert_called_once_with(["hi", "bye"])

    @pytest.mark.asyncio
    async def test_aembed_query(self, mock_limiter):
        with patch("app.infrastructure.embeddings.huggingface_adapter.HuggingFaceEmbeddings") as mock_hf_class:
            mock_hf_instance = mock_hf_class.return_value
            mock_hf_instance.embed_query.return_value = [0.1, 0.2]

            adapter = HuggingFaceEmbeddingAdapter("model", mock_limiter)

            embedding = await adapter.aembed_query("query")
            assert embedding == [0.1, 0.2]
            mock_hf_instance.embed_query.assert_called_once_with("query")

class TestCrossEncoderAdapter:
    @pytest.mark.asyncio
    async def test_rerank_success(self, mock_metrics, mock_limiter):
        from app.domain.models.metadata import Metadata
        with patch("app.infrastructure.retrieval.cross_encoder_adapter.CrossEncoder") as mock_ce_class:
            mock_ce_instance = mock_ce_class.return_value
            mock_ce_instance.predict.return_value = [0.1, 0.9, 0.5]

            adapter = CrossEncoderAdapter("reranker-model", mock_metrics, mock_limiter)

            meta = Metadata(filename="f1", page_number=1)
            results = [
                SearchResult(chunk=Chunk(text="c1", chunk_id="1", document_id="d1", metadata=meta), score=0.1, rank=1),
                SearchResult(chunk=Chunk(text="c2", chunk_id="2", document_id="d1", metadata=meta), score=0.1, rank=2),
                SearchResult(chunk=Chunk(text="c3", chunk_id="3", document_id="d1", metadata=meta), score=0.1, rank=3),
            ]

            reranked = await adapter.rerank("query", results, k=2)

            assert len(reranked) == 2
            assert reranked[0].chunk.text == "c2" # score 0.9
            assert reranked[0].score == 0.9
            assert reranked[0].rank == 1
            assert reranked[1].chunk.text == "c3" # score 0.5
            assert reranked[1].score == 0.5
            assert reranked[1].rank == 2

            mock_metrics.track_reranker.assert_called_once()

    @pytest.mark.asyncio
    async def test_rerank_failure(self, mock_metrics, mock_limiter):
        with patch("app.infrastructure.retrieval.cross_encoder_adapter.CrossEncoder") as mock_ce_class:
            mock_ce_instance = mock_ce_class.return_value
            mock_ce_instance.predict.side_effect = Exception("Inference error")

            adapter = CrossEncoderAdapter("model", mock_metrics, mock_limiter)
            results = [SearchResult(chunk=MagicMock(), score=0.1, rank=1)]

            with pytest.raises(RuntimeError, match="Reranking failed"):
                await adapter.rerank("query", results, k=1)

    @pytest.mark.asyncio
    async def test_rerank_empty(self, mock_metrics, mock_limiter):
        adapter = CrossEncoderAdapter("model", mock_metrics, mock_limiter)
        assert await adapter.rerank("query", [], k=5) == []

    @pytest.mark.asyncio
    async def test_lazy_loading(self, mock_metrics, mock_limiter):
        with patch("app.infrastructure.retrieval.cross_encoder_adapter.CrossEncoder") as mock_ce_class:
            adapter = CrossEncoderAdapter("model", mock_metrics, mock_limiter)
            assert adapter._model is None

            # Trigger lazy load
            _ = adapter.model
            assert adapter._model is not None
            mock_ce_class.assert_called_once_with("model")
