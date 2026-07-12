"use client";

import { create } from "zustand";
import { ChatResponse } from "@/features/chat/types";

interface EvidenceStore {
  recentAnalysis: ChatResponse | null;
  selectedEvidenceId: string | null;
  setRecentAnalysis: (analysis: ChatResponse) => void;
  setSelectedEvidenceId: (id: string | null) => void;
}

/**
 * Shared store to allow Evidence Explorer to consume results from Chat investigations.
 * This avoids duplicating API calls and maintains feature isolation.
 * Since we don't have a dedicated Evidence API yet, this is the most architectural way
 * to handle the data flow.
 */
export const useEvidenceStore = create<EvidenceStore>((set) => ({
  recentAnalysis: null,
  selectedEvidenceId: null,
  setRecentAnalysis: (analysis) => set({
    recentAnalysis: analysis,
    selectedEvidenceId: analysis.evidence[0]?.chunk_id || null
  }),
  setSelectedEvidenceId: (id) => set({ selectedEvidenceId: id }),
}));
