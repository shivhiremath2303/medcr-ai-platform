import pytest

from app.infrastructure.retrieval.bm25_adapter import BM25Adapter
from tests.fixtures.chunk_factory import make_chunk


@pytest.mark.asyncio
async def test_index_builds_bm25_index():
    retriever = BM25Adapter()

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

    await retriever.index(chunks)

    assert retriever.bm25 is not None
    assert retriever.chunks == chunks


@pytest.mark.asyncio
async def test_search_returns_matching_chunks():
    retriever = BM25Adapter()

    chunk_1 = make_chunk(
        "chunk-1",
        "The plaintiff signed the agreement.",
    )

    chunk_2 = make_chunk(
        "chunk-2",
        "The defendant breached the contract.",
    )

    chunk_3 = make_chunk(
        "chunk-3",
        "Damages were awarded by the court.",
    )

    await retriever.index(
        [
            chunk_1,
            chunk_2,
            chunk_3,
        ]
    )

    results = await retriever.search(
        query="breached contract",
        k=2,
    )

    assert len(results) > 0

    result_ids = {chunk.chunk_id for chunk in results}

    assert "chunk-2" in result_ids


@pytest.mark.asyncio
async def test_search_returns_empty_when_not_indexed():
    retriever = BM25Adapter()

    results = await retriever.search(
        query="contract",
        k=5,
    )

    assert results == []


@pytest.mark.asyncio
async def test_search_respects_k_limit():
    retriever = BM25Adapter()

    chunks = [
        make_chunk(
            "chunk-1",
            "contract agreement",
        ),
        make_chunk(
            "chunk-2",
            "contract breach",
        ),
        make_chunk(
            "chunk-3",
            "contract damages",
        ),
    ]

    await retriever.index(chunks)

    results = await retriever.search(
        query="contract",
        k=2,
    )

    assert len(results) <= 2


@pytest.mark.asyncio
async def test_search_returns_empty_when_no_match():
    retriever = BM25Adapter()

    chunks = [
        make_chunk(
            "chunk-1",
            "agreement",
        ),
        make_chunk(
            "chunk-2",
            "contract",
        ),
    ]

    await retriever.index(chunks)

    results = await retriever.search(
        query="astronomy galaxy telescope",
        k=5,
    )

    assert isinstance(results, list)
