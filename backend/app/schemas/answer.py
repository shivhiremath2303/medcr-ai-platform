from pydantic import BaseModel, Field
from typing import List, Optional


class EvidenceSchema(BaseModel):
    """
    Detailed evidence object.
    """
    document_id: str
    document_name: str
    page_number: int
    chunk_id: str
    chunk_text: str
    retrieval_score: float
    reranker_score: Optional[float] = None
    confidence: float
    rank: int


class SourceResponse(BaseModel):
    """
    Source supporting the generated answer.
    """
    filename: str
    page_number: int


class AnswerResponse(BaseModel):
    """
    Response returned by the RAG endpoint.
    """
    answer: str
    summary: Optional[str] = None
    citations: List[str] = []
    evidence: List[EvidenceSchema] = []
    confidence: float = 0.0
    sources: List[SourceResponse] = []
