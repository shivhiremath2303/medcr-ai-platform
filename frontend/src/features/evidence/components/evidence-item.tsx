"use client";

import { Evidence } from "@/features/chat/types";
import { cn } from "@/core/utils/cn";
import { FileText, ChevronRight, Target, MapPin } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";

interface EvidenceItemProps {
  evidence: Evidence;
  isSelected: boolean;
  onSelect: (id: string) => void;
}

export function EvidenceItem({ evidence, isSelected, onSelect }: EvidenceItemProps) {
  return (
    <button
      onClick={() => onSelect(evidence.chunk_id)}
      className={cn(
        "flex w-full flex-col gap-3 p-4 text-left transition-all border-b last:border-b-0 hover:bg-muted/50",
        isSelected ? "bg-accent border-l-4 border-l-primary" : "bg-card"
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 overflow-hidden">
          <FileText className={cn("h-4 w-4 shrink-0", isSelected ? "text-primary" : "text-muted-foreground")} />
          <span className="text-xs font-bold truncate max-w-[150px] uppercase tracking-tight">
            {evidence.document_name}
          </span>
        </div>
        <Badge variant={evidence.confidence >= 0.8 ? "success" : "warning"} className="text-[9px] px-1.5 h-4 font-black">
          {Math.round(evidence.confidence * 100)}%
        </Badge>
      </div>

      <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
        {evidence.chunk_text}
      </p>

      <div className="flex items-center gap-4 mt-1">
         <div className="flex items-center gap-1 text-[10px] font-bold text-muted-foreground uppercase">
            <MapPin className="h-3 w-3" />
            P.{evidence.page_number}
         </div>
         <div className="flex items-center gap-1 text-[10px] font-bold text-muted-foreground uppercase">
            <Target className="h-3 w-3" />
            Rank {evidence.rank}
         </div>
      </div>
    </button>
  );
}
