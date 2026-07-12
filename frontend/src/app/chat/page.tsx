import { AppLayout } from "@/shared/layouts/app-layout";
import { LegalChat } from "@/features/chat/components/legal-chat";
import { PageHeader } from "@/shared/components/dashboard/page-header";

export const metadata = {
  title: "Legal AI Chat | Legal AI Platform",
  description: "Advanced RAG investigation and document querying.",
};

export default function ChatPage() {
  return (
    <AppLayout>
      <div className="h-full flex flex-col">
        <PageHeader
          title="Legal AI Chat"
          description="AI-powered investigation assistant using Hybrid Retrieval and Deep Reasoning."
        />
        <div className="flex-1 min-h-0">
          <LegalChat />
        </div>
      </div>
    </AppLayout>
  );
}
