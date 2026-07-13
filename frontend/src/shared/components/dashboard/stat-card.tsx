"use client"

import { memo } from "react";
import { cn } from "@/core/utils/cn";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  trend?: {
    value: number;
    isUp: boolean;
  };
  className?: string;
}

export const StatCard = memo(function StatCard({
  title,
  value,
  icon: Icon,
  description,
  trend,
  className
}: StatCardProps) {
  return (
    <div className={cn("rounded-xl border bg-card p-6 shadow-sm transition-all hover:shadow-md", className)}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-bold uppercase tracking-widest text-muted-foreground/70">{title}</p>
        <div className="p-2 rounded-lg bg-muted/50">
          <Icon className="h-4 w-4 text-muted-foreground" />
        </div>
      </div>
      <div className="mt-4 flex items-baseline gap-2">
        <h3 className="text-2xl font-black tracking-tight text-foreground">{value}</h3>
        {trend && (
          <span className={cn(
            "text-xs font-bold px-1.5 py-0.5 rounded",
            trend.isUp
              ? "text-green-600 bg-green-500/10"
              : "text-red-600 bg-red-500/10"
          )}>
            {trend.isUp ? "+" : "-"}{trend.value}%
          </span>
        )}
      </div>
      {description && (
        <p className="mt-2 text-xs font-medium text-muted-foreground">{description}</p>
      )}
    </div>
  );
});
