"use client";

import { ClauseComparison } from "./clause-comparison";
import { ClauseComparison as ComparisonType } from "../../types";
import { motion } from "framer-motion";

const MOCK_COMPARISON: ComparisonType = {
  original: {
    id: "o1",
    title: "Section 4.2: Termination for Convenience",
    content: "Either party may terminate this Agreement at any time upon sixty (60) days prior written notice to the other party.",
    metadata: { section: "4.2", source: "Master Service Agreement", page: 14 },
    citation: "MSA-2023-4.2"
  },
  proposed: {
    id: "p1",
    title: "Section 4.2: Termination for Convenience (Amended)",
    content: "Either party may terminate this Agreement at any time upon ninety (90) days prior written notice to the other party, provided that termination by Service Provider shall only be effective after completion of all outstanding work orders.",
    metadata: { section: "4.2", source: "Amendment Draft", page: 2 },
    citation: "AMD-2024-4.2"
  },
  differences: [
    { type: "modification", text: "ninety (90)", startIndex: 55, endIndex: 65 },
    { type: "addition", text: ", provided that termination by Service Provider shall only be effective after completion of all outstanding work orders.", startIndex: 100, endIndex: 200 }
  ],
  conflicts: [
    "Extended notice period (60 to 90 days) may impact project operational continuity.",
    "Conditional termination for Service Provider creates a unilateral obligation not present in original MSA."
  ],
  riskLevel: "high",
  legalImpact: "The proposed change significantly restricts the Service Provider's ability to exit the contract, effectively locking them in until all work orders are closed. This creates a high risk of 'perpetual service' if work orders are continuously issued.",
  confidenceScore: 0.94
};

export function ClauseComparisonView() {
  return (
    <div className="max-w-7xl mx-auto py-4 space-y-8">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:items-center justify-between gap-4"
      >
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Clause Comparison & Risk Analysis</h2>
          <p className="text-muted-foreground mt-1">Reviewing semantic and structural changes between original MSA and proposed Amendment #1.</p>
        </div>
      </motion.div>

      <ClauseComparison comparison={MOCK_COMPARISON} />

      {/* Backend Limitation Notice */}
      <div className="p-4 border border-dashed rounded-xl bg-muted/20 text-center">
        <p className="text-xs text-muted-foreground italic">
          Dynamic diff highlighting and automated risk scoring are simulated for this review.
          Full automated NLP side-by-side comparison requires the Clause Analysis API (Planned for Q4).
        </p>
      </div>
    </div>
  );
}
