"use client";

import { TimelineEvent, Evidence } from "../../types";
import { Badge } from "@/shared/components/ui/badge";
import { FileText, ChevronRight, ExternalLink, ShieldCheck, Scale, Hash } from "lucide-react";
import { useState } from "react";
import { cn } from "@/core/utils/cn";
import { motion, AnimatePresence } from "framer-motion";

interface TimelineCardProps {
  event: TimelineEvent;
}

export function TimelineCard({ event }: TimelineCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Future-ready placeholders
  const confidence = event.confidenceScore ?? 0.85; // Placeholder if missing
  const evidenceCount = event.evidenceCount ?? event.evidence.length;
  const citationCount = event.citationCount ?? 0;
  const legalIssue = event.legalIssue ?? "General Compliance";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative pl-8 pb-8 group"
    >
      {/* Timeline connector */}
      <div className="absolute left-0 top-0 bottom-0 w-px bg-border group-last:bg-transparent" />

      {/* Timeline dot */}
      <div className="absolute left-[-4px] top-1.5 h-2 w-2 rounded-full bg-primary ring-4 ring-background z-10" />

      <div className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <time className="text-xs font-semibold text-primary bg-primary/10 px-2 py-0.5 rounded border border-primary/20">
            {event.date}
          </time>
          <div className="flex flex-wrap gap-2">
            {event.category && (
               <Badge variant="secondary" className="text-[10px] font-bold">{event.category}</Badge>
            )}
            {event.tags.map(tag => (
              <Badge key={tag} variant="outline" className="text-[10px] py-0 bg-background/50">{tag}</Badge>
            ))}
          </div>
        </div>

        <motion.div
          whileHover={{ scale: 1.005 }}
          className={cn(
            "rounded-xl border bg-card p-4 shadow-sm transition-all cursor-pointer",
            isExpanded ? "ring-2 ring-primary/20 border-primary/30" : "hover:border-primary/20 hover:shadow-md"
          )}
          onClick={() => setIsExpanded(!isExpanded)}
          role="button"
          aria-expanded={isExpanded}
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && setIsExpanded(!isExpanded)}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-foreground">{event.title}</h4>
              <div className="flex flex-wrap items-center gap-3 mt-1">
                 <div className="flex items-center gap-1 text-[11px] text-muted-foreground">
                   <Scale className="h-3 w-3" />
                   <span>{legalIssue}</span>
                 </div>
                 <div className="flex items-center gap-1 text-[11px] text-muted-foreground">
                   <ShieldCheck className="h-3 w-3" />
                   <span>{Math.round(confidence * 100)}% Confidence</span>
                 </div>
              </div>
            </div>
            <ChevronRight className={cn("h-5 w-5 text-muted-foreground transition-transform shrink-0", isExpanded && "rotate-90")} />
          </div>

          <p className={cn(
            "mt-2 text-sm text-muted-foreground leading-relaxed",
            !isExpanded && "line-clamp-2"
          )}>
            {event.description}
          </p>

          <div className="flex items-center gap-4 mt-4 pt-3 border-t">
            <div className="flex items-center gap-1.5">
              <div className="p-1 rounded bg-muted">
                <FileText className="h-3 w-3 text-muted-foreground" />
              </div>
              <span className="text-[11px] font-medium text-muted-foreground">{evidenceCount} Evidence</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="p-1 rounded bg-muted">
                <Hash className="h-3 w-3 text-muted-foreground" />
              </div>
              <span className="text-[11px] font-medium text-muted-foreground">{citationCount} Citations</span>
            </div>
          </div>

          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="mt-4 pt-4 border-t space-y-4">
                  <div className="space-y-3">
                    <h5 className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                      <FileText className="h-3.5 w-3.5" />
                      Evidence & Sources
                    </h5>
                    {event.evidence.map((ev: Evidence) => (
                      <div key={ev.id} className="flex flex-col sm:flex-row sm:items-start gap-3 p-3 rounded-lg bg-muted/30 border border-muted text-xs group/ev">
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="font-bold text-foreground">{ev.sourceDocument}</span>
                            <div className="flex items-center gap-2">
                               <span className="text-primary font-semibold">{Math.round(ev.confidence * 100)}% Match</span>
                               <ExternalLink className="h-3 w-3 text-muted-foreground cursor-pointer hover:text-primary transition-colors" />
                            </div>
                          </div>
                          <div className="text-[11px] text-muted-foreground mb-2 flex items-center gap-1">
                             <span className="px-1.5 py-0.5 bg-background rounded border">Page {ev.page ?? "N/A"}</span>
                          </div>
                          <p className="text-muted-foreground italic leading-relaxed border-l-2 border-primary/20 pl-3">
                            "{ev.snippet}"
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Future Metadata Placeholder */}
                  <div className="p-3 rounded-lg border border-dashed bg-muted/10">
                    <p className="text-[10px] text-muted-foreground text-center italic">
                      Additional cross-case analysis and legislative mapping will appear here when backend sync is enabled.
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </motion.div>
  );
}
