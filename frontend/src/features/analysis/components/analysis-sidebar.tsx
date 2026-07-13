import { SearchBar } from "./shared/search-bar";
import { AnalysisFilters } from "./shared/analysis-filters";
import { MetadataPanel } from "./shared/metadata-panel";
import { SectionHeader } from "./shared/section-header";
import { Network, Search, Database, Filter } from "lucide-react";

export function AnalysisSidebar() {
  return (
    <aside className="w-80 border-r bg-card hidden lg:flex flex-col">
      {/* Search Header */}
      <div className="p-4 border-b space-y-3">
        <div className="flex items-center gap-2 mb-1">
            <Search className="h-4 w-4 text-primary" />
            <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Investigation</span>
        </div>
        <SearchBar placeholder="Search analysis workspace..." />
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <div className="p-4 space-y-8">
          {/* Evidence & Metadata Group */}
          <div className="space-y-4">
             <div className="flex items-center gap-2 px-1">
                <Database className="h-4 w-4 text-muted-foreground" />
                <SectionHeader title="Source & Context" />
             </div>
             <MetadataPanel />
          </div>

          {/* Filters Group */}
          <div className="space-y-4">
             <div className="flex items-center gap-2 px-1">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <SectionHeader title="Parameters" />
             </div>
             <AnalysisFilters />
          </div>

          {/* Future Graph Group */}
          <div className="p-4 rounded-xl border border-dashed bg-muted/20 space-y-3">
             <div className="flex items-center gap-2">
                <Network className="h-4 w-4 text-muted-foreground opacity-50" />
                <span className="text-[11px] font-bold text-muted-foreground/60 uppercase">Graph Intelligence</span>
             </div>
             <p className="text-[10px] text-muted-foreground/70 leading-relaxed italic">
               Cross-document entity linking and relationship clusters are being generated in the background.
             </p>
             <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-primary/20 w-1/3 animate-pulse" />
             </div>
          </div>
        </div>
      </div>

      {/* Status Footer */}
      <div className="p-3 border-t bg-muted/10">
          <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold text-muted-foreground uppercase">Analysis Engine</span>
              <div className="flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-[10px] font-medium">READY</span>
              </div>
          </div>
      </div>
    </aside>
  );
}
