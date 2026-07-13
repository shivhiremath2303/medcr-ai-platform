import { Skeleton } from "../ui/skeleton"

export function PageSkeleton() {
  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="space-y-2">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-4 w-96" />
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-32 rounded-xl" />
        ))}
      </div>

      <div className="space-y-4 pt-8">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-6 md:grid-cols-2">
           <Skeleton className="h-64 rounded-xl" />
           <Skeleton className="h-64 rounded-xl" />
        </div>
      </div>
    </div>
  )
}
