"use client"

import dynamic from "next/dynamic";
import { AppLayout } from "@/shared/layouts/app-layout";
import { PageSkeleton } from "@/shared/components/loading/page-skeleton";

const DocumentManagement = dynamic(
  () => import("@/features/documents/components/document-management").then(mod => mod.DocumentManagement),
  {
    loading: () => <PageSkeleton />,
    ssr: false // Client-side heavy feature
  }
);

export default function DocumentsPage() {
  return (
    <AppLayout>
      <DocumentManagement />
    </AppLayout>
  );
}
