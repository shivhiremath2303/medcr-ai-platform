"use client";

import { RefreshCw, ShieldCheck, Download, ExternalLink } from "lucide-react";
import { motion } from "framer-motion";

interface AdminToolbarProps {
  onRefresh: () => void;
  isRefreshing?: boolean;
}

export function AdminToolbar({ onRefresh, isRefreshing }: AdminToolbarProps) {
  return (
    <div className="flex items-center justify-between p-4 bg-card border rounded-xl shadow-sm mb-8">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-primary/10">
          <ShieldCheck className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h1 className="text-lg font-bold">Admin Console</h1>
          <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest">
            System Operations & Governance
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium border rounded-md hover:bg-muted transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin" : ""}`} />
          Refresh Status
        </button>
        <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors shadow-sm">
          <Download className="h-3.5 w-3.5" />
          Export Logs
        </button>
      </div>
    </div>
  );
}
