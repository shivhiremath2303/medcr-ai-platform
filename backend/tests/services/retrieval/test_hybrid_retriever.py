from app.models.search_result import SearchResult
from app.services.retrieval.hybrid_retriever import HybridRetriever
from tests.fixtures.chunk_factory import make_chunk
from tests.fixtures.fake_bm25_retriever import FakeBM25Retriever
from tests.fixtures.fake_vector_store import FakeVectorStore

def test_build_bm25_index_indexes_all_chunks():
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

    vector_store = FakeVectorStore(
        chunks=chunks,
        search_results=[],
    )

    bm25 = FakeBM25Retriever()

    HybridRetriever(
        vector_store=vector_store,
        bm25=bm25,
    )

    assert bm25.chunks == chunks


def test_retrieve_merges_vector_and_bm25_results():
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

    vector_results = [
        SearchResult(
            chunk=chunk_1,
            score=0.95,
            rank=1,
        ),
        SearchResult(
            chunk=chunk_2,
            score=0.90,
            rank=2,
        ),
    ]

    vector_store = FakeVectorStore(
        chunks=[
            chunk_1,
            chunk_2,
            chunk_3,
        ],
        search_results=vector_results,
    )

    bm25 = FakeBM25Retriever(
        search_results=[
            chunk_2,  # Duplicate
            chunk_3,  # New result
        ],
    )

    retriever = HybridRetriever(
        vector_store=vector_store,
        bm25=bm25,
    )

    results = retriever.retrieve(
        query="contract breach",
        k=3,
    )

    assert bm25.search_queries == [
        "contract breach",
    ]

    assert len(results) == 3

    assert results[0].chunk.chunk_id == "chunk-1"
    assert results[1].chunk.chunk_id == "chunk-2"
    assert results[2].chunk.chunk_id == "chunk-3"

    assert results[0].rank == 1
    assert results[1].rank == 2
    assert results[2].rank == 3


def test_retrieve_returns_only_vector_results_when_bm25_is_empty():
    chunk_1 = make_chunk(
        "chunk-1",
        "The plaintiff signed the agreement.",
    )

    chunk_2 = make_chunk(
        "chunk-2",
        "The defendant breached the contract.",
    )

    vector_results = [
        SearchResult(
            chunk=chunk_1,
            score=0.95,
            rank=1,
        ),
        SearchResult(
            chunk=chunk_2,
            score=0.90,
            rank=2,
        ),
    ]

    retriever = HybridRetriever(
        vector_store=FakeVectorStore(
            chunks=[
                chunk_1,
                chunk_2,
            ],
            search_results=vector_results,
        ),
        bm25=FakeBM25Retriever(),
    )

    results = retriever.retrieve(
        query="contract",
        k=5,
    )

    assert len(results) == 2

    assert results[0].chunk.chunk_id == "chunk-1"
    assert results[1].chunk.chunk_id == "chunk-2"


def test_retrieve_returns_only_bm25_results_when_vector_search_is_empty():
    chunk_1 = make_chunk(
        "chunk-1",
        "The plaintiff signed the agreement.",
    )

    chunk_2 = make_chunk(
        "chunk-2",
        "The defendant breached the contract.",
    )

    retriever = HybridRetriever(
        vector_store=FakeVectorStore(
            chunks=[
                chunk_1,
                chunk_2,
            ],
            search_results=[],
        ),
        bm25=FakeBM25Retriever(
            search_results=[
                chunk_1,
                chunk_2,
            ],
        ),
    )

    results = retriever.retrieve(
        query="agreement",
        k=5,
    )

    assert len(results) == 2

    assert results[0].chunk.chunk_id == "chunk-1"
    assert results[1].chunk.chunk_id == "chunk-2"

    assert results[0].rank == 1
    assert results[1].rank == 2
