"use client";

import { cn } from "@/core/utils/cn";
import { Clock, Copy, AlertTriangle, Download, Share2, Scale } from "lucide-react";
import { motion } from "framer-motion";

interface AnalysisToolbarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export function AnalysisToolbar({ activeTab, onTabChange }: AnalysisToolbarProps) {
  const tabs = [
    { id: "timeline", label: "Timeline", icon: Clock },
    { id: "comparison", label: "Clause Comparison", icon: Copy },
    { id: "conflicts", label: "Conflict Viewer", icon: AlertTriangle },
  ];

  return (
    <nav
      className="flex items-center justify-between px-4 py-2 border-b bg-card z-10"
      aria-label="Analysis Workspace Navigation"
    >
      <div className="flex space-x-1 overflow-x-auto no-scrollbar pb-1 sm:pb-0" role="tablist">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-controls={`${tab.id}-panel`}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "relative flex items-center px-4 py-2 text-sm font-semibold rounded-md transition-all duration-200 whitespace-nowrap",
              activeTab === tab.id
                ? "text-primary"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
          >
            <tab.icon className={cn("w-4 h-4 mr-2", activeTab === tab.id ? "text-primary" : "text-muted-foreground")} />
            {tab.label}
            {activeTab === tab.id && (
              <motion.div
                layoutId="activeTab"
                className="absolute bottom-[-9px] left-0 right-0 h-[2px] bg-primary"
              />
            )}
          </button>
        ))}
      </div>

      <div className="flex items-center space-x-1 sm:space-x-2 shrink-0">
        <button
          title="Share Analysis"
          className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-md transition-colors"
          aria-label="Share Analysis"
        >
          <Share2 className="w-4 h-4" />
        </button>
        <button
          title="Download Report"
          className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-md transition-colors"
          aria-label="Download Report"
        >
          <Download className="w-4 h-4" />
        </button>
      </div>
    </nav>
  );
}
