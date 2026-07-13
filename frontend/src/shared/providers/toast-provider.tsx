"use client"

import React, { createContext, useContext, useState, useCallback, ReactNode } from "react"
import { Toast, ToastType } from "../components/ui/toast"
import { AnimatePresence } from "framer-motion"

interface ToastContextType {
  toast: (options: { title?: string; description?: string; type?: ToastType; duration?: number }) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider")
  }
  return context
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Array<{ id: string; title?: string; description?: string; type?: ToastType }>>([])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const toast = useCallback(({ title, description, type = "info", duration = 5000 }: any) => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts((prev) => [...prev, { id, title, description, type }])

    setTimeout(() => {
      removeToast(id)
    }, duration)
  }, [removeToast])

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]">
        <div className="flex flex-col gap-2">
          <AnimatePresence mode="popLayout">
            {toasts.map((t) => (
              <Toast key={t.id} {...t} onClose={removeToast} />
            ))}
          </AnimatePresence>
        </div>
      </div>
    </ToastContext.Provider>
  )
}
