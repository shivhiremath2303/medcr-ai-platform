"use client"

import dynamic from "next/dynamic";
import { AppLayout } from "@/shared/layouts/app-layout";
import { PageHeader } from "@/shared/components/dashboard/page-header";
import { PageSkeleton } from "@/shared/components/loading/page-skeleton";

const LegalChat = dynamic(
  () => import("@/features/chat/components/legal-chat").then(mod => mod.LegalChat),
  {
    loading: () => <PageSkeleton />,
    ssr: false
  }
);

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
