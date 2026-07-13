import { SystemStatus } from "../types";
import { StatusBadge } from "./status-badge";
import { LucideIcon } from "lucide-react";
import { cn } from "@/core/utils/cn";

interface StatusCardProps {
  title: string;
  description: string;
  status: SystemStatus;
  icon: LucideIcon;
  lastUpdated?: string;
  metric?: string;
}

export function StatusCard({ title, description, status, icon: Icon, lastUpdated, metric }: StatusCardProps) {
  return (
    <div className="rounded-xl border bg-card p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="p-2 rounded-lg bg-muted/50">
          <Icon className={cn("h-5 w-5",
            status === "up" ? "text-primary" : status === "down" ? "text-destructive" : "text-yellow-500"
          )} />
        </div>
        <StatusBadge status={status} />
      </div>

      <div className="mt-4">
        <h3 className="text-sm font-bold text-foreground">{title}</h3>
        <p className="text-xs text-muted-foreground mt-1 line-clamp-1">{description}</p>
      </div>

      <div className="mt-4 flex items-center justify-between pt-4 border-t border-dashed">
        <div className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">
          {metric || "Operational"}
        </div>
        {lastUpdated && (
          <div className="text-[10px] text-muted-foreground">
            {lastUpdated}
          </div>
        )}
      </div>
    </div>
  );
}
