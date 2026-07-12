import { Evidence } from "../types";
import { FileText, MapPin, Target } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";

interface EvidenceCardProps {
  evidence: Evidence;
}

export function EvidenceCard({ evidence }: EvidenceCardProps) {
  return (
    <div className="flex flex-col gap-3 p-4 border rounded-xl bg-muted/30 hover:bg-muted/50 transition-colors border-l-4 border-l-primary/40">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-primary/10 rounded text-primary">
            <FileText className="h-4 w-4" />
          </div>
          <div className="flex flex-col">
             <span className="text-sm font-semibold truncate max-w-[200px]">
               {evidence.document_name}
             </span>
             <div className="flex items-center gap-2 text-[10px] text-muted-foreground font-medium uppercase tracking-wider">
                <span className="flex items-center gap-1">
                   <MapPin className="h-2.5 w-2.5" />
                   Page {evidence.page_number}
                </span>
                <span className="flex items-center gap-1">
                   <Target className="h-2.5 w-2.5" />
                   Rank {evidence.rank}
                </span>
             </div>
          </div>
        </div>
        <Badge variant="secondary" className="text-[10px]">
          {Math.round(evidence.confidence * 100)}% Match
        </Badge>
      </div>

      <div className="relative">
        <p className="text-sm text-foreground/90 leading-relaxed italic line-clamp-4">
          "...{evidence.chunk_text}..."
        </p>
      </div>
    </div>
  );
}
