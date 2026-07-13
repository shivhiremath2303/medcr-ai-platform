"use client"

import { useEffect, useState } from "react"
import { WifiOff, Wifi, AlertTriangle } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

export function OfflineBanner() {
  const [isOffline, setIsOffline] = useState(false)
  const [showReconnected, setShowReconnected] = useState(false)

  useEffect(() => {
    const handleOnline = () => {
      setIsOffline(false)
      setShowReconnected(true)
      setTimeout(() => setShowReconnected(false), 5000)
    }
    const handleOffline = () => setIsOffline(true)

    window.addEventListener("online", handleOnline)
    window.addEventListener("offline", handleOffline)

    return () => {
      window.removeEventListener("online", handleOnline)
      window.removeEventListener("offline", handleOffline)
    }
  }, [])

  return (
    <AnimatePresence>
      {isOffline && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="bg-destructive text-destructive-foreground"
        >
          <div className="mx-auto max-w-7xl px-4 py-2 flex items-center justify-center gap-3 text-xs font-bold uppercase tracking-widest">
            <WifiOff className="h-4 w-4" />
            No Internet Connection. Some features may be unavailable.
          </div>
        </motion.div>
      )}

      {showReconnected && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="bg-green-600 text-white"
        >
          <div className="mx-auto max-w-7xl px-4 py-2 flex items-center justify-center gap-3 text-xs font-bold uppercase tracking-widest">
            <Wifi className="h-4 w-4" />
            Connection Restored. You are back online.
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
