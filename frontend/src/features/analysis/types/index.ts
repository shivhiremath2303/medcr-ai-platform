export type Severity = "low" | "medium" | "high" | "critical";
export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface Evidence {
  id: string;
  sourceDocument: string;
  page?: number;
  snippet: string;
  confidence: number;
}

export interface TimelineEvent {
  id: string;
  date: string;
  title: string;
  description: string;
  evidence: Evidence[];
  tags: string[];
  // Future backend metadata
  legalIssue?: string;
  evidenceCount?: number;
  citationCount?: number;
  confidenceScore?: number;
  category?: string;
}

export interface LegalClause {
  id: string;
  title: string;
  content: string;
  metadata: Record<string, any>;
  citation?: string;
}

export interface ClauseComparison {
  original: LegalClause;
  proposed: LegalClause;
  differences: {
    type: "addition" | "deletion" | "modification";
    text: string;
    startIndex: number;
    endIndex: number;
  }[];
  conflicts: string[];
  // Future backend metadata
  legalImpact?: string;
  riskLevel?: RiskLevel;
  confidenceScore?: number;
}

export interface LegalConflict {
  id: string;
  title: string;
  description: string;
  severity: Severity;
  evidence: Evidence[];
  reasoning: string;
  relationshipType: string;
  // Future backend metadata
  suggestedResolution?: string;
  relatedClauses?: string[];
  confidenceScore?: number;
  reasoningSummary?: string;
}
