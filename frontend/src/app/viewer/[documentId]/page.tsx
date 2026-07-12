import { AppLayout } from "@/shared/layouts/app-layout";
import { PdfViewer } from "@/features/pdf/components/pdf-viewer";
import { PageHeader } from "@/shared/components/dashboard/page-header";
import { ChevronLeft } from "lucide-react";
import Link from "next/link";

interface ViewerPageProps {
  params: Promise<{
    documentId: string;
  }>;
}

export default async function ViewerPage({ params }: ViewerPageProps) {
  const { documentId: encodedId } = await params;
  const documentId = decodeURIComponent(encodedId);

  return (
    <AppLayout>
      <div className="h-full flex flex-col">
        <div className="flex items-center gap-4 mb-4">
           <Link
             href="/evidence"
             className="p-2 hover:bg-accent rounded-lg text-muted-foreground transition-colors"
           >
              <ChevronLeft className="h-5 w-5" />
           </Link>
           <PageHeader
             title={documentId}
             description="Traceability View: Verifying AI claims against original source text."
             className="mb-0 flex-1"
           />
        </div>
        <div className="flex-1 min-h-0">
          <PdfViewer documentId={documentId} />
        </div>
      </div>
    </AppLayout>
  );
}
