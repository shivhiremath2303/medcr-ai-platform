"use client";

import { Badge } from "@/shared/components/ui/badge";
import { cn } from "@/core/utils/cn";
import { Link2 } from "lucide-react";

interface RelationshipBadgeProps {
  type: string;
  className?: string;
}

export function RelationshipBadge({ type, className }: RelationshipBadgeProps) {
  return (
    <Badge
      variant="secondary"
      className={cn(
        "bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-400 border-purple-100 dark:border-purple-800 font-bold text-[10px] flex items-center gap-1 px-2 py-0.5",
        className
      )}
    >
      <Link2 className="h-3 w-3" />
      {type}
    </Badge>
  );
}
