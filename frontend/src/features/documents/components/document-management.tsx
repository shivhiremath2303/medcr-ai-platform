"use client";

import { useState } from "react";
import { PageHeader } from "@/shared/components/dashboard/page-header";
import { UploadDropzone } from "./upload-dropzone";
import { UploadItem } from "./upload-item";
import { DocumentPlaceholderTable } from "./document-placeholder-table";
import { Search, Filter, History, Trash2, Database, Zap } from "lucide-react";
import { useToast } from "@/shared/providers/toast-provider";
import { EmptyState } from "@/shared/components/ui/empty-state";
import { motion, AnimatePresence } from "framer-motion";

export function DocumentManagement() {
  const [uploadQueue, setUploadQueue] = useState<{ id: string; file: File }[]>([]);
  const { toast } = useToast();

  const handleFilesSelected = (files: File[]) => {
    const newItems = files.map(file => ({
      id: Math.random().toString(36).substring(7),
      file
    }));
    setUploadQueue(prev => [...prev, ...newItems]);

    toast({
      title: "Files added to queue",
      description: `Preparing ${files.length} document(s) for indexing.`,
      type: "info"
    });
  };

  const removeFile = (id: string) => {
    setUploadQueue(prev => prev.filter(item => item.id !== id));
  };

  return (
    <div className="space-y-10 pb-20">
      <PageHeader
        title="Document Management"
        description="Ingest, index, and organize legal evidence. Our AI automatically extracts citations and builds semantic relationships."
      />

      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
             <Database className="h-5 w-5 text-primary" />
             <h2 className="text-xl font-bold tracking-tight">Ingestion Control</h2>
          </div>
          <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-muted-foreground bg-muted/50 border px-3 py-1.5 rounded-lg">
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            Ingestion Gateway: Online
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_400px]">
          <UploadDropzone onFilesSelected={handleFilesSelected} />

          <div className="rounded-2xl border bg-card p-6 shadow-sm flex flex-col">
            <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-6 flex items-center gap-2">
              <History className="h-4 w-4" />
              Active Queue ({uploadQueue.length})
            </h3>

            <div className="flex-1">
              <AnimatePresence mode="popLayout">
                {uploadQueue.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex flex-col items-center justify-center h-[280px] text-center"
                  >
                    <div className="p-4 rounded-full bg-muted mb-4 opacity-50">
                       <History className="h-8 w-8 text-muted-foreground" />
                    </div>
                    <p className="text-sm font-bold text-muted-foreground">Queue is empty</p>
                    <p className="text-xs text-muted-foreground mt-1">Pending uploads will appear here.</p>
                  </motion.div>
                ) : (
                  <div className="space-y-3 max-h-[450px] overflow-y-auto pr-2 custom-scrollbar">
                    {uploadQueue.map((item) => (
                      <UploadItem
                        key={item.id}
                        file={item.file}
                        onRemove={() => removeFile(item.id)}
                        onComplete={() => {
                          toast({
                            title: "Index Complete",
                            description: `${item.file.name} is now searchable.`,
                            type: "success"
                          });
                        }}
                      />
                    ))}
                  </div>
                )}
              </AnimatePresence>
            </div>

            {uploadQueue.length > 0 && (
              <button
                onClick={() => setUploadQueue([])}
                className="mt-6 w-full py-2.5 rounded-lg border bg-muted/10 text-[11px] font-bold uppercase tracking-widest text-muted-foreground hover:text-destructive hover:border-destructive/20 hover:bg-destructive/5 transition-all flex items-center justify-center gap-2"
              >
                <Trash2 className="h-3.5 w-3.5" />
                Flush Queue
              </button>
            )}
          </div>
        </div>
      </section>

      <section className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
             <Zap className="h-5 w-5 text-primary" />
             <h2 className="text-xl font-bold tracking-tight">Legal Knowledge Base</h2>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative group">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
              <input
                type="text"
                placeholder="Semantic search through index..."
                className="pl-10 bg-muted/50 border rounded-xl h-10 text-sm w-full md:w-[300px] outline-none focus:ring-2 focus:ring-primary/20 transition-all"
              />
            </div>
            <button className="inline-flex items-center justify-center rounded-xl text-xs font-bold border bg-card h-10 px-4 hover:bg-muted transition-colors uppercase tracking-widest">
              <Filter className="h-3.5 w-3.5 mr-2" />
              Filter
            </button>
          </div>
        </div>

        <DocumentPlaceholderTable />
      </section>
    </div>
  );
}
