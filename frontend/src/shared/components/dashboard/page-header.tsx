"use client"

import { memo } from "react";
import { cn } from "@/core/utils/cn";

interface PageHeaderProps {
  title: string;
  description?: string;
  children?: React.ReactNode;
  className?: string;
}

export const PageHeader = memo(function PageHeader({ title, description, children, className }: PageHeaderProps) {
  return (
    <header className={cn("flex flex-col gap-4 md:flex-row md:items-center md:justify-between mb-10 pb-2 border-b-2 border-primary/5", className)}>
      <div className="space-y-2">
        <h1 className="text-3xl font-black tracking-tighter text-foreground sm:text-4xl">
          {title}
        </h1>
        {description && (
          <p className="text-muted-foreground text-base sm:text-lg max-w-2xl leading-relaxed">
            {description}
          </p>
        )}
      </div>
      {children && (
        <div className="flex items-center gap-3 shrink-0">
          {children}
        </div>
      )}
    </header>
  );
});
