"use client"

import { useEffect, useState } from "react"
import { Globe, AlertTriangle } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

export function NetworkStatus() {
  const [slowConnection, setSlowConnection] = useState(false)

  useEffect(() => {
    const checkConnection = () => {
      // @ts-ignore - navigator.connection is not standard but supported in Chrome
      const conn = navigator.connection
      if (conn && (conn.effectiveType === '2g' || conn.effectiveType === '3g')) {
        setSlowConnection(true)
      } else {
        setSlowConnection(false)
      }
    }

    checkConnection()
    // @ts-ignore
    if (navigator.connection) {
       // @ts-ignore
      navigator.connection.addEventListener('change', checkConnection)
    }

    return () => {
       // @ts-ignore
      if (navigator.connection) {
         // @ts-ignore
        navigator.connection.removeEventListener('change', checkConnection)
      }
    }
  }, [])

  return (
    <AnimatePresence>
      {slowConnection && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="fixed bottom-6 left-6 z-[100] bg-yellow-500/10 backdrop-blur-md border border-yellow-500/20 p-3 rounded-xl shadow-lg flex items-center gap-3"
        >
          <div className="p-2 bg-yellow-500 text-white rounded-lg shadow-sm">
             <AlertTriangle className="h-4 w-4" />
          </div>
          <div>
            <h4 className="text-[10px] font-black uppercase tracking-widest text-yellow-600 dark:text-yellow-400">Slow Network</h4>
            <p className="text-[11px] text-muted-foreground">Some analysis may take longer.</p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
