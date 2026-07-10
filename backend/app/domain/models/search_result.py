from dataclasses import dataclass

from .chunk import Chunk


@dataclass
class SearchResult:
    chunk: Chunk
    score: float
    rank: int
