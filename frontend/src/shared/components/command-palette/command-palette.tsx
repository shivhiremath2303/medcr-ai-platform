"use client"

import * as React from "react"
import * as Dialog from "@radix-ui/react-dialog"
import { Search, Command, FileText, MessageSquare, Scale, Settings, Shield, Layout, ArrowRight } from "lucide-react"
import { useRouter } from "next/navigation"
import { cn } from "@/core/utils/cn"
import { motion, AnimatePresence } from "framer-motion"

export function CommandPalette() {
  const [open, setOpen] = React.useState(false)
  const [search, setSearch] = React.useState("")
  const router = useRouter()

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }
    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  const actions = [
    { title: "Dashboard", href: "/dashboard", icon: Layout, category: "Navigation" },
    { title: "Upload Document", href: "/documents", icon: FileText, category: "Actions" },
    { title: "Start Legal Chat", href: "/chat", icon: MessageSquare, category: "Navigation" },
    { title: "Analysis Workspace", href: "/analysis", icon: Scale, category: "Navigation" },
    { title: "Admin Console", href: "/admin", icon: Shield, category: "System" },
    { title: "User Settings", href: "/settings", icon: Settings, category: "System" },
  ]

  const filteredActions = actions.filter((action) =>
    action.title.toLowerCase().includes(search.toLowerCase())
  )

  const handleNavigate = (href: string) => {
    router.push(href)
    setOpen(false)
    setSearch("")
  }

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-[150] bg-background/80 backdrop-blur-sm" />
        <Dialog.Content className="fixed left-1/2 top-[20%] z-[160] w-full max-w-2xl -translate-x-1/2 overflow-hidden rounded-2xl border bg-card shadow-2xl transition-all outline-none">
          <div className="flex items-center border-b px-4 py-3">
            <Search className="mr-3 h-5 w-5 text-muted-foreground" />
            <input
              autoFocus
              className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
              placeholder="Search pages, actions, or documents... (Ctrl+K)"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <div className="flex items-center gap-1 rounded bg-muted px-2 py-1 text-[10px] font-bold text-muted-foreground">
              <Command className="h-3 w-3" />
              K
            </div>
          </div>

          <div className="max-h-[300px] overflow-y-auto p-2 custom-scrollbar">
            {filteredActions.length > 0 ? (
              <div className="space-y-2">
                {Array.from(new Set(filteredActions.map((a) => a.category))).map((category) => (
                  <div key={category} className="space-y-1">
                    <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                      {category}
                    </div>
                    {filteredActions
                      .filter((a) => a.category === category)
                      .map((action) => (
                        <button
                          key={action.title}
                          onClick={() => handleNavigate(action.href)}
                          className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors hover:bg-muted group"
                        >
                          <div className="flex items-center gap-3">
                            <div className="rounded-md bg-muted p-2 group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                              <action.icon className="h-4 w-4" />
                            </div>
                            <span className="font-medium">{action.title}</span>
                          </div>
                          <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 -translate-x-2 transition-all group-hover:opacity-100 group-hover:translate-x-0" />
                        </button>
                      ))}
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-12 text-center text-sm text-muted-foreground italic">
                No results found for "{search}"
              </div>
            )}
          </div>

          <div className="border-t bg-muted/30 px-4 py-2 text-[10px] text-muted-foreground flex justify-between items-center">
            <div className="flex gap-4">
               <span><kbd className="font-sans border px-1 rounded bg-background">↑↓</kbd> to navigate</span>
               <span><kbd className="font-sans border px-1 rounded bg-background">↵</kbd> to select</span>
            </div>
            <span><kbd className="font-sans border px-1 rounded bg-background">esc</kbd> to close</span>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
