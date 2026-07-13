import { Badge } from "@/shared/components/ui/badge";
import { cn } from "@/core/utils/cn";

interface RelationshipBadgeProps {
  type: string;
  className?: string;
}

export function RelationshipBadge({ type, className }: RelationshipBadgeProps) {
  return (
    <Badge
      variant="secondary"
      className={cn("bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300 border-purple-200", className)}
    >
      {type}
    </Badge>
  );
}
