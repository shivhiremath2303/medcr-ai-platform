"use client"

import { Navbar } from "@/shared/components/navigation/navbar"
import { Sidebar } from "@/shared/components/navigation/sidebar"
import { ToastProvider } from "@/shared/providers/toast-provider"
import { GlobalErrorBoundary } from "@/shared/components/error/error-boundary"
import { CommandPalette } from "@/shared/components/command-palette/command-palette"
import { OfflineBanner } from "@/shared/components/notifications/offline-banner"
import { NetworkStatus } from "@/shared/components/notifications/network-status"
import { motion, AnimatePresence } from "framer-motion"

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <GlobalErrorBoundary>
      <ToastProvider>
        <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
          <OfflineBanner />
          <NetworkStatus />
          <Navbar />
          <Sidebar />
          <CommandPalette />

          <div className="p-4 sm:ml-64 pt-20">
            <main className="mx-auto max-w-7xl">
              <AnimatePresence mode="wait">
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2, ease: "easeOut" }}
                >
                  {children}
                </motion.div>
              </AnimatePresence>
            </main>
          </div>
        </div>
      </ToastProvider>
    </GlobalErrorBoundary>
  )
}
