import { Badge } from "@/shared/components/ui/badge";
import { SystemStatus } from "../types";
import { cn } from "@/core/utils/cn";

interface StatusBadgeProps {
  status: SystemStatus;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const variants: Record<SystemStatus, { label: string; class: string }> = {
    up: { label: "Healthy", class: "bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20" },
    down: { label: "Critical", class: "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20" },
    degraded: { label: "Degraded", class: "bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 border-yellow-500/20" },
    unknown: { label: "Unknown", class: "bg-gray-500/10 text-gray-600 dark:text-gray-400 border-gray-500/20" },
  };

  const current = variants[status] || variants.unknown;

  return (
    <Badge variant="outline" className={cn("capitalize font-bold px-2 py-0.5 text-[10px]", current.class, className)}>
      <span className={cn("mr-1.5 h-1.5 w-1.5 rounded-full",
        status === "up" ? "bg-green-500" : status === "down" ? "bg-red-500" : "bg-yellow-500"
      )} />
      {current.label}
    </Badge>
  );
}
