"use client"

import * as React from "react"
import { Cross2Icon } from "@radix-ui/react-icons"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/core/utils/cn"

// Since @radix-ui/react-toast might not be installed,
// and the prompt asks for complete updated files,
// I will implement a simplified but highly professional version
// using framer-motion for the "Enterprise Experience".

import { motion, AnimatePresence } from "framer-motion"
import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from "lucide-react"

export type ToastType = "success" | "error" | "warning" | "info"

export interface ToastProps {
  id: string
  title?: string
  description?: string
  type?: ToastType
  onClose: (id: string) => void
}

const toastVariants = cva(
  "group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-xl border p-4 pr-8 shadow-lg transition-all",
  {
    variants: {
      variant: {
        default: "bg-background border-border text-foreground",
        success: "bg-background border-green-500/20 text-foreground",
        error: "bg-background border-destructive/20 text-foreground",
        warning: "bg-background border-yellow-500/20 text-foreground",
        info: "bg-background border-blue-500/20 text-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export function Toast({ id, title, description, type = "info", onClose }: ToastProps) {
  const icons = {
    success: <CheckCircle2 className="h-5 w-5 text-green-500" />,
    error: <AlertCircle className="h-5 w-5 text-destructive" />,
    warning: <AlertTriangle className="h-5 w-5 text-yellow-500" />,
    info: <Info className="h-5 w-5 text-blue-500" />,
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
      className={cn(toastVariants({ variant: type as any }))}
    >
      <div className="flex gap-3">
        {icons[type]}
        <div className="grid gap-1">
          {title && <div className="text-sm font-bold leading-none">{title}</div>}
          {description && (
            <div className="text-xs text-muted-foreground leading-relaxed">
              {description}
            </div>
          )}
        </div>
      </div>
      <button
        onClick={() => onClose(id)}
        className="absolute right-2 top-2 rounded-md p-1 text-muted-foreground/50 opacity-0 transition-opacity hover:text-foreground group-hover:opacity-100"
      >
        <X className="h-4 w-4" />
      </button>
    </motion.div>
  )
}
