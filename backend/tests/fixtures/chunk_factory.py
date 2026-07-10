from app.domain.models.chunk import Chunk
from app.domain.models.metadata import Metadata


def make_chunk(
    chunk_id: str,
    text: str,
    *,
    document_id: str = "doc-1",
    filename: str = "contract.pdf",
    page_number: int = 1,
    section: str | None = "Introduction",
) -> Chunk:
    """
    Create a Chunk for testing.

    Default values can be overridden when a test
    needs specific metadata.
    """

    return Chunk(
        chunk_id=chunk_id,
        document_id=document_id,
        text=text,
        metadata=Metadata(
            filename=filename,
            page_number=page_number,
            section=section,
        ),
    )
