from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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


class LegalIssueSchema(BaseModel):
    title: str
    description: str
    severity: str
    evidence_ids: List[str] = []


class TimelineEventSchema(BaseModel):
    date: str
    event: str
    description: str
    evidence_id: str


class LegalRelationshipSchema(BaseModel):
    source: str
    target: str
    relationship_type: str
    description: str


class ReasoningMetadataSchema(BaseModel):
    facts: List[str] = []
    issues: List[LegalIssueSchema] = []
    timeline: List[TimelineEventSchema] = []
    relationships: List[LegalRelationshipSchema] = []
    conflicts: List[str] = []
    uncertainties: List[str] = []


class SourceResponse(BaseModel):
    """
    Source supporting the generated answer.
    """

    filename: str
    page_number: int


class EvaluationSchema(BaseModel):
    retrieval_ndcg: float
    grounding_score: float
    citation_accuracy: float
    reasoning_consistency: float
    hallucination_rate: float
    overall_score: float
    estimated_cost_usd: float


class AnswerResponse(BaseModel):
    """
    Response returned by the RAG endpoint.
    """

    answer: str
    summary: Optional[str] = None
    citations: List[str] = []
    evidence: List[EvidenceSchema] = []
    confidence: float = 0.0
    grounding_score: float = 0.0
    answer_status: str = "supported"
    missing_documents: List[str] = []
    contradictions: List[str] = []
    reasoning_notes: Optional[str] = None
    reasoning_metadata: Optional[ReasoningMetadataSchema] = None
    evaluation: Optional[EvaluationSchema] = None
    sources: List[SourceResponse] = []
    retrieval_diagnostics: Optional[Dict[str, Any]] = None
