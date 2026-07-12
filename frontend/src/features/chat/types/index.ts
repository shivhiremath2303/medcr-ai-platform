export interface Evidence {
  document_id: string;
  document_name: string;
  page_number: number;
  chunk_id: string;
  chunk_text: string;
  retrieval_score: number;
  reranker_score?: number;
  confidence: number;
  rank: number;
}

export interface LegalIssue {
  title: string;
  description: string;
  severity: string;
  evidence_ids: string[];
}

export interface TimelineEvent {
  date: string;
  event: string;
  description: string;
  evidence_id: string;
}

export interface LegalRelationship {
  source: string;
  target: string;
  relationship_type: string;
  description: string;
}

export interface ReasoningMetadata {
  facts: string[];
  issues: LegalIssue[];
  timeline: TimelineEvent[];
  relationships: LegalRelationship[];
  conflicts: string[];
  uncertainties: string[];
}

export interface Evaluation {
  retrieval_ndcg: number;
  grounding_score: number;
  reasoning_consistency: number;
  hallucination_rate: number;
  overall_score: number;
  estimated_cost_usd: number;
}

export interface Source {
  filename: string;
  page_number: number;
}

export interface ChatRequest {
  question: string;
  k?: number;
}

export interface ChatResponse {
  answer: string;
  summary?: string;
  citations: string[];
  evidence: Evidence[];
  confidence: number;
  grounding_score: number;
  answer_status: "supported" | "partially_supported" | "insufficient_evidence" | "contradictory_evidence" | "outside_scope";
  missing_documents: string[];
  contradictions: string[];
  reasoning_notes?: string;
  reasoning_metadata?: ReasoningMetadata;
  evaluation?: Evaluation;
  sources: Source[];
  retrieval_diagnostics?: Record<string, any>;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  metadata?: ChatResponse;
  status: "sending" | "sent" | "error";
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
}
