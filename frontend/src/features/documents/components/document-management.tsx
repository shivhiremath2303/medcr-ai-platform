"use client";

import { useState } from "react";
import { PageHeader } from "@/shared/components/dashboard/page-header";
import { UploadDropzone } from "./upload-dropzone";
import { UploadItem } from "./upload-item";
import { DocumentPlaceholderTable } from "./document-placeholder-table";
import { Search, Filter, History, Trash2 } from "lucide-react";

export function DocumentManagement() {
  const [uploadQueue, setUploadQueue] = useState<{ id: string; file: File }[]>([]);

  const handleFilesSelected = (files: File[]) => {
    const newItems = files.map(file => ({
      id: Math.random().toString(36).substring(7),
      file
    }));
    setUploadQueue(prev => [...prev, ...newItems]);
  };

  const removeFile = (id: string) => {
    setUploadQueue(prev => prev.filter(item => item.id !== id));
  };

  return (
    <div className="space-y-10 pb-20">
      <PageHeader
        title="Documents"
        description="Ingest and manage legal evidence. AI will automatically index contents for RAG analysis."
      />

      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold tracking-tight">Ingest Documents</h2>
          <div className="flex items-center gap-2 text-xs text-muted-foreground bg-muted px-3 py-1 rounded-full">
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            Backend: Uploads Online
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_350px]">
          <UploadDropzone onFilesSelected={handleFilesSelected} />

          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-muted-foreground flex items-center gap-2">
              <History className="h-4 w-4" />
              Upload Queue ({uploadQueue.length})
            </h3>

            {uploadQueue.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-[280px] rounded-xl border border-dashed bg-muted/30 p-8 text-center">
                <p className="text-sm text-muted-foreground">No files in queue.</p>
                <p className="text-xs text-muted-foreground mt-1">Select files to begin indexing.</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[450px] overflow-y-auto pr-2 custom-scrollbar">
                {uploadQueue.map((item) => (
                  <UploadItem
                    key={item.id}
                    file={item.file}
                    onRemove={() => removeFile(item.id)}
                    onComplete={() => {}} // Optional: handle batch completion
                  />
                ))}
              </div>
            )}

            {uploadQueue.length > 0 && (
              <button
                onClick={() => setUploadQueue([])}
                className="w-full py-2 text-xs font-medium text-muted-foreground hover:text-destructive flex items-center justify-center gap-2 transition-colors"
              >
                <Trash2 className="h-3 w-3" />
                Clear Completed
              </button>
            )}
          </div>
        </div>
      </section>

      <section className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <h2 className="text-xl font-bold tracking-tight">Document Library</h2>

          <div className="flex items-center gap-2 opacity-50 pointer-events-none">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search index..."
                disabled
                className="pl-9 bg-muted border rounded-lg h-9 text-sm"
              />
            </div>
            <button disabled className="inline-flex items-center justify-center rounded-md text-sm font-medium border bg-background h-9 px-3">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </button>
          </div>
        </div>

        <DocumentPlaceholderTable />
      </section>
    </div>
  );
}
