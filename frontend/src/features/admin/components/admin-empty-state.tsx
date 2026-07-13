import { ShieldAlert } from "lucide-react";

export function AdminEmptyState({
  title,
  description,
  onRetry
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4 text-center border-2 border-dashed rounded-2xl bg-muted/5">
      <div className="p-4 rounded-full bg-muted mb-6">
        <ShieldAlert className="h-10 w-10 text-muted-foreground" />
      </div>
      <h3 className="text-xl font-bold text-foreground">
        {title || "Management Console Unavailable"}
      </h3>
      <p className="text-sm text-muted-foreground mt-2 max-w-sm mx-auto leading-relaxed">
        {description || "We encountered an issue connecting to the core system administration services. Please verify your administrative permissions and check the system logs."}
      </p>

      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-8 px-6 py-2 bg-primary text-primary-foreground rounded-lg font-semibold text-sm hover:bg-primary/90 transition-colors shadow-sm"
        >
          RETRY CONNECTION
        </button>
      )}
    </div>
  );
}
