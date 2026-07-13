import { TimelineCard } from "./timeline-card";
import { TimelineGroup } from "./timeline-group";
import { TimelineEvent } from "../../types";

const MOCK_EVENTS: Record<string, TimelineEvent[]> = {
  "2023": [
    {
      id: "1",
      date: "Oct 12, 2023",
      title: "Initial Contract Signature",
      description: "Service level agreement signed between MedCore and HealthPlus Systems.",
      tags: ["Contract", "Execution"],
      evidence: [
        {
          id: "ev1",
          sourceDocument: "SLA_Main_2023.pdf",
          page: 1,
          snippet: "Both parties agree to the terms as of October 12, 2023...",
          confidence: 0.98
        }
      ]
    },
    {
      id: "2",
      date: "Nov 05, 2023",
      title: "Compliance Audit Started",
      description: "First quarter compliance review initiated by regulatory board.",
      tags: ["Audit", "Compliance"],
      evidence: [
        {
          id: "ev2",
          sourceDocument: "Audit_Log_Q4.pdf",
          page: 12,
          snippet: "Review of HIPAA compliance for patient data systems started.",
          confidence: 0.92
        }
      ]
    }
  ],
  "2024": [
    {
      id: "3",
      date: "Jan 15, 2024",
      title: "Amendment #1 Proposed",
      description: "Request for modification of data storage retention policies.",
      tags: ["Amendment", "Data Policy"],
      evidence: [
        {
          id: "ev3",
          sourceDocument: "Amend_1_Draft.docx",
          page: 2,
          snippet: "Proposed change: extend data retention from 5 to 7 years.",
          confidence: 0.95
        }
      ]
    }
  ]
};

export function TimelineView() {
  return (
    <div className="max-w-3xl mx-auto py-4">
      {Object.entries(MOCK_EVENTS).map(([year, events]) => (
        <TimelineGroup key={year} label={year}>
          {events.map(event => (
            <TimelineCard key={event.id} event={event} />
          ))}
        </TimelineGroup>
      ))}

      {/* Backend Limitation Notice */}
      <div className="mt-8 p-4 border border-dashed rounded-lg bg-muted/50 text-center">
        <p className="text-sm text-muted-foreground">
          Real-time timeline synchronization is currently unavailable.
          The data above is generated from static document analysis.
        </p>
      </div>
    </div>
  );
}
