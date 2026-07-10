from dataclasses import dataclass

from .metadata import Metadata


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    text: str
    metadata: Metadata
