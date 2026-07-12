"use client";

import { useState, useRef, useEffect } from "react";
import { Message, ChatResponse } from "../types";
import { useSendMessage } from "../hooks/use-chat";
import { ChatMessage } from "./chat-message";
import { ShieldAlert, Send, Search, BookOpen, Trash2, History, Loader2, Info } from "lucide-react";
import { cn } from "@/core/utils/cn";
import { EmptyState } from "@/shared/components/dashboard/empty-state";
import { useEvidenceStore } from "@/features/evidence/hooks/use-evidence-store";

export function LegalChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const { mutateAsync: sendMessage, isPending } = useSendMessage();
  const setRecentAnalysis = useEvidenceStore(state => state.setRecentAnalysis);

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isPending]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isPending) return;

    const userMessage: Message = {
      id: Math.random().toString(36).substring(7),
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
      status: "sent",
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const response = await sendMessage({ question: input });
      setRecentAnalysis(response);

      const assistantMessage: Message = {
        id: Math.random().toString(36).substring(7),
        role: "assistant",
        content: response.answer,
        timestamp: new Date().toISOString(),
        metadata: response,
        status: "sent",
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: Math.random().toString(36).substring(7),
        role: "assistant",
        content: "I apologize, but I encountered an error while processing your legal query.",
        timestamp: new Date().toISOString(),
        status: "error",
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  return (
    <div className="flex h-[calc(100vh-10rem)] w-full overflow-hidden rounded-2xl border bg-card shadow-lg animate-in fade-in zoom-in-95 duration-500">
      {/* Sidebar Placeholder */}
      <aside className="hidden lg:flex w-72 flex-col border-r bg-muted/20">
        <div className="p-4 border-b flex items-center justify-between">
           <h3 className="text-sm font-bold flex items-center gap-2">
             <History className="h-4 w-4" />
             Investigation History
           </h3>
        </div>

        <div className="flex-1 p-6 flex flex-col items-center justify-center text-center opacity-50 select-none grayscale">
           <div className="h-10 w-10 bg-muted rounded-full flex items-center justify-center mb-4">
              <History className="h-5 w-5 text-muted-foreground" />
           </div>
           <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">History Unavailable</p>
           <p className="text-[10px] leading-relaxed text-muted-foreground max-w-[180px]">
             Historical conversation persistence is currently limited to the active session.
           </p>
        </div>

        <div className="p-4 border-t bg-muted/30">
           <div className="rounded-lg bg-primary/5 p-3 border border-primary/10">
              <div className="flex items-center gap-2 text-xs font-bold text-primary mb-1">
                 <ShieldAlert className="h-3 w-3" />
                 Secure Enclave
              </div>
              <p className="text-[10px] text-muted-foreground leading-relaxed">
                All analysis is conducted in isolation. Evidence is strictly scoped to your uploads.
              </p>
           </div>
        </div>
      </aside>

      {/* Chat Area */}
      <main className="flex flex-1 flex-col relative bg-background">
        <header className="flex h-14 items-center justify-between border-b px-6 bg-card/50 backdrop-blur-sm">
           <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs font-bold uppercase tracking-widest">Active Analysis Session</span>
           </div>
           <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                 <Search className="h-3.5 w-3.5" />
                 Hybrid Retrieval Active
              </div>
              <button
                onClick={() => setMessages([])}
                className="p-1.5 hover:bg-muted rounded text-muted-foreground transition-colors"
                title="Clear Session"
              >
                <Trash2 className="h-4 w-4" />
              </button>
           </div>
        </header>

        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto custom-scrollbar"
        >
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
               <EmptyState
                 title="AI Investigation Assistant"
                 description="Ask complex legal questions about your uploaded evidence. Our RAG pipeline will retrieve relevant clauses and provide grounded reasoning."
                 icon={ShieldAlert}
                 className="border-none bg-transparent"
               />
            </div>
          ) : (
            <div className="flex flex-col w-full">
              {messages.map((m) => (
                <ChatMessage key={m.id} message={m} />
              ))}
              {isPending && (
                <div className="flex w-full gap-4 p-6 bg-muted/30 border-y border-muted/50 animate-pulse">
                   <div className="max-w-4xl mx-auto flex w-full gap-4 lg:gap-6">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary border border-primary/20">
                         <ShieldAlert className="h-5 w-5" />
                      </div>
                      <div className="flex flex-col gap-3 w-full">
                         <div className="flex items-center gap-2">
                           <span className="text-sm font-bold">Legal AI Analyst</span>
                           <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />
                         </div>
                         <div className="space-y-2">
                           <div className="h-4 bg-muted-foreground/10 rounded w-full" />
                           <div className="h-4 bg-muted-foreground/10 rounded w-3/4" />
                         </div>
                      </div>
                   </div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="p-6 border-t bg-card/50">
          <form
            onSubmit={handleSubmit}
            className="max-w-4xl mx-auto relative group"
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Query evidence (e.g., 'Summarize the conflict resolution terms in Exhibit A')..."
              className="w-full min-h-[100px] resize-none rounded-2xl border border-input bg-background p-4 pr-14 text-sm shadow-sm ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring group-hover:border-primary/50"
              disabled={isPending}
            />
            <button
              type="submit"
              disabled={!input.trim() || isPending}
              className="absolute right-4 bottom-4 inline-flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-lg transition-all hover:scale-105 hover:bg-primary/90 disabled:opacity-50 disabled:hover:scale-100"
            >
              {isPending ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
            </button>
            <div className="flex items-center gap-4 mt-2 px-2">
               <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground font-medium uppercase tracking-widest">
                  <Info className="h-3 w-3" />
                  Press Enter to send, Shift + Enter for new line
               </div>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
