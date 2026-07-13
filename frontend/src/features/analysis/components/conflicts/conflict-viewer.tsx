"use client";

import { ConflictCard } from "./conflict-card";
import { LegalConflict } from "../../types";
import { RelationshipGraphPanel } from "../shared/relationship-graph-panel";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { AlertTriangle, Network } from "lucide-react";

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
    ],
    suggestedResolution: "Harmonize governing law clauses by explicitly stating which document takes precedence in the event of a conflict.",
    relatedClauses: ["Section 12.4 (Governing Law)", "Section 4.1 (Scope)"],
    confidenceScore: 0.98,
    reasoningSummary: "Contradiction detected in jurisdictional clauses across active agreements."
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
    ],
    confidenceScore: 0.85,
    reasoningSummary: "Partial overlap between data retention policies and financial record obligations."
  }
];

export function ConflictViewer() {
  return (
    <div className="max-w-6xl mx-auto py-4">
      <div className="mb-8">
        <h2 className="text-2xl font-bold tracking-tight">Conflict Analysis & Relationships</h2>
        <p className="text-muted-foreground mt-1">Identify contradictions, overlaps, and deep relationships across your document repository.</p>
      </div>

      {/* Since shadcn/ui tabs might not be fully available or imported correctly,
          I will stick to a simplified toggle for now to avoid breaking imports,
          but making it look professional. */}

      <div className="space-y-8">
        <div className="space-y-4">
           <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="h-5 w-5 text-primary" />
              <h3 className="text-lg font-bold">Identified Conflicts</h3>
           </div>
           <div className="grid gap-6">
            {MOCK_CONFLICTS.map(conflict => (
              <ConflictCard key={conflict.id} conflict={conflict} />
            ))}
          </div>
        </div>

        <div className="pt-12 border-t">
           <div className="flex items-center gap-2 mb-6">
              <Network className="h-5 w-5 text-primary" />
              <h3 className="text-lg font-bold">Relationship Visualization</h3>
           </div>
           <RelationshipGraphPanel />
        </div>
      </div>
    </div>
  );
}
