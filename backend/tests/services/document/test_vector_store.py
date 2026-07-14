from pathlib import Path

import pytest

from app.core.observability.concurrency import ConcurrencyLimiter
from app.core.observability.metrics import MetricsRegistry, NoOpMetricsProvider
from app.core.observability.resource_guard import ResourceGuard
from app.infrastructure.vectorstore.faiss_repository import FAISSVectorRepository
from tests.fixtures.chunk_factory import make_chunk
from tests.fixtures.fake_embeddings import FakeEmbeddingService


@pytest.fixture
def limiter():
    metrics = MetricsRegistry(NoOpMetricsProvider())
    guard = ResourceGuard(metrics)
    return ConcurrencyLimiter(guard)


@pytest.mark.asyncio
async def test_create_builds_faiss_index(tmp_path: Path, limiter):
    embedding_service = FakeEmbeddingService()

    vector_store = FAISSVectorRepository(
        embedding_provider=embedding_service,
        faiss_dir=tmp_path,
        index_name="test_index",
        default_top_k=3,
        limiter=limiter,
    )

    chunks = [
        make_chunk(
            "chunk-1",
            "The agreement begins here.",
        ),
        make_chunk(
            "chunk-2",
            "The defendant breached the contract.",
        ),
    ]

    await vector_store.create(chunks)

    assert vector_store.vector_store is not None

    indexed_documents = vector_store.vector_store.docstore._dict

    assert len(indexed_documents) == len(chunks)


@pytest.mark.asyncio
async def test_similarity_search_returns_ranked_results(tmp_path: Path, limiter):
    embedding_service = FakeEmbeddingService()

    vector_store = FAISSVectorRepository(
        embedding_provider=embedding_service,
        faiss_dir=tmp_path,
        index_name="test_index",
        default_top_k=3,
        limiter=limiter,
    )

    chunks = [
        make_chunk(
            "chunk-1",
            "The plaintiff signed the agreement.",
        ),
        make_chunk(
            "chunk-2",
            "The defendant breached the contract.",
        ),
        make_chunk(
            "chunk-3",
            "Damages were awarded by the court.",
        ),
    ]

    await vector_store.create(chunks)

    results = await vector_store.similarity_search(
        query="contract breach",
        k=2,
    )

    assert len(results) == 2

    first = results[0]

    assert first.rank == 1
    assert first.chunk.document_id == "doc-1"
    assert first.chunk.metadata.filename == "contract.pdf"
    assert first.chunk.metadata.page_number == 1
    assert isinstance(first.chunk.text, str)
    assert len(first.chunk.text) > 0

    second = results[1]

    assert second.rank == 2


@pytest.mark.asyncio
async def test_save_and_load_restores_vector_store(tmp_path: Path, limiter):
    embedding_service = FakeEmbeddingService()

    original_store = FAISSVectorRepository(
        embedding_provider=embedding_service,
        faiss_dir=tmp_path,
        index_name="test_index",
        default_top_k=3,
        limiter=limiter,
    )

    chunks = [
        make_chunk(
            "chunk-1",
            "The plaintiff signed the agreement.",
        ),
        make_chunk(
            "chunk-2",
            "The defendant breached the contract.",
        ),
    ]

    await original_store.create(chunks)
    await original_store.save()

    restored_store = FAISSVectorRepository(
        embedding_provider=embedding_service,
        faiss_dir=tmp_path,
        index_name="test_index",
        default_top_k=3,
        limiter=limiter,
    )

    assert await restored_store.load() is True

    results = await restored_store.similarity_search(
        query="contract",
        k=1,
    )

    assert len(results) == 1

    result = results[0]

    assert result.rank == 1
    assert result.chunk.document_id == "doc-1"
    assert result.chunk.metadata.filename == "contract.pdf"
    assert result.chunk.metadata.page_number == 1


@pytest.mark.asyncio
async def test_load_returns_false_when_index_does_not_exist(tmp_path: Path, limiter):
    vector_store = FAISSVectorRepository(
        embedding_provider=FakeEmbeddingService(),
        faiss_dir=tmp_path,
        index_name="test_index",
        default_top_k=3,
        limiter=limiter,
    )

    assert await vector_store.load() is False
    assert vector_store.vector_store is None


@pytest.mark.asyncio
async def test_save_does_nothing_when_vector_store_not_created(tmp_path: Path, limiter):
    # Updated: Implementation now returns early if None, no longer raises ValueError
    vector_store = FAISSVectorRepository(
        embedding_provider=FakeEmbeddingService(),
        faiss_dir=tmp_path,
        index_name="test_index",
        default_top_k=3,
        limiter=limiter,
    )

    await vector_store.save()  # Should not raise


@pytest.mark.asyncio
async def test_similarity_search_returns_empty_when_vector_store_not_created(
    tmp_path: Path, limiter
):
    # Updated: Implementation now returns empty list if not ready, no longer raises ValueError
    vector_store = FAISSVectorRepository(
        embedding_provider=FakeEmbeddingService(),
        faiss_dir=tmp_path,
        index_name="test_index",
        default_top_k=3,
        limiter=limiter,
    )

    results = await vector_store.similarity_search("contract")
    assert results == []


@pytest.mark.asyncio
async def test_get_all_chunks_returns_empty_when_vector_store_not_created(
    tmp_path: Path, limiter
):
    # Updated: Implementation now returns empty list if None, no longer raises ValueError
    vector_store = FAISSVectorRepository(
        embedding_provider=FakeEmbeddingService(),
        faiss_dir=tmp_path,
        index_name="test_index",
        default_top_k=3,
        limiter=limiter,
    )

    chunks = await vector_store.get_all_chunks()
    assert chunks == []


@pytest.mark.asyncio
async def test_get_all_chunks_returns_all_indexed_chunks(tmp_path: Path, limiter):
    vector_store = FAISSVectorRepository(
        embedding_provider=FakeEmbeddingService(),
        faiss_dir=tmp_path,
        index_name="test_index",
        default_top_k=3,
        limiter=limiter,
    )

    chunks = [
        make_chunk(
            "chunk-1",
            "The plaintiff signed the agreement.",
        ),
        make_chunk(
            "chunk-2",
            "The defendant breached the contract.",
        ),
        make_chunk(
            "chunk-3",
            "Damages were awarded by the court.",
        ),
    ]

    await vector_store.create(chunks)

    indexed_chunks = await vector_store.get_all_chunks()

    assert len(indexed_chunks) == len(chunks)

    chunk_ids = {chunk.chunk_id for chunk in indexed_chunks}

    assert chunk_ids == {
        "chunk-1",
        "chunk-2",
        "chunk-3",
    }

    for chunk in indexed_chunks:
        assert chunk.document_id == "doc-1"
        assert chunk.metadata.filename == "contract.pdf"
        assert chunk.metadata.page_number == 1
        assert chunk.metadata.section == "Introduction"
        assert isinstance(chunk.text, str)
        assert len(chunk.text) > 0
