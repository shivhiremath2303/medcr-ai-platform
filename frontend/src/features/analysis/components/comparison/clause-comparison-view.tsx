import { ClauseComparison } from "./clause-comparison";
import { ClauseComparison as ComparisonType } from "../../types";

const MOCK_COMPARISON: ComparisonType = {
  original: {
    id: "o1",
    title: "Section 4.2: Termination for Convenience",
    content: "Either party may terminate this Agreement at any time upon sixty (60) days prior written notice to the other party.",
    metadata: { section: "4.2", source: "Master Service Agreement" },
    citation: "MSA-2023-4.2"
  },
  proposed: {
    id: "p1",
    title: "Section 4.2: Termination for Convenience (Amended)",
    content: "Either party may terminate this Agreement at any time upon ninety (90) days prior written notice to the other party, provided that termination by Service Provider shall only be effective after completion of all outstanding work orders.",
    metadata: { section: "4.2", source: "Amendment Draft" },
    citation: "AMD-2024-4.2"
  },
  differences: [
    { type: "modification", text: "ninety (90)", startIndex: 55, endIndex: 65 },
    { type: "addition", text: ", provided that termination by Service Provider shall only be effective after completion of all outstanding work orders.", startIndex: 100, endIndex: 200 }
  ],
  conflicts: [
    "Extended notice period may impact project timelines.",
    "Conditional termination for Service Provider creates asymmetry in contractual rights."
  ]
};

export function ClauseComparisonView() {
  return (
    <div className="max-w-6xl mx-auto py-4 space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold">Clause Comparison</h2>
          <p className="text-sm text-muted-foreground">Reviewing changes between original MSA and proposed Amendment #1.</p>
        </div>
      </div>

      <ClauseComparison comparison={MOCK_COMPARISON} />

      {/* Backend Limitation Notice */}
      <div className="p-4 border border-dashed rounded-lg bg-muted/50 text-center">
        <p className="text-sm text-muted-foreground">
          Dynamic diff highlighting is simulated. Full automated side-by-side comparison
          requires the Clause Analysis API (Planned for Q3).
        </p>
      </div>
    </div>
  );
}
