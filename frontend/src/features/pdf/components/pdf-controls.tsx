"use client";

import {
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  RotateCw,
  Download,
  Maximize,
  Maximize2
} from "lucide-react";
import { cn } from "@/core/utils/cn";

interface PdfControlsProps {
  currentPage: number;
  totalPages: number;
  zoom: number;
  onPageChange: (page: number) => void;
  onZoomChange: (zoom: number) => void;
  onDownload?: () => void;
}

export function PdfControls({
  currentPage,
  totalPages,
  zoom,
  onPageChange,
  onZoomChange,
  onDownload
}: PdfControlsProps) {
  return (
    <div className="flex items-center justify-between h-12 px-4 border-b bg-card shadow-sm z-20">
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          className="p-1.5 hover:bg-muted rounded-lg disabled:opacity-30 transition-colors"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <div className="flex items-center gap-1.5 px-3 py-1 bg-muted/50 rounded-lg border">
           <input
             type="text"
             value={currentPage}
             readOnly
             className="w-8 bg-transparent text-center text-xs font-bold focus:outline-none"
           />
           <span className="text-[10px] font-black text-muted-foreground uppercase">of {totalPages || "?"}</span>
        </div>
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="p-1.5 hover:bg-muted rounded-lg disabled:opacity-30 transition-colors"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1 bg-muted/50 rounded-lg border p-0.5">
           <button
             onClick={() => onZoomChange(Math.max(0.5, zoom - 0.1))}
             className="p-1.5 hover:bg-background rounded-md transition-all active:scale-95"
           >
             <ZoomOut className="h-4 w-4" />
           </button>
           <span className="w-12 text-center text-[10px] font-black uppercase tracking-tighter">
             {Math.round(zoom * 100)}%
           </span>
           <button
             onClick={() => onZoomChange(Math.min(3, zoom + 0.1))}
             className="p-1.5 hover:bg-background rounded-md transition-all active:scale-95"
           >
             <ZoomIn className="h-4 w-4" />
           </button>
        </div>

        <div className="h-6 w-px bg-border mx-2 hidden md:block" />

        <div className="flex items-center gap-1 hidden md:flex">
           <button className="p-2 hover:bg-muted rounded-lg text-muted-foreground transition-colors">
              <RotateCw className="h-4 w-4" />
           </button>
           <button
             onClick={onDownload}
             className="p-2 hover:bg-muted rounded-lg text-muted-foreground transition-colors"
           >
              <Download className="h-4 w-4" />
           </button>
           <button className="p-2 hover:bg-muted rounded-lg text-muted-foreground transition-colors">
              <Maximize2 className="h-4 w-4" />
           </button>
        </div>
      </div>
    </div>
  );
}
