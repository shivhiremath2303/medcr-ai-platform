import { ClauseComparison as ComparisonType } from "../../types";
import { ClauseCard } from "./clause-card";
import { AlertCircle } from "lucide-react";

interface ClauseComparisonProps {
  comparison: ComparisonType;
}

export function ClauseComparison({ comparison }: ClauseComparisonProps) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
        <ClauseCard clause={comparison.original} type="original" />
        <ClauseCard clause={comparison.proposed} type="proposed" />
      </div>

      {comparison.conflicts.length > 0 && (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800">
          <div className="flex items-center gap-2 mb-2 text-red-800 dark:text-red-300">
            <AlertCircle className="h-4 w-4" />
            <h5 className="text-sm font-semibold">Detected Conflicts</h5>
          </div>
          <ul className="list-disc list-inside space-y-1">
            {comparison.conflicts.map((conflict, i) => (
              <li key={i} className="text-xs text-red-700 dark:text-red-400">{conflict}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
