import { Evidence, ChatResponse, ReasoningMetadata } from "@/features/chat/types";

export interface EvidenceAuditItem extends Evidence {
  audit_status?: "verified" | "flagged" | "pending";
  notes?: string;
}

export interface EvidenceWorkspaceState {
  recentAnalysis: ChatResponse | null;
  selectedEvidenceId: string | null;
  filters: {
    minConfidence: number;
    documentName: string | null;
  };
}
