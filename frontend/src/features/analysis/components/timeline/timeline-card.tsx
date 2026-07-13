import { TimelineEvent } from "../../types";
import { Evidence } from "../../types";
import { Badge } from "@/shared/components/ui/badge";
import { FileText, ChevronRight, ExternalLink } from "lucide-react";
import { useState } from "react";
import { cn } from "@/core/utils/cn";

interface TimelineCardProps {
  event: TimelineEvent;
}

export function TimelineCard({ event }: TimelineCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="relative pl-8 pb-8 group">
      {/* Timeline connector */}
      <div className="absolute left-0 top-0 bottom-0 w-px bg-border group-last:bg-transparent" />

      {/* Timeline dot */}
      <div className="absolute left-[-4px] top-1.5 h-2 w-2 rounded-full bg-primary ring-4 ring-background" />

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <time className="text-xs font-medium text-muted-foreground bg-muted px-2 py-0.5 rounded">
            {event.date}
          </time>
          <div className="flex gap-2">
            {event.tags.map(tag => (
              <Badge key={tag} variant="outline" className="text-[10px] py-0">{tag}</Badge>
            ))}
          </div>
        </div>

        <div
          className={cn(
            "rounded-xl border bg-card p-4 shadow-sm transition-all hover:shadow-md cursor-pointer",
            isExpanded && "ring-1 ring-primary/50"
          )}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-start justify-between">
            <h4 className="text-sm font-semibold text-foreground">{event.title}</h4>
            <ChevronRight className={cn("h-4 w-4 text-muted-foreground transition-transform", isExpanded && "rotate-90")} />
          </div>
          <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
            {event.description}
          </p>

          {isExpanded && (
            <div className="mt-4 pt-4 border-t space-y-4 animate-in fade-in slide-in-from-top-2">
              <div className="space-y-2">
                <h5 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Evidence & Sources</h5>
                {event.evidence.map((ev: Evidence) => (
                  <div key={ev.id} className="flex items-start gap-3 p-2 rounded-md bg-muted/50 text-xs">
                    <FileText className="h-4 w-4 text-primary shrink-0" />
                    <div className="flex-1">
                      <div className="flex justify-between">
                        <span className="font-medium">{ev.sourceDocument} (Page {ev.page})</span>
                        <span className="text-primary font-medium">{Math.round(ev.confidence * 100)}% Confidence</span>
                      </div>
                      <p className="mt-1 text-muted-foreground italic">"{ev.snippet}"</p>
                    </div>
                    <ExternalLink className="h-3 w-3 text-muted-foreground cursor-pointer hover:text-foreground" />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
