from pydantic import BaseModel


class ChunkMetadata(BaseModel):
    """
    Metadata describing where a chunk originated.
    """

    document_name: str
    page_number: int
    chunk_id: int


class Chunk(BaseModel):
    """
    Represents one searchable chunk of text.
    """

    text: str
    metadata: ChunkMetadata
