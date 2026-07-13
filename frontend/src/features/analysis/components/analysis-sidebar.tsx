import { SearchBar } from "./shared/search-bar";
import { AnalysisFilters } from "./shared/analysis-filters";
import { MetadataPanel } from "./shared/metadata-panel";

export function AnalysisSidebar() {
  return (
    <aside className="w-80 border-r bg-card hidden lg:flex flex-col">
      <div className="p-4 border-b">
        <SearchBar placeholder="Search analysis..." />
      </div>
      <div className="flex-1 overflow-y-auto">
        <div className="p-4 space-y-6">
          <AnalysisFilters />
          <MetadataPanel />
        </div>
      </div>
    </aside>
  );
}
