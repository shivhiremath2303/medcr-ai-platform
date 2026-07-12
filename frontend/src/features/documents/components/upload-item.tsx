"use client";

import { useState, useEffect } from "react";
import { FileText, X, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { formatFileSize } from "../utils/file-utils";
import { Progress } from "@/shared/components/ui/progress";
import { Badge } from "@/shared/components/ui/badge";
import { useUploadDocument } from "../hooks/use-documents";
import { cn } from "@/core/utils/cn";
import { usePdfStore } from "@/features/pdf/hooks/use-pdf-store";

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
    // Start upload immediately on mount
    const upload = async () => {
      try {
        // Simulate progress for UX since backend doesn't support progress events via standard fetch
        const interval = setInterval(() => {
          setFakeProgress((prev) => {
            if (prev >= 95) {
              clearInterval(interval);
              return 95;
            }
            return prev + 5;
          });
        }, 100);

        const result = await mutateAsync(file);

        clearInterval(interval);
        setFakeProgress(100);

        // Store locally if successful to allow viewing
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
    <div className="flex flex-col gap-3 p-4 border rounded-xl bg-card shadow-sm animate-in slide-in-from-right-2 duration-300">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg text-primary">
            <FileText className="h-5 w-5" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold truncate max-w-[200px]">
              {file.name}
            </span>
            <span className="text-xs text-muted-foreground">
              {formatFileSize(file.size)}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {isSuccess && (
            <Badge variant="success" className="gap-1">
              <CheckCircle2 className="h-3 w-3" />
              Indexed
            </Badge>
          )}
          {isError && (
            <Badge variant="destructive" className="gap-1">
              <AlertCircle className="h-3 w-3" />
              Failed
            </Badge>
          )}
          {!isSuccess && !isError && (
            <button
              onClick={onRemove}
              className="p-1 hover:bg-muted rounded-full text-muted-foreground transition-colors"
              disabled={isPending}
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground">
            {isPending ? "Indexing legal clauses..." : isSuccess ? "Done" : isError ? "Error" : "Queued"}
          </span>
          {isPending && <span className="font-medium">{fakeProgress}%</span>}
        </div>
        <Progress value={isPending ? fakeProgress : isSuccess ? 100 : 0} />
      </div>

      {isSuccess && data && (
        <div className="text-[11px] text-green-600 dark:text-green-400 bg-green-500/5 p-2 rounded border border-green-500/10">
          Successfully indexed <strong>{data.chunks}</strong> legal evidence chunks.
        </div>
      )}

      {isError && (
        <div className="text-[11px] text-destructive bg-destructive/5 p-2 rounded border border-destructive/10">
          {error instanceof Error ? error.message : "Internal processing error. Please check file format."}
        </div>
      )}
    </div>
  );
}
