from dataclasses import dataclass
from typing import Optional


@dataclass
class Evidence:
    """
    Represents a specific piece of legal evidence retrieved from documents.
    """

    document_id: str
    document_name: str
    page_number: int
    chunk_id: str
    chunk_text: str
    retrieval_score: float
    reranker_score: Optional[float] = None
    confidence: float = 0.0
    rank: int = 0
