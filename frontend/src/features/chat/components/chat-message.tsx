"use client";

import { memo, useState } from "react";
import { Message } from "../types";
import { cn } from "@/core/utils/cn";
import { ShieldAlert, User, Copy, Check, Info, AlertTriangle } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { EvidenceCard } from "./evidence-card";
import { Badge } from "@/shared/components/ui/badge";

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage = memo(function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);
  const [showEvidence, setShowEvidence] = useState(false);

  const copyToClipboard = () => {
    if (!message.content) return;
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const metadata = message.metadata;

  return (
    <div className={cn(
      "flex w-full gap-4 p-6 transition-all duration-300",
      isUser ? "bg-background" : "bg-muted/30 border-y border-muted/50"
    )}>
      <div className="max-w-5xl mx-auto flex w-full gap-4 lg:gap-8">
        <div className={cn(
          "flex h-10 w-10 shrink-0 select-none items-center justify-center rounded-xl shadow-sm transition-transform hover:scale-105",
          isUser
            ? "bg-primary text-primary-foreground shadow-primary/20"
            : "bg-primary/10 text-primary border border-primary/20"
        )}>
          {isUser ? <User className="h-5 w-5" /> : <ShieldAlert className="h-5 w-5" />}
        </div>

        <div className="flex flex-col gap-3 w-full min-w-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-black tracking-tight uppercase">
                {isUser ? "Investigator" : "Legal AI Analyst"}
              </span>
              {!isUser && (
                <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-primary/10 border border-primary/20 text-[9px] font-black text-primary uppercase">
                  Hybrid RAG v1.0
                </div>
              )}
            </div>
            <div className="flex items-center gap-2">
              {!isUser && (
                 <button
                   onClick={copyToClipboard}
                   className="p-1.5 hover:bg-muted rounded-lg text-muted-foreground transition-all hover:text-primary active:scale-95"
                   aria-label="Copy message"
                 >
                   {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                 </button>
              )}
              <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest bg-muted/50 px-2 py-0.5 rounded">
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>

          <div className="prose prose-sm dark:prose-invert max-w-none prose-p:leading-relaxed prose-p:mb-4 prose-headings:font-black prose-headings:tracking-tight prose-strong:text-primary prose-pre:bg-muted/50 prose-pre:border prose-pre:border-muted-foreground/10 prose-code:text-primary prose-a:text-primary hover:prose-a:underline">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>

          {/* AI Metadata & Evidence */}
          {!isUser && metadata && (
            <div className="mt-8 flex flex-col gap-5 animate-in fade-in slide-in-from-bottom-2 duration-500">
               <div className="flex flex-wrap gap-3">
                  <Badge
                    variant={metadata.grounding_score > 0.8 ? "success" : "warning"}
                    className="gap-1.5 font-black uppercase text-[10px] py-1 shadow-sm"
                  >
                    {metadata.grounding_score > 0.8 ? <Check className="h-3 w-3" /> : <AlertTriangle className="h-3 w-3" />}
                    Grounding: {Math.round(metadata.grounding_score * 100)}%
                  </Badge>
                  <button
                    onClick={() => setShowEvidence(!showEvidence)}
                    className={cn(
                      "flex items-center gap-2 px-3 py-1 rounded-full border text-[10px] font-black uppercase tracking-widest transition-all shadow-sm",
                      showEvidence
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-background text-muted-foreground hover:bg-muted hover:border-primary/30"
                    )}
                  >
                    <Info className="h-3 w-3" />
                    {metadata.evidence.length} Evidence Sources
                  </button>
                  {metadata.answer_status !== "supported" && (
                    <Badge variant="destructive" className="capitalize font-black text-[10px] py-1">
                      {metadata.answer_status.replace("_", " ")}
                    </Badge>
                  )}
               </div>

               {showEvidence && (
                 <div className="grid gap-4 md:grid-cols-2 mt-2">
                    {metadata.evidence.map((ev, idx) => (
                      <EvidenceCard key={ev.chunk_id || idx} evidence={ev} />
                    ))}
                 </div>
               )}

               {metadata.summary && (
                 <div className="p-5 rounded-2xl border bg-primary/5 text-[11px] leading-relaxed text-muted-foreground border-primary/10 shadow-inner">
                    <div className="flex items-center gap-2 mb-2">
                       <ShieldAlert className="h-3.5 w-3.5 text-primary" />
                       <span className="font-black uppercase tracking-[0.1em] text-primary">Executive Summary</span>
                    </div>
                    {metadata.summary}
                 </div>
               )}
            </div>
          )}

          {message.status === "error" && (
            <div className="mt-4 flex items-center gap-3 text-xs text-destructive font-bold bg-destructive/10 p-4 rounded-xl border border-destructive/20 shadow-sm">
               <AlertTriangle className="h-5 w-5 shrink-0" />
               Failed to retrieve legal analysis. Please verify your connectivity or try a different investigation query.
            </div>
          )}
        </div>
      </div>
    </div>
  );
});
