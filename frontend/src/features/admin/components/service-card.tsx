import { AdminServiceInfo } from "../types";
import { StatusBadge } from "./status-badge";
import { Cpu, Layers, ShieldCheck, Zap } from "lucide-react";

interface ServiceCardProps {
  service: AdminServiceInfo;
}

export function ServiceCard({ service }: ServiceCardProps) {
  return (
    <div className="rounded-xl border bg-card overflow-hidden shadow-sm hover:border-primary/20 transition-all group">
      <div className="p-4 border-b flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
            <Cpu className="h-4 w-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold">{service.name}</h4>
            <div className="flex items-center gap-2 mt-0.5">
               <span className="text-[10px] text-muted-foreground uppercase font-medium">{service.provider || "Internal"}</span>
               {service.version && (
                 <span className="text-[10px] px-1.5 py-0 rounded bg-muted text-muted-foreground">{service.version}</span>
               )}
            </div>
          </div>
        </div>
        <StatusBadge status={service.status} />
      </div>

      <div className="p-4 space-y-4">
        <p className="text-xs text-muted-foreground leading-relaxed">
          {service.description}
        </p>

        {service.modelName && (
          <div className="p-2.5 rounded-lg bg-muted/30 border space-y-1">
            <div className="flex items-center gap-1.5 text-[10px] font-bold text-muted-foreground uppercase">
              <Layers className="h-3 w-3" />
              Active Model
            </div>
            <p className="text-xs font-bold text-foreground">{service.modelName}</p>
          </div>
        )}

        {service.metrics && service.metrics.length > 0 && (
          <div className="grid grid-cols-2 gap-3 pt-2">
            {service.metrics.map((metric) => (
              <div key={metric.name} className="space-y-1">
                <div className="text-[10px] font-bold text-muted-foreground uppercase truncate">{metric.name}</div>
                <div className="flex items-end gap-1">
                  <span className="text-sm font-bold">{metric.value}</span>
                  {metric.unit && <span className="text-[10px] text-muted-foreground pb-0.5">{metric.unit}</span>}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Placeholder for future specific service controls */}
        <div className="pt-2 border-t border-dashed">
            <button className="text-[10px] font-bold text-primary hover:underline flex items-center gap-1">
                VIEW PERFORMANCE TRACES
                <Zap className="h-2.5 w-2.5" />
            </button>
        </div>
      </div>
    </div>
  );
}
