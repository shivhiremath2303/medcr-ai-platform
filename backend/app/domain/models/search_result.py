from dataclasses import dataclass
from typing import Optional

from .chunk import Chunk


@dataclass
class SearchResult:
    chunk: Chunk
    score: float  # This will be the primary score used for ranking (either retrieval or rerank)
    rank: int
    retrieval_score: float | None = None
    reranker_score: float | None = None
