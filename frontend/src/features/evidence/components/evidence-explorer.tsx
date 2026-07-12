"use client";

import { useEvidenceStore } from "../hooks/use-evidence-store";
import { EvidenceItem } from "./evidence-item";
import { EvidenceDetail } from "./evidence-detail";
import { EmptyState } from "@/shared/components/dashboard/empty-state";
import { Search, History, Filter, ShieldAlert } from "lucide-react";
import { Input } from "@/shared/components/ui/input"; // We'll create this helper

export function EvidenceExplorer() {
  const { recentAnalysis, selectedEvidenceId, setSelectedEvidenceId } = useEvidenceStore();

  const selectedEvidence = recentAnalysis?.evidence.find(e => e.chunk_id === selectedEvidenceId);

  if (!recentAnalysis) {
    return (
      <div className="h-[calc(100vh-12rem)] flex items-center justify-center">
        <EmptyState
          title="No Active Investigation"
          description="The Evidence Explorer displays granular source data from your most recent AI investigation. Start a chat to populate this view."
          icon={Search}
          action={
            <a href="/chat" className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-primary-foreground shadow-lg hover:bg-primary/90 transition-all">
              Start Investigation
            </a>
          }
        />
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-10rem)] w-full overflow-hidden rounded-2xl border bg-card shadow-xl animate-in fade-in zoom-in-95 duration-500">
      {/* Evidence List */}
      <aside className="w-80 lg:w-96 flex flex-col border-r bg-muted/10">
        <div className="p-4 border-b bg-card">
           <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-black uppercase tracking-widest flex items-center gap-2">
                 <History className="h-4 w-4" />
                 Investigation Findings
              </h3>
              <button disabled className="p-1.5 hover:bg-muted rounded text-muted-foreground opacity-50">
                 <Filter className="h-4 w-4" />
              </button>
           </div>
           <div className="relative group">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
              <input
                type="text"
                placeholder="Filter findings..."
                className="w-full bg-muted/50 border-none rounded-lg pl-9 pr-4 py-2 text-xs focus:ring-1 focus:ring-ring outline-none"
              />
           </div>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar">
           {recentAnalysis.evidence.map((ev) => (
              <EvidenceItem
                key={ev.chunk_id}
                evidence={ev}
                isSelected={selectedEvidenceId === ev.chunk_id}
                onSelect={setSelectedEvidenceId}
              />
           ))}
        </div>

        <div className="p-4 border-t bg-muted/30">
           <div className="flex items-center justify-between text-[10px] font-bold uppercase text-muted-foreground">
              <span>Total Evidence: {recentAnalysis.evidence.length}</span>
              <span className="text-green-500">Verified</span>
           </div>
        </div>
      </aside>

      {/* Detail Panel */}
      <main className="flex-1 bg-background overflow-hidden relative">
         {selectedEvidence ? (
           <EvidenceDetail
             evidence={selectedEvidence}
             reasoning={recentAnalysis.reasoning_metadata}
           />
         ) : (
           <div className="h-full flex items-center justify-center">
              <div className="text-center opacity-30 select-none grayscale">
                 <ShieldAlert className="h-12 w-12 mx-auto mb-4" />
                 <p className="text-sm font-black uppercase tracking-[0.2em]">Select evidence to audit</p>
              </div>
           </div>
         )}
      </main>
    </div>
  );
}
