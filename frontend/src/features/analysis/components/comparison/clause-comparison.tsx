"use client";

import { ClauseComparison as ComparisonType, RiskLevel } from "../../types";
import { ClauseCard } from "./clause-card";
import { AlertTriangle, ShieldCheck, Zap, Info, FileText, BookOpen } from "lucide-react";
import { cn } from "@/core/utils/cn";
import { motion } from "framer-motion";

interface ClauseComparisonProps {
  comparison: ComparisonType;
}

export function ClauseComparison({ comparison }: ClauseComparisonProps) {
  // Future-ready placeholders
  const riskLevel: RiskLevel = comparison.riskLevel ?? "medium";
  const legalImpact = comparison.legalImpact ?? "Potentially modifies the liability threshold for service delays. Needs review by Senior Counsel.";
  const confidence = comparison.confidenceScore ?? 0.92;

  const riskStyles: Record<RiskLevel, string> = {
    low: "text-blue-600 bg-blue-50 border-blue-100",
    medium: "text-yellow-600 bg-yellow-50 border-yellow-100",
    high: "text-orange-600 bg-orange-50 border-orange-100",
    critical: "text-red-600 bg-red-50 border-red-100",
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <ClauseCard clause={comparison.original} type="original" />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <ClauseCard clause={comparison.proposed} type="proposed" />
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 lg:grid-cols-3 gap-6"
      >
        {/* Analysis Column */}
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
            <div className="px-4 py-3 border-b bg-muted/30 flex items-center justify-between">
              <h5 className="text-sm font-bold flex items-center gap-2">
                <Zap className="h-4 w-4 text-primary" />
                AI Legal Impact Analysis
              </h5>
              <div className={cn("px-2 py-0.5 rounded text-[10px] font-bold uppercase border", riskStyles[riskLevel])}>
                {riskLevel} Risk
              </div>
            </div>
            <div className="p-4 space-y-4">
              <p className="text-sm text-foreground leading-relaxed">
                {legalImpact}
              </p>

              <div className="grid grid-cols-2 gap-4 pt-2">
                <div className="p-3 rounded-lg bg-muted/30 border space-y-1">
                  <div className="flex items-center gap-2 text-[11px] font-bold text-muted-foreground uppercase">
                    <FileText className="h-3.5 w-3.5" />
                    Evidence
                  </div>
                  <p className="text-xs font-medium">{comparison.proposed.metadata.source || "Amendment Draft"}</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/30 border space-y-1">
                  <div className="flex items-center gap-2 text-[11px] font-bold text-muted-foreground uppercase">
                    <BookOpen className="h-3.5 w-3.5" />
                    Citations
                  </div>
                  <p className="text-xs font-medium">{comparison.proposed.citation || "None identified"}</p>
                </div>
              </div>
            </div>
          </div>

          {comparison.conflicts.length > 0 && (
            <div className="rounded-xl border border-red-200 bg-red-50/50 dark:bg-red-900/10 p-4">
              <div className="flex items-center gap-2 mb-3 text-red-800 dark:text-red-400">
                <AlertTriangle className="h-5 w-5" />
                <h5 className="text-sm font-bold">Identified Contractual Conflicts</h5>
              </div>
              <ul className="space-y-2">
                {comparison.conflicts.map((conflict, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-red-700 dark:text-red-300">
                    <div className="h-1.5 w-1.5 rounded-full bg-red-400 mt-1.5 shrink-0" />
                    {conflict}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Sidebar Info Column */}
        <div className="space-y-6">
          <div className="rounded-xl border bg-card p-4 space-y-4">
            <h5 className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <ShieldCheck className="h-3.5 w-3.5 text-green-500" />
              Analysis Metrics
            </h5>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-muted-foreground">AI Confidence</span>
                  <span className="font-bold">{Math.round(confidence * 100)}%</span>
                </div>
                <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${confidence * 100}%` }}
                    className="h-full bg-green-500"
                  />
                </div>
              </div>

              <div className="pt-2">
                <div className="flex items-start gap-2 p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 border border-blue-100 dark:border-blue-800">
                  <Info className="h-4 w-4 shrink-0 mt-0.5" />
                  <p className="text-[11px] leading-relaxed italic">
                    Comparison is based on semantic similarity and keyword mapping. Risk assessment is advisory.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl border border-dashed text-center">
            <p className="text-[11px] text-muted-foreground italic">
              Automated redlining and track-changes integration available in upcoming Pro Release.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
