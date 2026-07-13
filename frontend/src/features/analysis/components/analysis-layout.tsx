import React from "react";
import { AnalysisSidebar } from "./analysis-sidebar";
import { AnalysisToolbar } from "./analysis-toolbar";

interface AnalysisLayoutProps {
  children: React.ReactNode;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export function AnalysisLayout({ children, activeTab, onTabChange }: AnalysisLayoutProps) {
  return (
    <div className="flex flex-col h-[calc(100vh-120px)] border rounded-xl bg-card overflow-hidden">
      <AnalysisToolbar activeTab={activeTab} onTabChange={onTabChange} />
      <div className="flex flex-1 overflow-hidden">
        <AnalysisSidebar />
        <main className="flex-1 overflow-y-auto p-6 bg-muted/10">
          {children}
        </main>
      </div>
    </div>
  );
}
