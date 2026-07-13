"use client";

import { useState, useEffect } from "react";
import { FileText, X, CheckCircle2, AlertCircle, Loader2, Database, ShieldCheck } from "lucide-react";
import { formatFileSize } from "../utils/file-utils";
import { Progress } from "@/shared/components/ui/progress";
import { Badge } from "@/shared/components/ui/badge";
import { useUploadDocument } from "../hooks/use-documents";
import { cn } from "@/core/utils/cn";
import { usePdfStore } from "@/features/pdf/hooks/use-pdf-store";
import { motion } from "framer-motion";

interface UploadItemProps {
  file: File;
  onRemove: () => void;
  onComplete: (success: boolean) => void;
}

export function UploadItem({ file, onRemove, onComplete }: UploadItemProps) {
  const { mutateAsync, isPending, isSuccess, isError, error, data } = useUploadDocument();
  const [fakeProgress, setFakeProgress] = useState(0);
  const addLocalBlob = usePdfStore(state => state.addLocalBlob);

  useEffect(() => {
    const upload = async () => {
      try {
        const interval = setInterval(() => {
          setFakeProgress((prev) => {
            if (prev >= 95) {
              clearInterval(interval);
              return 95;
            }
            return prev + (Math.random() * 8);
          });
        }, 150);

        const result = await mutateAsync(file);

        clearInterval(interval);
        setFakeProgress(100);

        if (result && result.filename) {
           addLocalBlob(result.filename, file);
        }

        onComplete(true);
      } catch (e) {
        setFakeProgress(0);
        onComplete(false);
      }
    };

    upload();
  }, [file, mutateAsync, onComplete, addLocalBlob]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={cn(
        "flex flex-col gap-3 p-4 border rounded-xl bg-card shadow-sm transition-all border-l-4",
        isSuccess ? "border-l-green-500 shadow-md" : isError ? "border-l-destructive" : "border-l-primary/50"
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0">
          <div className={cn(
            "p-2.5 rounded-xl transition-colors",
            isSuccess ? "bg-green-500/10 text-green-600" : isError ? "bg-destructive/10 text-destructive" : "bg-primary/10 text-primary"
          )}>
            {isPending ? <Loader2 className="h-5 w-5 animate-spin" /> : <FileText className="h-5 w-5" />}
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-bold truncate">
              {file.name}
            </span>
            <div className="flex items-center gap-2 mt-0.5">
               <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                 {formatFileSize(file.size)}
               </span>
               <span className="h-1 w-1 rounded-full bg-muted-foreground/30" />
               <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                 {file.type.split('/')[1] || 'PDF'}
               </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {isSuccess && (
            <div className="p-1 rounded-full bg-green-500 text-white shadow-sm">
              <CheckCircle2 className="h-3 w-3" />
            </div>
          )}
          {isError && (
            <div className="p-1 rounded-full bg-destructive text-white shadow-sm">
              <AlertCircle className="h-3 w-3" />
            </div>
          )}
          {!isSuccess && !isError && (
            <button
              onClick={onRemove}
              className="p-1.5 hover:bg-muted rounded-full text-muted-foreground transition-colors"
              disabled={isPending}
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-[11px] font-bold uppercase tracking-widest">
          <span className="text-muted-foreground">
            {isPending ? "Extracting Clauses..." : isSuccess ? "Sync Complete" : isError ? "Processing Error" : "Queued"}
          </span>
          {isPending && <span className="text-primary">{Math.round(fakeProgress)}%</span>}
        </div>
        <Progress
            value={isPending ? fakeProgress : isSuccess ? 100 : 0}
            className={cn("h-1.5", isSuccess ? "bg-green-100 dark:bg-green-900/20" : "")}
        />
      </div>

      {isSuccess && data && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="text-[11px] font-medium text-green-700 dark:text-green-400 bg-green-500/5 p-2 rounded-lg border border-green-500/10 flex items-center gap-2"
        >
          <ShieldCheck className="h-3.5 w-3.5" />
          Indexed {data.chunks} evidence fragments.
        </motion.div>
      )}

      {isError && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="text-[11px] font-medium text-destructive bg-destructive/5 p-2 rounded-lg border border-destructive/10"
        >
          {error instanceof Error ? error.message : "Internal processing error."}
        </motion.div>
      )}
    </motion.div>
  );
}
