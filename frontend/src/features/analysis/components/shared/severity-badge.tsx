import { Badge } from "@/shared/components/ui/badge";
import { Severity } from "../../types";
import { cn } from "@/core/utils/cn";

interface SeverityBadgeProps {
  severity: Severity;
  className?: string;
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const variants: Record<Severity, string> = {
    low: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300 border-blue-200",
    medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300 border-yellow-200",
    high: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300 border-orange-200",
    critical: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300 border-red-200",
  };

  return (
    <Badge
      variant="outline"
      className={cn("capitalize font-semibold", variants[severity], className)}
    >
      {severity}
    </Badge>
  );
}
