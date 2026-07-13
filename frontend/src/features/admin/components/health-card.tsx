import { SystemStatus } from "../types";
import { StatusBadge } from "./status-badge";
import { cn } from "@/core/utils/cn";
import { Activity, Clock, Server } from "lucide-react";

interface HealthCardProps {
  name: string;
  status: SystemStatus;
  message?: string;
  details?: Record<string, any>;
}

export function HealthCard({ name, status, message, details }: HealthCardProps) {
  return (
    <div className="rounded-xl border bg-card overflow-hidden">
      <div className="p-4 border-b flex items-center justify-between bg-muted/20">
        <div className="flex items-center gap-2">
          <Server className="h-4 w-4 text-muted-foreground" />
          <h4 className="text-sm font-bold">{name}</h4>
        </div>
        <StatusBadge status={status} />
      </div>

      <div className="p-4 space-y-4">
        {message && (
          <p className="text-xs text-muted-foreground leading-relaxed italic border-l-2 pl-3 py-1">
            "{message}"
          </p>
        )}

        <div className="grid grid-cols-2 gap-3">
          <div className="p-2 rounded-lg bg-muted/30 border space-y-1">
            <div className="flex items-center gap-1.5 text-[10px] font-bold text-muted-foreground uppercase">
              <Activity className="h-3 w-3" />
              Latency
            </div>
            <p className="text-xs font-medium">{details?.latency || "---"}ms</p>
          </div>
          <div className="p-2 rounded-lg bg-muted/30 border space-y-1">
            <div className="flex items-center gap-1.5 text-[10px] font-bold text-muted-foreground uppercase">
              <Clock className="h-3 w-3" />
              Uptime
            </div>
            <p className="text-xs font-medium">{details?.uptime || "99.9%"}</p>
          </div>
        </div>

        {details && Object.keys(details).length > 2 && (
          <div className="pt-2">
            <div className="text-[10px] font-bold text-muted-foreground uppercase mb-2">Metrics</div>
            <div className="space-y-1.5">
              {Object.entries(details).map(([key, value]) => {
                if (key === 'latency' || key === 'uptime' || key === 'status') return null;
                return (
                  <div key={key} className="flex justify-between text-[11px]">
                    <span className="text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</span>
                    <span className="font-medium">{String(value)}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
