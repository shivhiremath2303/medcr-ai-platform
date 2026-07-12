import { Badge } from "@/shared/components/ui/badge";
import { BookOpen } from "lucide-react";
import { cn } from "@/core/utils/cn";

interface CitationBadgeProps {
  citation: string;
  onClick?: () => void;
  className?: string;
}

export function CitationBadge({ citation, onClick, className }: CitationBadgeProps) {
  // Extract number from [Evidence 1]
  const match = citation.match(/\[Evidence (\d+)\]/);
  const number = match ? match[1] : "?";

  return (
    <Badge
      variant="secondary"
      className={cn(
        "cursor-pointer gap-1 px-1.5 py-0 text-[10px] font-bold hover:bg-primary hover:text-primary-foreground transition-all",
        className
      )}
      onClick={onClick}
    >
      <BookOpen className="h-2.5 w-2.5" />
      {number}
    </Badge>
  );
}
