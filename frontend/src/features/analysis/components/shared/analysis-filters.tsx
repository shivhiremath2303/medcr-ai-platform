import { SectionHeader } from "./section-header";

export function AnalysisFilters() {
  const categories = ["All", "Contractual", "Regulatory", "Litigation", "Compliance"];

  return (
    <div className="space-y-4">
      <SectionHeader title="Filters" />
      <div className="space-y-2">
        <label className="text-xs font-medium text-muted-foreground uppercase">Category</label>
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              className="px-2 py-1 text-xs rounded-md border bg-background hover:bg-muted transition-colors"
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-medium text-muted-foreground uppercase">Confidence Score</label>
        <input type="range" className="w-full h-1.5 bg-muted rounded-lg appearance-none cursor-pointer accent-primary" />
        <div className="flex justify-between text-[10px] text-muted-foreground">
          <span>0%</span>
          <span>50%</span>
          <span>100%</span>
        </div>
      </div>
    </div>
  );
}
