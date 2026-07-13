"use client";

import { LegalConflict, Evidence } from "../../types";
import { SeverityBadge } from "../shared/severity-badge";
import { RelationshipBadge } from "../shared/relationship-badge";
import { FileText, MessageSquare, ChevronDown, ShieldAlert, CheckCircle, List, ArrowRight } from "lucide-react";
import { useState } from "react";
import { cn } from "@/core/utils/cn";
import { motion, AnimatePresence } from "framer-motion";

interface ConflictCardProps {
  conflict: LegalConflict;
}

export function ConflictCard({ conflict }: ConflictCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Future-ready placeholders
  const suggestedResolution = conflict.suggestedResolution ?? "Harmonize governing law clauses by explicitly stating which document takes precedence in the event of a conflict.";
  const relatedClauses = conflict.relatedClauses ?? ["Section 12.4 (Governing Law)", "Section 4.1 (Scope)"];
  const confidence = conflict.confidenceScore ?? 0.88;
  const reasoningSummary = conflict.reasoningSummary ?? "Contradiction detected in jurisdictional clauses across active agreements.";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border bg-card overflow-hidden shadow-sm hover:shadow-md transition-all duration-200 border-l-4 border-l-primary/50"
    >
      <div className="p-5">
        <div className="flex items-start justify-between gap-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <SeverityBadge severity={conflict.severity} />
              <RelationshipBadge type={conflict.relationshipType} />
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-muted/50 border text-[10px] font-bold text-muted-foreground">
                <ShieldAlert className="h-3 w-3" />
                {Math.round(confidence * 100)}% Match
              </div>
            </div>
            <h4 className="text-base font-bold text-foreground leading-tight">{conflict.title}</h4>
            <p className="text-sm text-muted-foreground leading-relaxed max-w-3xl">
              {conflict.description}
            </p>
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className={cn(
              "p-2 hover:bg-muted rounded-full transition-colors shrink-0",
              isExpanded && "bg-muted text-primary"
            )}
            aria-label={isExpanded ? "Collapse" : "Expand"}
          >
            <ChevronDown className={cn("h-5 w-5 text-muted-foreground transition-transform duration-300", isExpanded && "rotate-180")} />
          </button>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-4 py-3 border-y border-dashed">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <FileText className="h-3.5 w-3.5 text-primary/70" />
                <span className="font-medium">{conflict.evidence.length} Evidence Chunks</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <List className="h-3.5 w-3.5 text-primary/70" />
                <span className="font-medium">{relatedClauses.length} Related Clauses</span>
            </div>
        </div>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="overflow-hidden"
            >
              <div className="mt-6 space-y-6">
                {/* Reasoning Summary */}
                <div className="p-4 rounded-lg bg-primary/5 border border-primary/10">
                   <h5 className="text-[11px] font-bold uppercase tracking-wider text-primary mb-2 flex items-center gap-2">
                    <MessageSquare className="h-3.5 w-3.5" />
                    AI reasoning Summary
                  </h5>
                  <p className="text-sm font-medium text-foreground/90">
                    {reasoningSummary}
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Detailed Reasoning */}
                  <div className="space-y-3">
                    <h5 className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                      <List className="h-3.5 w-3.5" />
                      Detailed Logic
                    </h5>
                    <p className="text-xs text-muted-foreground leading-relaxed italic p-3 rounded-lg border bg-muted/20">
                      {conflict.reasoning}
                    </p>
                  </div>

                  {/* Suggested Resolution */}
                  <div className="space-y-3">
                    <h5 className="text-[11px] font-bold uppercase tracking-wider text-green-600 dark:text-green-400 flex items-center gap-2">
                      <CheckCircle className="h-3.5 w-3.5" />
                      Suggested Resolution
                    </h5>
                    <div className="p-3 rounded-lg border border-green-100 dark:border-green-900 bg-green-50/30 dark:bg-green-900/10">
                        <p className="text-xs text-green-800 dark:text-green-300 leading-relaxed font-medium">
                            {suggestedResolution}
                        </p>
                        <button className="mt-3 flex items-center gap-1.5 text-[10px] font-bold text-green-600 dark:text-green-400 hover:underline">
                            CREATE REMEDIATION DRAFT
                            <ArrowRight className="h-3 w-3" />
                        </button>
                    </div>
                  </div>
                </div>

                {/* Evidence Panel */}
                <div className="space-y-3">
                  <h5 className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                    <FileText className="h-3.5 w-3.5" />
                    Supporting Evidence
                  </h5>
                  <div className="grid gap-3">
                    {conflict.evidence.map((ev: Evidence) => (
                      <div key={ev.id} className="p-3 rounded-lg border bg-card hover:bg-muted/30 transition-colors group/ev">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-bold text-foreground flex items-center gap-2">
                            <FileText className="h-3 w-3 text-primary" />
                            {ev.sourceDocument}
                          </span>
                          <span className="text-[10px] font-bold text-primary px-1.5 py-0.5 rounded bg-primary/10 border border-primary/20">
                            {Math.round(ev.confidence * 100)}% Match
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground italic leading-relaxed pl-4 border-l-2 border-muted">
                          "{ev.snippet}"
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Related Clauses Placeholder */}
                <div className="p-3 rounded-lg border border-dashed text-center">
                    <p className="text-[10px] text-muted-foreground italic">
                        Cross-document clause mapping is in BETA. Full traceability graph coming soon.
                    </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
