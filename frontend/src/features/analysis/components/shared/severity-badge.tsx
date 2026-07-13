"use client";

import { Badge } from "@/shared/components/ui/badge";
import { Severity } from "../../types";
import { cn } from "@/core/utils/cn";
import { AlertCircle, AlertTriangle, Info, Skull } from "lucide-react";

interface SeverityBadgeProps {
  severity: Severity;
  className?: string;
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const configs: Record<Severity, { styles: string; icon: any }> = {
    low: {
        styles: "bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400 border-blue-200",
        icon: Info
    },
    medium: {
        styles: "bg-yellow-50 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400 border-yellow-200",
        icon: AlertTriangle
    },
    high: {
        styles: "bg-orange-50 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400 border-orange-200",
        icon: AlertCircle
    },
    critical: {
        styles: "bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400 border-red-200",
        icon: Skull
    },
  };

  const { styles, icon: Icon } = configs[severity];

  return (
    <Badge
      variant="outline"
      className={cn("capitalize font-bold flex items-center gap-1 px-2 py-0.5 text-[10px]", styles, className)}
    >
      <Icon className="h-3 w-3" />
      {severity}
    </Badge>
  );
}
