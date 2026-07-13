"use client";

import { TimelineCard } from "./timeline-card";
import { TimelineGroup } from "./timeline-group";
import { TimelineEvent } from "../../types";
import { Info } from "lucide-react";
import { motion } from "framer-motion";

const MOCK_EVENTS: Record<string, TimelineEvent[]> = {
  "2023": [
    {
      id: "1",
      date: "Oct 12, 2023",
      title: "Initial Contract Signature",
      description: "Service level agreement signed between MedCore and HealthPlus Systems.",
      tags: ["Contract", "Execution"],
      category: "Agreement",
      legalIssue: "Contract Formation",
      evidence: [
        {
          id: "ev1",
          sourceDocument: "SLA_Main_2023.pdf",
          page: 1,
          snippet: "Both parties agree to the terms as of October 12, 2023...",
          confidence: 0.98
        }
      ],
      citationCount: 1,
      confidenceScore: 0.99
    },
    {
      id: "2",
      date: "Nov 05, 2023",
      title: "Compliance Audit Started",
      description: "First quarter compliance review initiated by regulatory board for healthcare data privacy.",
      tags: ["Audit", "Compliance"],
      category: "Regulatory",
      legalIssue: "Data Privacy",
      evidence: [
        {
          id: "ev2",
          sourceDocument: "Audit_Log_Q4.pdf",
          page: 12,
          snippet: "Review of HIPAA compliance for patient data systems started.",
          confidence: 0.92
        }
      ],
      citationCount: 4,
      confidenceScore: 0.95
    }
  ],
  "2024": [
    {
      id: "3",
      date: "Jan 15, 2024",
      title: "Amendment #1 Proposed",
      description: "Request for modification of data storage retention policies from 5 to 7 years.",
      tags: ["Amendment", "Data Policy"],
      category: "Modification",
      legalIssue: "Document Retention",
      evidence: [
        {
          id: "ev3",
          sourceDocument: "Amend_1_Draft.docx",
          page: 2,
          snippet: "Proposed change: extend data retention from 5 to 7 years.",
          confidence: 0.95
        }
      ],
      citationCount: 2,
      confidenceScore: 0.97
    }
  ]
};

export function TimelineView() {
  return (
    <div className="max-w-4xl mx-auto py-4">
      <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">Chronological Case Timeline</h2>
          <p className="text-muted-foreground mt-1">Reconstructed sequence of legal events and document interactions.</p>
        </div>
      </div>

      <div className="relative">
        {Object.entries(MOCK_EVENTS).map(([year, events], idx) => (
          <motion.div
            key={year}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            <TimelineGroup label={year}>
              {events.map(event => (
                <TimelineCard key={event.id} event={event} />
              ))}
            </TimelineGroup>
          </motion.div>
        ))}
      </div>

      {/* Backend Limitation Notice */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="mt-12 p-6 border rounded-xl bg-muted/30 border-dashed text-center"
      >
        <div className="flex items-center justify-center gap-2 mb-2 text-muted-foreground">
            <Info className="h-4 w-4" />
            <span className="text-sm font-bold uppercase tracking-widest">Architectural Note</span>
        </div>
        <p className="text-sm text-muted-foreground max-w-lg mx-auto leading-relaxed">
          Real-time event extraction and cross-document reconciliation is currently processed as static snapshots.
          Dynamic streaming updates will be enabled in Milestone 11.
        </p>
      </motion.div>
    </div>
  );
}
