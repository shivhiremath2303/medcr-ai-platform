import { InfrastructureStatus } from "../types";
import { Badge } from "@/shared/components/ui/badge";
import { cn } from "@/core/utils/cn";
import { Box, Cloud, GitBranch, Terminal } from "lucide-react";

interface InfrastructureCardProps {
  item: InfrastructureStatus;
}

export function InfrastructureCard({ item }: InfrastructureCardProps) {
  const statusConfig = {
    configured: { label: "Configured", class: "bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20" },
    integrated: { label: "Integrated", class: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20" },
    planned: { label: "Planned", class: "bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 border-yellow-500/20" },
    unavailable: { label: "Unavailable", class: "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20" },
  };

  const current = statusConfig[item.status];

  return (
    <div className="rounded-xl border bg-card p-4 flex items-start gap-4 hover:border-primary/20 transition-all">
      <div className="p-2.5 rounded-lg bg-muted text-muted-foreground shrink-0">
        <Box className="h-5 w-5" />
      </div>

      <div className="flex-1 space-y-1">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-bold text-foreground">{item.name}</h4>
          <Badge variant="outline" className={cn("text-[9px] px-1.5 py-0 font-bold", current.class)}>
            {current.label}
          </Badge>
        </div>
        <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
          {item.description}
        </p>
      </div>
    </div>
  );
}
