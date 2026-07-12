"use client";

import { useState, useMemo } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";
import { Loader2, AlertCircle, FileSearch } from "lucide-react";
import { cn } from "@/core/utils/cn";

// Configure worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface PdfRendererProps {
  url: string;
  pageNumber: number;
  zoom: number;
  onLoadSuccess: (numPages: number) => void;
  className?: string;
}

export function PdfRenderer({ url, pageNumber, zoom, onLoadSuccess, className }: PdfRendererProps) {
  const [error, setError] = useState<string | null>(null);

  const loading = (
    <div className="flex flex-col items-center justify-center h-full gap-4 text-muted-foreground animate-in fade-in duration-700">
       <Loader2 className="h-10 w-10 animate-spin text-primary" />
       <p className="text-sm font-bold uppercase tracking-widest">Rendering Legal Document...</p>
    </div>
  );

  const errorState = (
    <div className="flex flex-col items-center justify-center h-full gap-4 p-8 text-center animate-in zoom-in-95 duration-500">
       <div className="p-4 bg-destructive/10 rounded-full text-destructive">
          <AlertCircle className="h-12 w-12" />
       </div>
       <h3 className="text-xl font-bold">Document Access Denied</h3>
       <p className="text-sm text-muted-foreground max-w-sm">
         The backend storage provider is currently restricted or the document is missing.
         This functionality requires a production-level object storage API.
       </p>
    </div>
  );

  return (
    <div className={cn("relative flex-1 bg-muted/20 overflow-auto custom-scrollbar p-8 flex justify-center", className)}>
      <div className="shadow-2xl border-4 border-white/10 rounded-sm overflow-hidden h-fit transition-transform duration-300 origin-top">
        <Document
          file={url}
          onLoadSuccess={({ numPages }) => {
            setError(null);
            onLoadSuccess(numPages);
          }}
          onLoadError={(err) => {
            console.error("PDF Load Error:", err);
            setError(err.message);
          }}
          loading={loading}
          error={errorState}
        >
          <Page
            pageNumber={pageNumber}
            scale={zoom}
            className="shadow-xl"
            renderAnnotationLayer={true}
            renderTextLayer={true}
            loading={loading}
          />
        </Document>
      </div>
    </div>
  );
}
