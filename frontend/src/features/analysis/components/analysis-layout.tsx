"use client";

import React from "react";
import { AnalysisSidebar } from "./analysis-sidebar";
import { AnalysisToolbar } from "./analysis-toolbar";
import { motion, AnimatePresence } from "framer-motion";

interface AnalysisLayoutProps {
  children: React.ReactNode;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export function AnalysisLayout({ children, activeTab, onTabChange }: AnalysisLayoutProps) {
  return (
    <div className="flex flex-col h-[calc(100vh-140px)] md:h-[calc(100vh-120px)] border rounded-xl bg-card overflow-hidden shadow-sm">
      <AnalysisToolbar activeTab={activeTab} onTabChange={onTabChange} />
      <div className="flex flex-1 overflow-hidden">
        <AnalysisSidebar />
        <main className="flex-1 overflow-y-auto bg-muted/5 relative custom-scrollbar">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="p-4 md:p-8 h-full"
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
