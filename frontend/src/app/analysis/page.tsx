"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { AppLayout } from "@/shared/layouts/app-layout";
import { PageHeader } from "@/shared/components/dashboard/page-header";
import { AnalysisLayout } from "@/features/analysis/components/analysis-layout";
import { motion } from "framer-motion";
import { PageSkeleton } from "@/shared/components/loading/page-skeleton";

const TimelineView = dynamic(() => import("@/features/analysis/components/timeline/timeline-view").then(mod => mod.TimelineView), { loading: () => <PageSkeleton /> });
const ClauseComparisonView = dynamic(() => import("@/features/analysis/components/comparison/clause-comparison-view").then(mod => mod.ClauseComparisonView), { loading: () => <PageSkeleton /> });
const ConflictViewer = dynamic(() => import("@/features/analysis/components/conflicts/conflict-viewer").then(mod => mod.ConflictViewer), { loading: () => <PageSkeleton /> });

export default function AnalysisPage() {
  const [activeTab, setActiveTab] = useState("timeline");

  const renderContent = () => {
    switch (activeTab) {
      case "timeline":
        return <TimelineView />;
      case "comparison":
        return <ClauseComparisonView />;
      case "conflicts":
        return <ConflictViewer />;
      default:
        return <TimelineView />;
    }
  };

  return (
    <AppLayout>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <PageHeader
          title="Legal Analysis Workspace"
          description="Enterprise-grade environment for chronological reconstruction, clause risk assessment, and cross-document conflict detection."
        />
      </motion.div>

      <AnalysisLayout activeTab={activeTab} onTabChange={setActiveTab}>
        <div id={`${activeTab}-panel`} role="tabpanel" aria-labelledby={activeTab} className="h-full">
            {renderContent()}
        </div>
      </AnalysisLayout>
    </AppLayout>
  );
}
