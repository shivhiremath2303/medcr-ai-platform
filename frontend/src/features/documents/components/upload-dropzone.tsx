"use client";

import { useState, useCallback } from "react";
import { Upload, FileUp, Info } from "lucide-react";
import { cn } from "@/core/utils/cn";
import { isSupportedFileType } from "../utils/file-utils";

interface UploadDropzoneProps {
  onFilesSelected: (files: File[]) => void;
}

export function UploadDropzone({ onFilesSelected }: UploadDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files).filter(file => isSupportedFileType(file.name));
    if (files.length > 0) {
      onFilesSelected(files);
    }
  }, [onFilesSelected]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files).filter(file => isSupportedFileType(file.name));
      if (files.length > 0) {
        onFilesSelected(files);
      }
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={cn(
        "group relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-12 transition-all duration-300",
        isDragging
          ? "border-primary bg-primary/5 scale-[1.01]"
          : "border-muted-foreground/20 hover:border-primary/50 hover:bg-accent/50"
      )}
    >
      <input
        type="file"
        multiple
        accept=".pdf,.docx"
        onChange={handleFileChange}
        className="absolute inset-0 cursor-pointer opacity-0"
      />

      <div className={cn(
        "flex h-20 w-20 items-center justify-center rounded-full bg-muted transition-transform duration-300",
        isDragging && "scale-110"
      )}>
        <FileUp className={cn(
          "h-10 w-10 text-muted-foreground group-hover:text-primary transition-colors",
          isDragging && "text-primary"
        )} />
      </div>

      <div className="mt-6 text-center">
        <h3 className="text-xl font-bold tracking-tight">Drop legal documents here</h3>
        <p className="mt-2 text-muted-foreground">
          Drag and drop PDF or DOCX files to start AI indexing
        </p>
      </div>

      <div className="mt-8 flex items-center gap-6 text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <Info className="h-3 w-3" />
          <span>Max file size: 20MB</span>
        </div>
        <div className="flex items-center gap-2">
          <Upload className="h-3 w-3" />
          <span>PDF, DOCX only</span>
        </div>
      </div>

      {isDragging && (
        <div className="absolute inset-0 z-10 flex items-center justify-center rounded-2xl bg-primary/10 pointer-events-none border-2 border-primary">
          <div className="bg-background px-6 py-3 rounded-full shadow-lg font-bold text-primary flex items-center gap-2">
             <Upload className="h-5 w-5 animate-bounce" />
             Release to upload
          </div>
        </div>
      )}
    </div>
  );
}
