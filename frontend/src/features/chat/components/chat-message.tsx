"use client";

import { Message, Evidence } from "../types";
import { cn } from "@/core/utils/cn";
import { ShieldAlert, User, Copy, Check, Info, AlertTriangle } from "lucide-react";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { EvidenceCard } from "./evidence-card";
import { Badge } from "@/shared/components/ui/badge";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);
  const [showEvidence, setShowEvidence] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const metadata = message.metadata;

  return (
    <div className={cn(
      "flex w-full gap-4 p-6 transition-colors",
      isUser ? "bg-background" : "bg-muted/30 border-y border-muted/50"
    )}>
      <div className="max-w-4xl mx-auto flex w-full gap-4 lg:gap-6">
        <div className={cn(
          "flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-lg shadow-sm",
          isUser ? "bg-primary text-primary-foreground" : "bg-primary/10 text-primary border border-primary/20"
        )}>
          {isUser ? <User className="h-5 w-5" /> : <ShieldAlert className="h-5 w-5" />}
        </div>

        <div className="flex flex-col gap-2 w-full min-w-0">
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold tracking-tight">
              {isUser ? "Legal Investigator" : "Legal AI Analyst"}
            </span>
            <div className="flex items-center gap-2">
              {!isUser && (
                 <button
                   onClick={copyToClipboard}
                   className="p-1.5 hover:bg-muted rounded text-muted-foreground transition-colors"
                 >
                   {copied ? <Check className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5" />}
                 </button>
              )}
              <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-tighter">
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>

          <div className="prose prose-sm dark:prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-muted/50 prose-pre:border prose-pre:border-muted-foreground/10 prose-code:text-primary">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>

          {/* AI Metadata & Evidence */}
          {!isUser && metadata && (
            <div className="mt-6 flex flex-col gap-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
               <div className="flex flex-wrap gap-2">
                  <Badge variant={metadata.grounding_score > 0.8 ? "success" : "warning"} className="gap-1.5">
                    {metadata.grounding_score > 0.8 ? <Check className="h-3 w-3" /> : <AlertTriangle className="h-3 w-3" />}
                    Grounding: {Math.round(metadata.grounding_score * 100)}%
                  </Badge>
                  <Badge variant="outline" className="gap-1.5 cursor-pointer hover:bg-muted" onClick={() => setShowEvidence(!showEvidence)}>
                    <Info className="h-3 w-3" />
                    {metadata.evidence.length} Sources
                  </Badge>
                  {metadata.answer_status !== "supported" && (
                    <Badge variant="destructive" className="capitalize">
                      {metadata.answer_status.replace("_", " ")}
                    </Badge>
                  )}
               </div>

               {showEvidence && (
                 <div className="grid gap-3 md:grid-cols-2 mt-2">
                    {metadata.evidence.map((ev, idx) => (
                      <EvidenceCard key={ev.chunk_id || idx} evidence={ev} />
                    ))}
                 </div>
               )}

               {metadata.summary && (
                 <div className="p-4 rounded-xl border bg-primary/5 text-xs italic leading-relaxed text-muted-foreground border-primary/10">
                    <strong>Fact Summary:</strong> {metadata.summary}
                 </div>
               )}
            </div>
          )}

          {message.status === "error" && (
            <div className="mt-2 flex items-center gap-2 text-xs text-destructive font-medium bg-destructive/10 p-2 rounded-lg border border-destructive/20">
               <AlertTriangle className="h-3.5 w-3.5" />
               Failed to retrieve legal analysis. Please check your connectivity or try a different query.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
