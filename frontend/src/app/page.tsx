"use client"

import { useState, useEffect } from "react"
import { AppLayout } from "@/shared/layouts/app-layout"
import { PageHeader } from "@/shared/components/dashboard/page-header"
import { StatCard } from "@/shared/components/dashboard/stat-card"
import { QuickActions } from "@/features/dashboard/components/quick-actions"
import {
  Files,
  MessageSquare,
  ShieldCheck,
  AlertCircle,
  TrendingUp,
  Activity,
  History,
  Zap
} from "lucide-react"
import { PageSkeleton } from "@/shared/components/loading/page-skeleton"
import { motion } from "framer-motion"

export default function DashboardPage() {
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 800)
    return () => clearTimeout(timer)
  }, [])

  if (loading) {
    return (
      <AppLayout>
        <PageSkeleton />
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <PageHeader
        title="Command Dashboard"
        description="Welcome back, Administrator. Real-time intelligence and operational metrics for your legal workspace."
      />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-10">
        <StatCard
          title="Total Documents"
          value={124}
          icon={Files}
          trend={{ value: 12, isUp: true }}
          description="Managed legal files"
        />
        <StatCard
          title="AI Consultations"
          value={48}
          icon={MessageSquare}
          trend={{ value: 8, isUp: true }}
          description="RAG queries today"
        />
        <StatCard
          title="Evidence Identified"
          value={856}
          icon={ShieldCheck}
          trend={{ value: 24, isUp: true }}
          description="Verified citations"
        />
        <StatCard
          title="Conflicts Detected"
          value={3}
          icon={AlertCircle}
          trend={{ value: 2, isUp: false }}
          description="Requires attention"
        />
      </div>

      <div className="space-y-4 mb-10">
        <div className="flex items-center gap-2 px-1">
          <Zap className="h-4 w-4 text-primary" />
          <h2 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">Quick Actions</h2>
        </div>
        <QuickActions />
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 rounded-2xl border bg-card shadow-sm overflow-hidden">
          <div className="p-4 border-b bg-muted/20 flex items-center justify-between">
             <div className="flex items-center gap-2">
                <History className="h-4 w-4 text-muted-foreground" />
                <h3 className="text-xs font-bold uppercase tracking-widest">Recent Platform Activity</h3>
             </div>
             <button className="text-[10px] font-bold text-primary hover:underline">VIEW ALL LOGS</button>
          </div>
          <div className="p-6 space-y-6">
            {[
              { user: "Admin", action: "Uploaded SLA_v2.pdf", time: "12 mins ago", type: "document" },
              { user: "AI Engine", action: "Completed conflict analysis for Project X", time: "45 mins ago", type: "analysis" },
              { user: "Legal Counsel", action: "Verified 12 citations in Case 402", time: "2 hours ago", type: "verification" },
            ].map((activity, i) => (
              <div key={i} className="flex items-start gap-4 group">
                <div className="h-10 w-10 rounded-xl bg-muted flex items-center justify-center group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                  <Activity className="h-5 w-5" />
                </div>
                <div className="flex-1 space-y-0.5">
                  <p className="text-sm font-bold text-foreground">
                    <span className="text-primary">{activity.user}</span> {activity.action}
                  </p>
                  <p className="text-xs text-muted-foreground">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border bg-card shadow-sm overflow-hidden">
           <div className="p-4 border-b bg-muted/20 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-xs font-bold uppercase tracking-widest">AI Performance Index</h3>
           </div>
           <div className="p-8 text-center space-y-4">
              <div className="inline-flex items-center justify-center h-24 w-24 rounded-full border-4 border-primary/20 border-t-primary relative">
                 <span className="text-2xl font-black">94<span className="text-xs">%</span></span>
              </div>
              <div className="space-y-1">
                 <h4 className="text-sm font-bold">Confidence Average</h4>
                 <p className="text-xs text-muted-foreground">Based on last 500 semantic retrieval cycles.</p>
              </div>
              <div className="pt-4 grid grid-cols-2 gap-4">
                 <div className="p-3 rounded-xl bg-muted/30 border">
                    <div className="text-[10px] font-bold text-muted-foreground uppercase">Precision</div>
                    <div className="text-sm font-bold">0.92</div>
                 </div>
                 <div className="p-3 rounded-xl bg-muted/30 border">
                    <div className="text-[10px] font-bold text-muted-foreground uppercase">Recall</div>
                    <div className="text-sm font-bold">0.89</div>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </AppLayout>
  )
}
