import { AppLayout } from "@/shared/layouts/app-layout";
import { EvidenceExplorer } from "@/features/evidence/components/evidence-explorer";
import { PageHeader } from "@/shared/components/dashboard/page-header";

export const metadata = {
  title: "Evidence Explorer | Legal AI Platform",
  description: "Independent audit and inspection of AI-retrieved legal evidence.",
};

export default function EvidencePage() {
  return (
    <AppLayout>
      <div className="h-full flex flex-col">
        <PageHeader
          title="Evidence Explorer"
          description="Independent audit and inspection of evidence retrieved from your legal corpus."
        />
        <div className="flex-1 min-h-0">
          <EvidenceExplorer />
        </div>
      </div>
    </AppLayout>
  );
}
