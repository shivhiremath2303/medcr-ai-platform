"use client";

import { Network, Info, Lock } from "lucide-react";
import { motion } from "framer-motion";

export function RelationshipGraphPanel() {
  return (
    <div className="h-full flex flex-col items-center justify-center p-8 bg-card rounded-xl border-2 border-dashed border-muted-foreground/20 text-center max-w-2xl mx-auto min-h-[400px]">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="p-6 rounded-full bg-primary/10 mb-6 relative"
      >
        <Network className="h-12 w-12 text-primary" />
        <div className="absolute -top-1 -right-1 bg-background p-1 rounded-full border shadow-sm">
            <Lock className="h-4 w-4 text-muted-foreground" />
        </div>
      </motion.div>

      <h3 className="text-xl font-bold text-foreground mb-3">Relationship Graph Explorer</h3>
      <p className="text-sm text-muted-foreground mb-8 leading-relaxed">
        Our proprietary graph-based analysis identifies deep relationships between clauses, entities, and obligations across your entire document repository.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full mb-8">
        {[
          "Cross-Document Entity Mapping",
          "Obligation Propagation Analysis",
          "Conflict Path Detection",
          "Dependency Visualization"
        ].map((feature) => (
          <div key={feature} className="flex items-center gap-3 p-3 rounded-lg bg-muted/30 border border-muted/50 text-left">
            <div className="h-2 w-2 rounded-full bg-primary/40 shrink-0" />
            <span className="text-xs font-medium text-muted-foreground">{feature}</span>
          </div>
        ))}
      </div>

      <div className="flex items-start gap-3 p-4 rounded-xl bg-blue-50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-800 text-left">
        <Info className="h-5 w-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-xs font-bold text-blue-800 dark:text-blue-300 uppercase tracking-wider mb-1">Architecture Roadmap</h4>
          <p className="text-[11px] text-blue-700 dark:text-blue-400 leading-relaxed">
            The Relationship Graph will become available when backend graph analysis (Neo4j) endpoints are implemented in Milestone 10. Graph data is currently being indexed in the background.
          </p>
        </div>
      </div>
    </div>
  );
}
