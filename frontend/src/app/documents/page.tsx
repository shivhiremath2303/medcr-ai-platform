import { AppLayout } from "@/shared/layouts/app-layout";
import { DocumentManagement } from "@/features/documents/components/document-management";

export const metadata = {
  title: "Documents | Legal AI Platform",
  description: "Ingest and manage legal evidence for AI analysis.",
};

export default function DocumentsPage() {
  return (
    <AppLayout>
      <DocumentManagement />
    </AppLayout>
  );
}
