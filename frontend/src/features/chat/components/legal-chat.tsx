"use client";

import { useState, useRef, useEffect } from "react";
import { Message, ChatResponse } from "../types";
import { useSendMessage } from "../hooks/use-chat";
import { ChatMessage } from "./chat-message";
import { ShieldAlert, Send, Search, BookOpen, Trash2, History, Loader2, Info, Sparkles, Database } from "lucide-react";
import { cn } from "@/core/utils/cn";
import { EmptyState } from "@/shared/components/ui/empty-state";
import { useEvidenceStore } from "@/features/evidence/hooks/use-evidence-store";
import { useToast } from "@/shared/providers/toast-provider";
import { motion, AnimatePresence } from "framer-motion";

export function LegalChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const { mutateAsync: sendMessage, isPending } = useSendMessage();
  const setRecentAnalysis = useEvidenceStore(state => state.setRecentAnalysis);
  const { toast } = useToast();

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
      toast({
        title: "Analysis Failed",
        description: "Encountered an error while processing your legal query.",
        type: "error"
      });

      const errorMessage: Message = {
        id: Math.random().toString(36).substring(7),
        role: "assistant",
        content: "I apologize, but I encountered an technical error while processing your legal query. Please try again or check system status.",
        timestamp: new Date().toISOString(),
        status: "error",
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const clearSession = () => {
    setMessages([]);
    toast({
      title: "Session Cleared",
      description: "Chat history has been reset for this investigation.",
      type: "info"
    });
  };

  return (
    <div className="flex h-[calc(100vh-12rem)] w-full overflow-hidden rounded-2xl border bg-card shadow-lg">
      {/* Sidebar - Investigation Intelligence */}
      <aside className="hidden xl:flex w-80 flex-col border-r bg-muted/20">
        <div className="p-4 border-b bg-card/50">
           <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2">
             <History className="h-4 w-4" />
             Investigation Context
           </h3>
        </div>

        <div className="flex-1 p-6 flex flex-col items-center justify-center text-center opacity-40">
           <div className="h-12 w-12 bg-muted rounded-full flex items-center justify-center mb-4 border-2 border-dashed border-muted-foreground/30">
              <History className="h-6 w-6 text-muted-foreground" />
           </div>
           <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-2">History v2.0</p>
           <p className="text-xs leading-relaxed text-muted-foreground max-w-[200px]">
             Conversation persistence across sessions is coming in the next enterprise update.
           </p>
        </div>

        <div className="p-6 space-y-4 border-t bg-card/50">
           <div className="space-y-3">
              <div className="flex items-center gap-2 text-[10px] font-bold text-primary uppercase tracking-wider">
                 <ShieldAlert className="h-3.5 w-3.5" />
                 SECURITY STATUS
              </div>
              <div className="p-3 rounded-xl border bg-background/50 space-y-2">
                 <div className="flex justify-between items-center text-[10px]">
                    <span className="text-muted-foreground font-bold">Encrypted End-to-End</span>
                    <div className="h-1.5 w-1.5 rounded-full bg-green-500" />
                 </div>
                 <div className="flex justify-between items-center text-[10px]">
                    <span className="text-muted-foreground font-bold">PII Redaction</span>
                    <div className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                 </div>
              </div>
           </div>
        </div>
      </aside>

      {/* Main Chat Interface */}
      <main className="flex flex-1 flex-col relative bg-background/50">
        <header className="flex h-16 items-center justify-between border-b px-6 bg-card/80 backdrop-blur-md z-10">
           <div className="flex items-center gap-3">
              <div className="flex -space-x-2">
                 {[1, 2, 3].map(i => (
                    <div key={i} className="h-6 w-6 rounded-full border-2 border-card bg-primary/10 flex items-center justify-center">
                       <Database className="h-3 w-3 text-primary" />
                    </div>
                 ))}
              </div>
              <div className="flex flex-col">
                 <span className="text-sm font-bold leading-none">Investigation AI</span>
                 <span className="text-[10px] text-muted-foreground mt-1 uppercase font-bold tracking-widest">Active Hybrid-RAG</span>
              </div>
           </div>

           <div className="flex items-center gap-2">
              <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-muted/50 border text-[10px] font-bold text-muted-foreground">
                 <Sparkles className="h-3 w-3 text-primary" />
                 DEEP REASONING ON
              </div>
              <button
                onClick={clearSession}
                className="p-2 hover:bg-muted rounded-xl text-muted-foreground hover:text-destructive transition-all"
                title="Reset Session"
              >
                <Trash2 className="h-4 w-4" />
              </button>
           </div>
        </header>

        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-4 md:p-6 custom-scrollbar space-y-6"
        >
          <AnimatePresence mode="popLayout">
            {messages.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className="h-full flex items-center justify-center"
              >
                 <EmptyState
                   title="Legal Investigation Terminal"
                   description="Perform semantic queries, reconstruct timelines, and identify contractual risks through natural language investigation."
                   icon={ShieldAlert}
                   className="border-none bg-transparent"
                   action={{
                     label: "WHAT CAN I ASK?",
                     onClick: () => {
                       setInput("Analyze the liability limitations across all uploaded service agreements.");
                     }
                   }}
                 />
              </motion.div>
            ) : (
              <div className="flex flex-col gap-6 max-w-5xl mx-auto">
                {messages.map((m) => (
                  <ChatMessage key={m.id} message={m} />
                ))}

                {isPending && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex w-full gap-4 p-6 rounded-2xl bg-primary/5 border border-primary/10 animate-pulse"
                  >
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
                       <Sparkles className="h-5 w-5" />
                    </div>
                    <div className="flex flex-col gap-3 w-full">
                       <div className="flex items-center gap-3">
                         <span className="text-xs font-black uppercase tracking-widest text-primary">Synthesizing Response...</span>
                         <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
                       </div>
                       <div className="space-y-2">
                         <div className="h-3 bg-primary/10 rounded w-full" />
                         <div className="h-3 bg-primary/10 rounded w-3/4" />
                         <div className="h-3 bg-primary/10 rounded w-1/2" />
                       </div>
                    </div>
                  </motion.div>
                )}
              </div>
            )}
          </AnimatePresence>
        </div>

        {/* Input Bar */}
        <div className="p-6 bg-card/50 border-t">
          <form
            onSubmit={handleSubmit}
            className="max-w-5xl mx-auto relative flex items-end gap-3"
          >
            <div className="flex-1 relative group">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                placeholder="Ask about document risks, conflicts, or facts..."
                className="w-full min-h-[80px] max-h-[200px] resize-none rounded-2xl border-2 border-muted bg-background p-4 pr-12 text-sm shadow-sm transition-all focus:border-primary/50 outline-none"
                disabled={isPending}
              />
              <div className="absolute right-3 bottom-3 flex items-center gap-2">
                 <button
                   type="button"
                   className="p-1.5 rounded-lg text-muted-foreground hover:bg-muted transition-colors"
                   title="Attach Document Context"
                 >
                    <BookOpen className="h-4 w-4" />
                 </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={!input.trim() || isPending}
              className={cn(
                "flex h-[80px] w-[80px] flex-col items-center justify-center rounded-2xl transition-all shadow-lg active:scale-95",
                input.trim() && !isPending
                  ? "bg-primary text-primary-foreground shadow-primary/20"
                  : "bg-muted text-muted-foreground opacity-50 cursor-not-allowed"
              )}
            >
              {isPending ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                <>
                  <Send className="h-6 w-6 mb-1" />
                  <span className="text-[10px] font-black uppercase">Run</span>
                </>
              )}
            </button>
          </form>
          <p className="mt-4 text-center text-[10px] font-bold text-muted-foreground uppercase tracking-widest flex items-center justify-center gap-2">
            <ShieldAlert className="h-3 w-3" />
            AI guidance is advisory. Verify with primary source evidence citations.
          </p>
        </div>
      </main>
    </div>
  );
}
