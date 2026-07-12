"use client";

import { useState, useEffect } from "react";
import { PdfControls } from "./pdf-controls";
import { PdfRenderer } from "./pdf-renderer";
import { usePdfStore } from "../hooks/use-pdf-store";
import { EvidenceDetail } from "@/features/evidence/components/evidence-detail";
import { useEvidenceStore } from "@/features/evidence/hooks/use-evidence-store";
import {
  ChevronRight,
  ChevronLeft,
  BookOpen,
  ShieldAlert,
  PanelRightClose,
  PanelRight
} from "lucide-react";
import { cn } from "@/core/utils/cn";

interface PdfViewerProps {
  documentId: string;
}

export function PdfViewer({ documentId }: PdfViewerProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [zoom, setZoom] = useState(1.2);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const getBlob = usePdfStore(state => state.getBlob);
  const docBlob = getBlob(documentId);

  const { recentAnalysis, selectedEvidenceId, setSelectedEvidenceId } = useEvidenceStore();
  const selectedEvidence = recentAnalysis?.evidence.find(e => e.chunk_id === selectedEvidenceId);

  // Sync PDF page with selected evidence
  useEffect(() => {
    if (selectedEvidence) {
      setCurrentPage(selectedEvidence.page_number);
    }
  }, [selectedEvidence]);

  const onDownload = () => {
    if (!docBlob) return;
    const link = document.createElement("a");
    link.href = docBlob.url;
    link.download = docBlob.filename;
    link.click();
  };

  return (
    <div className="flex h-[calc(100vh-10rem)] w-full overflow-hidden rounded-2xl border bg-card shadow-xl animate-in fade-in zoom-in-95 duration-500">
      <div className="flex flex-col flex-1 min-w-0 bg-background">
        <PdfControls
          currentPage={currentPage}
          totalPages={totalPages}
          zoom={zoom}
          onPageChange={setCurrentPage}
          onZoomChange={setZoom}
          onDownload={onDownload}
        />

        {docBlob ? (
          <PdfRenderer
            url={docBlob.url}
            pageNumber={currentPage}
            zoom={zoom}
            onLoadSuccess={setTotalPages}
          />
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center p-12 text-center bg-muted/10">
             <div className="h-16 w-16 bg-muted rounded-full flex items-center justify-center mb-6">
                <ShieldAlert className="h-8 w-8 text-muted-foreground" />
             </div>
             <h3 className="text-xl font-bold mb-2">Remote Document Unavailable</h3>
             <p className="text-sm text-muted-foreground max-w-sm">
               The backend currently supports real-time indexing but does not yet expose a binary retrieval API.
               Only documents uploaded in the current session are viewable.
             </p>
          </div>
        )}
      </div>

      {/* Evidence Side Panel */}
      <aside className={cn(
        "border-l bg-muted/5 transition-all duration-300 relative flex flex-col",
        isSidebarOpen ? "w-[400px]" : "w-0"
      )}>
        <button
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="absolute left-0 top-1/2 -translate-x-1/2 z-30 bg-card border shadow-md p-1 rounded-full hover:bg-accent transition-colors"
        >
          {isSidebarOpen ? <PanelRightClose className="h-4 w-4" /> : <PanelRight className="h-4 w-4" />}
        </button>

        {isSidebarOpen && (
          <div className="flex flex-col h-full overflow-hidden">
            <header className="p-4 border-b bg-card flex items-center justify-between shrink-0">
               <h3 className="text-xs font-black uppercase tracking-widest flex items-center gap-2">
                  <BookOpen className="h-4 w-4 text-primary" />
                  Contextual Evidence
               </h3>
               <span className="text-[10px] font-bold text-muted-foreground uppercase">
                 {recentAnalysis?.evidence.length || 0} Found
               </span>
            </header>

            <div className="flex-1 overflow-y-auto custom-scrollbar bg-background">
               {recentAnalysis?.evidence.map(ev => (
                 <button
                   key={ev.chunk_id}
                   onClick={() => setSelectedEvidenceId(ev.chunk_id)}
                   className={cn(
                     "w-full p-4 text-left border-b last:border-b-0 hover:bg-muted/50 transition-colors relative",
                     selectedEvidenceId === ev.chunk_id && "bg-accent after:absolute after:left-0 after:top-0 after:bottom-0 after:w-1 after:bg-primary"
                   )}
                 >
                    <div className="flex items-center justify-between mb-1">
                       <span className="text-[10px] font-black uppercase text-muted-foreground tracking-tighter">
                         Page {ev.page_number}
                       </span>
                       <span className="text-[10px] font-bold text-green-500">
                         {Math.round(ev.confidence * 100)}%
                       </span>
                    </div>
                    <p className="text-xs leading-relaxed line-clamp-3 italic text-foreground/80">
                      "{ev.chunk_text}"
                    </p>
                 </button>
               ))}

               {!recentAnalysis && (
                 <div className="p-12 text-center text-muted-foreground opacity-50 select-none grayscale">
                    <ShieldAlert className="h-10 w-10 mx-auto mb-4" />
                    <p className="text-[10px] font-bold uppercase tracking-widest leading-loose">No active investigation findings</p>
                 </div>
               )}
            </div>
          </div>
        )}
      </aside>
    </div>
  );
}
