"use client";

import {
  FileText,
  Search,
  MoreHorizontal,
  Eye,
  Trash2,
  Download,
  AlertCircle
} from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Skeleton } from "@/shared/components/ui/skeleton";

export function DocumentPlaceholderTable() {
  return (
    <div className="rounded-xl border bg-card overflow-hidden shadow-sm relative">
      {/* Overlay explaining backend status */}
      <div className="absolute inset-0 z-10 bg-background/40 backdrop-blur-[1px] flex items-center justify-center p-6 text-center">
        <div className="max-w-md bg-card border p-8 rounded-2xl shadow-xl animate-in zoom-in-95 duration-300">
          <div className="h-12 w-12 bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="h-6 w-6" />
          </div>
          <h3 className="text-xl font-bold mb-2">Metadata API Unavailable</h3>
          <p className="text-muted-foreground text-sm mb-6">
            The production backend currently supports **Document Ingestion** only.
            Document listing, history, and metadata management are scheduled for a future API expansion.
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            <Badge variant="outline" className="bg-muted/50">List API: Pending</Badge>
            <Badge variant="outline" className="bg-muted/50">Delete API: Pending</Badge>
            <Badge variant="outline" className="bg-muted/50">Search API: Pending</Badge>
          </div>
        </div>
      </div>

      <div className="w-full text-left border-collapse opacity-30 grayscale pointer-events-none select-none">
        <div className="bg-muted/50 border-b">
          <div className="grid grid-cols-[1fr_150px_150px_80px] p-4">
            <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Document Name</div>
            <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Indexed Status</div>
            <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Created</div>
            <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Actions</div>
          </div>
        </div>

        <div className="divide-y">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="grid grid-cols-[1fr_150px_150px_80px] p-4 items-center">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 bg-muted rounded flex items-center justify-center">
                   <FileText className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="space-y-1">
                  <div className="h-4 w-48 bg-muted rounded" />
                  <div className="h-3 w-20 bg-muted rounded" />
                </div>
              </div>
              <div>
                <Badge variant="outline">Processing</Badge>
              </div>
              <div className="text-sm text-muted-foreground">
                 Dec 07, 2026
              </div>
              <div>
                <MoreHorizontal className="h-5 w-5 text-muted-foreground" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
