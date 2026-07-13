import { FileSearch } from "lucide-react";

export function AnalysisEmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      <div className="p-4 rounded-full bg-muted mb-4">
        <FileSearch className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold">No Analysis Data Found</h3>
      <p className="text-sm text-muted-foreground mt-2 max-w-sm">
        We couldn't find any analysis for the selected documents. Try uploading more documents or adjusting your filters.
      </p>
    </div>
  );
}
