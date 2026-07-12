import { cn } from "@/core/utils/cn";

interface ConfidenceGaugeProps {
  score: number;
  label?: string;
  size?: "sm" | "md";
}

export function ConfidenceGauge({ score, label, size = "md" }: ConfidenceGaugeProps) {
  const percentage = Math.round(score * 100);

  const getColor = (s: number) => {
    if (s >= 0.8) return "text-green-600 dark:text-green-400";
    if (s >= 0.5) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
  };

  const getBg = (s: number) => {
    if (s >= 0.8) return "bg-green-500/10";
    if (s >= 0.5) return "bg-yellow-500/10";
    return "bg-red-500/10";
  };

  return (
    <div className={cn(
      "flex flex-col gap-1 rounded-lg p-2 border border-transparent",
      getBg(score),
    )}>
      <div className="flex items-center justify-between gap-4">
        {label && <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">{label}</span>}
        <span className={cn("text-sm font-black", getColor(score))}>{percentage}%</span>
      </div>
      <div className="h-1 w-full overflow-hidden rounded-full bg-muted/30">
        <div
          className={cn("h-full transition-all duration-1000",
            score >= 0.8 ? "bg-green-500" : score >= 0.5 ? "bg-yellow-500" : "bg-red-500"
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
