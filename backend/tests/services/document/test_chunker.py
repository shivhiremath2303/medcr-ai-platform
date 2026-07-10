from uuid import UUID

from app.domain.models.document import Document
from app.domain.models.page import Page
from app.infrastructure.parser.langchain_chunker_adapter import LangChainChunkerAdapter


def build_document(text: str) -> Document:
    """
    Create a simple document for testing.
    """

    return Document(
        document_id="doc-001",
        filename="sample.pdf",
        pages=[
            Page(
                page_number=1,
                text=text,
            )
        ],
    )


def test_chunk_creation():
    """
    The chunker should create at least one chunk.
    """

    document = build_document("This is a short legal document.")

    chunker = LangChainChunkerAdapter(chunk_size=100, chunk_overlap=10)

    chunks = chunker.split_document(document)

    assert len(chunks) > 0


def test_document_metadata_preserved():
    """
    Document metadata should be copied to every chunk.
    """

    document = build_document("This is another legal document.")

    chunker = LangChainChunkerAdapter(chunk_size=100, chunk_overlap=10)

    chunks = chunker.split_document(document)

    for chunk in chunks:
        assert chunk.document_id == document.document_id
        assert chunk.metadata.filename == document.filename
        assert chunk.metadata.page_number == 1


def test_chunk_id_is_uuid():
    """
    Every chunk should receive a valid UUID.
    """

    document = build_document("Testing UUID generation.")

    chunker = LangChainChunkerAdapter(chunk_size=100, chunk_overlap=10)

    chunks = chunker.split_document(document)

    for chunk in chunks:
        UUID(chunk.chunk_id)


def test_empty_document():
    """
    Empty documents should produce zero chunks.
    """

    document = build_document("")

    chunker = LangChainChunkerAdapter(chunk_size=100, chunk_overlap=10)

    chunks = chunker.split_document(document)

    assert len(chunks) == 0


def test_long_document_creates_multiple_chunks():
    """
    Long documents should be split into multiple chunks.
    """

    text = "Legal Evidence " * 500

    document = build_document(text)

    chunker = LangChainChunkerAdapter(chunk_size=100, chunk_overlap=10)

    chunks = chunker.split_document(document)

    assert len(chunks) > 1
