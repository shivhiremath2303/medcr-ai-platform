import React from "react";

interface TimelineGroupProps {
  label: string;
  children: React.ReactNode;
}

export function TimelineGroup({ label, children }: TimelineGroupProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <h3 className="text-sm font-bold text-foreground whitespace-nowrap">{label}</h3>
        <div className="h-px w-full bg-border" />
      </div>
      <div className="pt-2">
        {children}
      </div>
    </div>
  );
}
