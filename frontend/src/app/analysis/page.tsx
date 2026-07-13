"use client";

import { useState } from "react";
import { AppLayout } from "@/shared/layouts/app-layout";
import { PageHeader } from "@/shared/components/dashboard/page-header";
import { AnalysisLayout } from "@/features/analysis/components/analysis-layout";
import { TimelineView } from "@/features/analysis/components/timeline/timeline-view";
import { ClauseComparisonView } from "@/features/analysis/components/comparison/clause-comparison-view";
import { ConflictViewer } from "@/features/analysis/components/conflicts/conflict-viewer";

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
      <PageHeader
        title="Legal Analysis Workspace"
        description="Explore chronological events, compare clauses, and identify document conflicts."
      />

      <AnalysisLayout activeTab={activeTab} onTabChange={setActiveTab}>
        {renderContent()}
      </AnalysisLayout>
    </AppLayout>
  );
}
