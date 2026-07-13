import React from "react"
import { LucideIcon } from "lucide-react"
import { cn } from "@/core/utils/cn"

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
}

export function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn(
      "flex flex-col items-center justify-center py-12 px-4 text-center border-2 border-dashed rounded-2xl bg-muted/5 animate-in fade-in zoom-in duration-300",
      className
    )}>
      <div className="mb-6 rounded-full bg-muted p-6 text-muted-foreground/50">
        <Icon className="h-12 w-12" />
      </div>
      <h3 className="text-xl font-bold text-foreground">{title}</h3>
      <p className="mt-2 mb-8 max-w-sm text-sm text-muted-foreground leading-relaxed">
        {description}
      </p>
      {action && (
        <button
          onClick={action.onClick}
          className="rounded-lg bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm transition-all hover:bg-primary/90"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}
