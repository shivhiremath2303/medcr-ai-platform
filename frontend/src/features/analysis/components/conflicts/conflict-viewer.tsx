import { ConflictCard } from "./conflict-card";
import { LegalConflict } from "../../types";
import { Share2, Network } from "lucide-react";

const MOCK_CONFLICTS: LegalConflict[] = [
  {
    id: "c1",
    title: "Governing Law Inconsistency",
    description: "The main agreement specifies New York law, but the recent addendum references Delaware law for dispute resolution.",
    severity: "high",
    relationshipType: "Contradiction",
    reasoning: "Contradictory governing law clauses can lead to significant legal uncertainty and increased litigation costs in the event of a dispute. The addendum lacks a superseding clause regarding jurisdiction.",
    evidence: [
      {
        id: "e1",
        sourceDocument: "MSA_2023.pdf",
        snippet: "This agreement shall be governed by the laws of the State of New York...",
        confidence: 0.99
      },
      {
        id: "e2",
        sourceDocument: "Addendum_B.pdf",
        snippet: "Any disputes arising from this addendum shall be settled under Delaware law...",
        confidence: 0.95
      }
    ]
  },
  {
    id: "c2",
    title: "Data Retention Overlap",
    description: "Privacy Policy mandates 5 years retention, but Service Agreement mentions 7 years for financial records.",
    severity: "medium",
    relationshipType: "Overlap",
    reasoning: "While not a direct conflict if 'financial records' are a subset, the ambiguity might lead to non-compliance with the stricter Privacy Policy if not clearly delineated.",
    evidence: [
      {
        id: "e3",
        sourceDocument: "Privacy_Policy.pdf",
        snippet: "All personal data shall be deleted after 5 years...",
        confidence: 0.92
      }
    ]
  }
];

export function ConflictViewer() {
  return (
    <div className="max-w-4xl mx-auto py-4 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">Conflict Analysis</h2>
          <p className="text-sm text-muted-foreground">System identified {MOCK_CONFLICTS.length} potential legal conflicts across documents.</p>
        </div>
        <div className="flex gap-2">
           <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium border rounded-md hover:bg-muted transition-colors">
            <Network className="h-3.5 w-3.5" />
            Visual Graph
          </button>
        </div>
      </div>

      <div className="grid gap-4">
        {MOCK_CONFLICTS.map(conflict => (
          <ConflictCard key={conflict.id} conflict={conflict} />
        ))}
      </div>

      <div className="mt-12 h-64 border-2 border-dashed rounded-xl flex flex-col items-center justify-center bg-muted/20 text-center p-6">
        <div className="p-3 rounded-full bg-primary/10 mb-4">
          <Network className="h-8 w-8 text-primary" />
        </div>
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Relationship Graph Explorer</h3>
        <p className="text-xs text-muted-foreground mt-2 max-w-xs">
          Interactive visualization of document relationships and conflict clusters is currently under development.
        </p>
      </div>
    </div>
  );
}
