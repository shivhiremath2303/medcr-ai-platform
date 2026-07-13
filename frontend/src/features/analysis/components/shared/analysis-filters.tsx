"use client";

import { SectionHeader } from "./section-header";
import { Filter, Check } from "lucide-react";
import { useState } from "react";
import { cn } from "@/core/utils/cn";

export function AnalysisFilters() {
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [confidence, setConfidence] = useState(80);

  const categories = ["All", "Contractual", "Regulatory", "Litigation", "Compliance", "Employment"];

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
            Category Filter
        </label>
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={cn(
                "px-3 py-1.5 text-[11px] font-medium rounded-full border transition-all duration-200",
                selectedCategory === cat
                    ? "bg-primary text-primary-foreground border-primary shadow-sm"
                    : "bg-background text-muted-foreground hover:border-primary/50 hover:text-foreground"
              )}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex justify-between items-center">
            <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                Minimum Confidence
            </label>
            <span className="text-xs font-bold text-primary">{confidence}%</span>
        </div>
        <div className="relative pt-1">
            <input
                type="range"
                min="0"
                max="100"
                value={confidence}
                onChange={(e) => setConfidence(parseInt(e.target.value))}
                className="w-full h-1.5 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
                aria-label="Confidence threshold"
            />
            <div className="flex justify-between text-[9px] text-muted-foreground/60 mt-1 font-bold">
                <span>RELAXED</span>
                <span>STRICT</span>
            </div>
        </div>
      </div>

      <div className="space-y-3">
         <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
            Analysis Status
        </label>
        <div className="space-y-2">
            {[
                { label: "Verified by Legal", checked: true },
                { label: "AI Generated", checked: true },
                { label: "Conflict Flagged", checked: false },
            ].map((item) => (
                <label key={item.label} className="flex items-center gap-3 cursor-pointer group">
                    <div className={cn(
                        "h-4 w-4 rounded border flex items-center justify-center transition-colors",
                        item.checked ? "bg-primary border-primary" : "border-muted-foreground/30 group-hover:border-primary"
                    )}>
                        {item.checked && <Check className="h-3 w-3 text-primary-foreground" />}
                    </div>
                    <span className="text-xs text-muted-foreground group-hover:text-foreground transition-colors">{item.label}</span>
                </label>
            ))}
        </div>
      </div>
    </div>
  );
}
