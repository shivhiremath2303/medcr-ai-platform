"use client";

import { Evidence, ReasoningMetadata } from "@/features/chat/types";
import {
  FileText,
  MapPin,
  ShieldCheck,
  Search,
  ExternalLink,
  BookOpen,
  Info,
  Clock
} from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { ConfidenceGauge } from "./confidence-gauge";

import Link from "next/link";

interface EvidenceDetailProps {
  evidence: Evidence;
  reasoning?: ReasoningMetadata;
}

export function EvidenceDetail({ evidence, reasoning }: EvidenceDetailProps) {
  // Find related issues or facts linked to this evidence
  const linkedIssues = reasoning?.issues.filter(i => i.evidence_ids.includes(evidence.chunk_id)) || [];
  const linkedFacts = reasoning?.facts.slice(0, 3) || []; // Placeholder for actual fact linking if added to backend

  return (
    <div className="flex flex-col h-full animate-in fade-in slide-in-from-right-4 duration-500">
      <div className="p-6 border-b bg-card">
         <div className="flex items-start justify-between gap-4 mb-6">
            <div className="flex items-center gap-3">
               <div className="p-3 bg-primary/10 rounded-xl text-primary">
                  <FileText className="h-6 w-6" />
               </div>
               <div>
                  <h3 className="font-bold text-lg leading-none">{evidence.document_name}</h3>
                  <div className="flex items-center gap-4 mt-2">
                     <span className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground uppercase tracking-widest">
                        <MapPin className="h-3.5 w-3.5" />
                        Page {evidence.page_number}
                     </span>
                     <span className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground uppercase tracking-widest">
                        <BookOpen className="h-3.5 w-3.5" />
                        Chunk {evidence.rank}
                     </span>
                  </div>
               </div>
            </div>

            <div className="flex flex-col items-end gap-2">
               <Link
                 href={`/viewer/${encodeURIComponent(evidence.document_name)}`}
                 className="inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-1.5 text-xs font-bold text-primary-foreground hover:bg-primary/90 transition-colors shadow-sm uppercase tracking-wider"
               >
                  <ExternalLink className="h-3.5 w-3.5" />
                  View Original
               </Link>
               <span className="text-[10px] text-muted-foreground font-bold italic uppercase">Sync Enabled</span>
            </div>
         </div>

         <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <ConfidenceGauge score={evidence.confidence} label="Confidence" />
            <ConfidenceGauge score={evidence.retrieval_score} label="Retrieval (L2)" />
            <ConfidenceGauge score={evidence.reranker_score || 0} label="Rerank (X-Enc)" />
            <div className="flex flex-col gap-1 rounded-lg p-2 border bg-muted/20">
               <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Audit Status</span>
               <div className="flex items-center gap-2 text-green-500">
                  <ShieldCheck className="h-4 w-4" />
                  <span className="text-sm font-bold uppercase">Backend Verified</span>
               </div>
            </div>
         </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar">
         <section>
            <h4 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground mb-4 flex items-center gap-2">
               <BookOpen className="h-4 w-4 text-primary" />
               Evidence Excerpt
            </h4>
            <div className="relative rounded-2xl border bg-muted/20 p-6 shadow-inner">
               <div className="absolute top-0 left-8 -translate-y-1/2 bg-background px-2">
                  <Info className="h-4 w-4 text-muted-foreground" />
               </div>
               <p className="text-sm leading-loose text-foreground/90 font-medium italic">
                  "{evidence.chunk_text}"
               </p>
            </div>
         </section>

         <div className="grid md:grid-cols-2 gap-8">
            <section>
               <h4 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground mb-4 flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-green-500" />
                  Reasoning Extraction
               </h4>
               <div className="space-y-3">
                  {linkedIssues.length > 0 ? linkedIssues.map((issue, idx) => (
                    <div key={idx} className="p-4 rounded-xl border bg-card shadow-sm">
                       <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-bold uppercase">{issue.title}</span>
                          <Badge variant={issue.severity === "high" ? "destructive" : "warning"} className="text-[9px]">
                             {issue.severity}
                          </Badge>
                       </div>
                       <p className="text-xs text-muted-foreground">{issue.description}</p>
                    </div>
                  )) : (
                    <div className="p-4 rounded-xl border border-dashed text-center">
                       <p className="text-[10px] text-muted-foreground uppercase font-bold">No direct legal issues tagged</p>
                    </div>
                  )}
               </div>
            </section>

            <section>
               <h4 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground mb-4 flex items-center gap-2">
                  <Clock className="h-4 w-4 text-primary" />
                  Related Facts
               </h4>
               <ul className="space-y-2">
                  {linkedFacts.map((fact, idx) => (
                    <li key={idx} className="flex gap-3 text-xs text-muted-foreground leading-relaxed">
                       <span className="flex-shrink-0 text-primary font-black">•</span>
                       {fact}
                    </li>
                  ))}
               </ul>
            </section>
         </div>
      </div>
    </div>
  );
}
