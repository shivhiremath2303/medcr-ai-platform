import { LegalClause } from "../../types";
import { Badge } from "@/shared/components/ui/badge";
import { Info } from "lucide-react";

interface ClauseCardProps {
  clause: LegalClause;
  type: "original" | "proposed";
}

export function ClauseCard({ clause, type }: ClauseCardProps) {
  return (
    <div className="flex flex-col h-full rounded-xl border bg-card overflow-hidden">
      <div className="px-4 py-2 border-b bg-muted/30 flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {type === "original" ? "Original Provision" : "Proposed Provision"}
        </span>
        {clause.citation && (
          <Badge variant="outline" className="text-[10px]">{clause.citation}</Badge>
        )}
      </div>
      <div className="p-4 flex-1">
        <h4 className="text-sm font-bold mb-3">{clause.title}</h4>
        <div className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
          {clause.content}
        </div>
      </div>
      <div className="px-4 py-2 border-t bg-muted/10 flex items-center gap-2">
        <Info className="h-3.5 w-3.5 text-muted-foreground" />
        <span className="text-[10px] text-muted-foreground">
          Metadata: {Object.entries(clause.metadata).map(([k, v]) => `${k}: ${v}`).join(", ")}
        </span>
      </div>
    </div>
  );
}
