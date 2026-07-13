"use client"

import { useState } from "react"
import { useTheme } from "next-themes"
import {
  User,
  Bell,
  Shield,
  Moon,
  Sun,
  Monitor,
  Globe,
  Accessibility,
  Cpu,
  Check,
  Smartphone
} from "lucide-react"
import { cn } from "@/core/utils/cn"
import { motion } from "framer-motion"

export function SettingsWorkspace() {
  const { theme, setTheme } = useTheme()
  const [notifications, setNotifications] = useState(true)
  const [highContrast, setHighContrast] = useState(false)

  const sections = [
    { id: "profile", label: "Account Profile", icon: User },
    { id: "appearance", label: "Appearance", icon: Monitor },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "accessibility", label: "Accessibility", icon: Accessibility },
    { id: "security", label: "Security & Privacy", icon: Shield },
    { id: "ai", label: "AI Preferences", icon: Cpu },
  ]

  const [activeSection, setActiveSection] = useState("appearance")

  return (
    <div className="flex flex-col lg:flex-row gap-8 min-h-[600px]">
      {/* Sidebar */}
      <aside className="w-full lg:w-64 space-y-1">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={cn(
              "flex w-full items-center gap-3 px-4 py-2 text-sm font-medium rounded-lg transition-colors",
              activeSection === section.id
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
          >
            <section.icon className="h-4 w-4" />
            {section.label}
          </button>
        ))}
      </aside>

      {/* Content */}
      <main className="flex-1 bg-card border rounded-xl p-8 shadow-sm">
        <motion.div
          key={activeSection}
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
        >
          {activeSection === "appearance" && (
            <div className="space-y-8">
              <div>
                <h3 className="text-lg font-bold mb-1">Appearance Settings</h3>
                <p className="text-sm text-muted-foreground">Customize how the platform looks on your device.</p>
              </div>

              <div className="space-y-4">
                <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Theme Mode</label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {[
                    { id: "light", label: "Light", icon: Sun },
                    { id: "dark", label: "Dark", icon: Moon },
                    { id: "system", label: "System", icon: Monitor },
                  ].map((mode) => (
                    <button
                      key={mode.id}
                      onClick={() => setTheme(mode.id)}
                      className={cn(
                        "flex flex-col items-center gap-3 p-4 rounded-xl border transition-all",
                        theme === mode.id
                          ? "border-primary bg-primary/5 ring-1 ring-primary"
                          : "border-border hover:border-primary/50"
                      )}
                    >
                      <mode.icon className={cn("h-6 w-6", theme === mode.id ? "text-primary" : "text-muted-foreground")} />
                      <span className={cn("text-xs font-bold", theme === mode.id ? "text-primary" : "text-foreground")}>
                        {mode.label}
                      </span>
                      {theme === mode.id && <Check className="h-4 w-4 text-primary" />}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-4 pt-6 border-t">
                <div className="flex items-center justify-between">
                   <div>
                      <h4 className="text-sm font-bold">Accent Color</h4>
                      <p className="text-xs text-muted-foreground">Adjust the primary color used throughout the interface.</p>
                   </div>
                   <div className="flex gap-2">
                      <div className="h-6 w-6 rounded-full bg-blue-600 cursor-pointer ring-2 ring-offset-2 ring-blue-600" />
                      <div className="h-6 w-6 rounded-full bg-purple-600 cursor-pointer hover:ring-2 hover:ring-offset-2 hover:ring-purple-600" />
                      <div className="h-6 w-6 rounded-full bg-emerald-600 cursor-pointer hover:ring-2 hover:ring-offset-2 hover:ring-emerald-600" />
                   </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === "notifications" && (
            <div className="space-y-8">
              <div>
                <h3 className="text-lg font-bold mb-1">Notification Preferences</h3>
                <p className="text-sm text-muted-foreground">Manage how you receive updates about document analysis and system alerts.</p>
              </div>

              <div className="space-y-6">
                 {[
                   { id: "browser", label: "Browser Notifications", desc: "Show desktop alerts when analysis is complete." },
                   { id: "email", label: "Email Summaries", desc: "Receive weekly activity and security reports." },
                   { id: "critical", label: "Security Alerts", desc: "Mandatory notifications for account security events." },
                 ].map((item) => (
                   <div key={item.id} className="flex items-center justify-between p-4 rounded-lg bg-muted/20 border">
                      <div className="space-y-0.5">
                        <div className="text-sm font-bold">{item.label}</div>
                        <div className="text-xs text-muted-foreground">{item.desc}</div>
                      </div>
                      <div
                        onClick={() => setNotifications(!notifications)}
                        className={cn(
                          "h-6 w-11 rounded-full p-1 cursor-pointer transition-colors",
                          notifications ? "bg-primary" : "bg-muted-foreground/30"
                        )}
                      >
                        <div className={cn(
                          "h-4 w-4 rounded-full bg-white transition-transform",
                          notifications ? "translate-x-5" : "translate-x-0"
                        )} />
                      </div>
                   </div>
                 ))}
              </div>
            </div>
          )}

          {activeSection === "ai" && (
            <div className="space-y-8 text-center py-12">
               <Cpu className="h-12 w-12 text-muted-foreground mx-auto opacity-20" />
               <div className="space-y-2">
                 <h3 className="text-lg font-bold">AI Model Configuration</h3>
                 <p className="text-sm text-muted-foreground max-w-sm mx-auto">
                   Configuring custom LLM parameters and RAG retrieval weights will be available in the next major release.
                 </p>
               </div>
               <button disabled className="mt-4 px-6 py-2 bg-muted text-muted-foreground rounded-lg text-sm font-bold cursor-not-allowed">
                 ENTERPRISE LICENSE REQUIRED
               </button>
            </div>
          )}

          {activeSection === "profile" && (
             <div className="space-y-8">
                <div className="flex items-center gap-6">
                   <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center text-primary text-2xl font-bold border-2 border-primary/20">
                      SA
                   </div>
                   <div className="space-y-1">
                      <h3 className="text-xl font-bold">System Administrator</h3>
                      <p className="text-sm text-muted-foreground">admin@medcr.ai • Role: Global Admin</p>
                      <button className="text-xs font-bold text-primary hover:underline">Change Avatar</button>
                   </div>
                </div>

                <div className="grid gap-6 pt-6 border-t">
                   <div className="space-y-2">
                      <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Full Name</label>
                      <input
                        type="text"
                        defaultValue="System Administrator"
                        className="w-full bg-muted/30 border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/20"
                      />
                   </div>
                   <div className="space-y-2">
                      <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Email Address</label>
                      <input
                        type="email"
                        defaultValue="admin@medcr.ai"
                        className="w-full bg-muted/30 border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/20"
                      />
                   </div>
                </div>
             </div>
          )}
        </motion.div>
      </main>
    </div>
  )
}
