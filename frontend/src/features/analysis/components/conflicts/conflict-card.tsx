import { LegalConflict } from "../../types";
import { SeverityBadge } from "../shared/severity-badge";
import { RelationshipBadge } from "../shared/relationship-badge";
import { FileText, MessageSquare, ChevronDown } from "lucide-react";
import { useState } from "react";
import { cn } from "@/core/utils/cn";

interface ConflictCardProps {
  conflict: LegalConflict;
}

export function ConflictCard({ conflict }: ConflictCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="rounded-xl border bg-card overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      <div className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <SeverityBadge severity={conflict.severity} />
              <RelationshipBadge type={conflict.relationshipType} />
            </div>
            <h4 className="text-base font-bold text-foreground mt-2">{conflict.title}</h4>
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 hover:bg-muted rounded-md transition-colors"
          >
            <ChevronDown className={cn("h-5 w-5 text-muted-foreground transition-transform", isExpanded && "rotate-180")} />
          </button>
        </div>

        <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
          {conflict.description}
        </p>

        {isExpanded && (
          <div className="mt-4 pt-4 border-t space-y-4 animate-in fade-in slide-in-from-top-2">
            <div>
              <h5 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-2">
                <MessageSquare className="h-3.5 w-3.5" />
                AI Reasoning
              </h5>
              <p className="text-sm bg-muted/30 p-3 rounded-lg border italic text-foreground/80">
                {conflict.reasoning}
              </p>
            </div>

            <div>
              <h5 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-2">
                <FileText className="h-3.5 w-3.5" />
                Supporting Evidence
              </h5>
              <div className="space-y-2">
                {conflict.evidence.map((ev) => (
                  <div key={ev.id} className="text-xs p-2 border rounded-md bg-card">
                    <div className="flex justify-between font-medium mb-1">
                      <span>{ev.sourceDocument}</span>
                      <span className="text-primary">{Math.round(ev.confidence * 100)}% Match</span>
                    </div>
                    <p className="text-muted-foreground italic">"{ev.snippet}"</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
