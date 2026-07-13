"use client";

import { Info, FileText, Calendar, User, Cpu } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";

export function MetadataPanel() {
  const metadata = [
    { label: "AI Engine", value: "LegalAI-v2.1", icon: Cpu },
    { label: "Last Analysis", value: "2024-05-20", icon: Calendar },
    { label: "Document Set", value: "12 files", icon: FileText },
    { label: "Lead Counsel", value: "Unassigned", icon: User },
  ];

  return (
    <div className="space-y-4">
      <div className="rounded-xl border bg-muted/20 p-4 space-y-4">
        <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-bold text-muted-foreground uppercase">Session Info</span>
            <Badge variant="success" className="text-[9px] py-0 h-4">Production</Badge>
        </div>

        <div className="space-y-3">
          {metadata.map((item) => (
            <div key={item.label} className="flex justify-between items-center group">
              <div className="flex items-center gap-2">
                <item.icon className="h-3.5 w-3.5 text-muted-foreground group-hover:text-primary transition-colors" />
                <span className="text-[11px] text-muted-foreground">{item.label}</span>
              </div>
              <span className="text-[11px] font-bold text-foreground">{item.value}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="p-4 rounded-xl bg-blue-50/50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-800 space-y-2">
        <div className="flex items-center gap-2 text-blue-800 dark:text-blue-300">
            <Info className="h-3.5 w-3.5 shrink-0" />
            <span className="text-[10px] font-bold uppercase tracking-wider">Usage Note</span>
        </div>
        <p className="text-[11px] leading-relaxed text-blue-700 dark:text-blue-400 italic">
          This workspace uses Hybrid RAG and Graph Analysis. Cross-document reasoning is currently in high-accuracy mode.
        </p>
      </div>
    </div>
  );
}
