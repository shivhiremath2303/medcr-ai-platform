import { Skeleton } from "@/shared/components/ui/skeleton";

export function AnalysisLoading() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="space-y-2">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-4 w-1/2" />
      </div>
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-32 w-full rounded-xl" />
        ))}
      </div>
    </div>
  );
}
