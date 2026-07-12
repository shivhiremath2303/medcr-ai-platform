import { AppLayout } from "@/shared/layouts/app-layout";
import { PageHeader } from "@/shared/components/dashboard/page-header";
import { StatCard } from "@/shared/components/dashboard/stat-card";
import { QuickActions } from "@/features/dashboard/components/quick-actions";
import {
  Files,
  MessageSquare,
  ShieldCheck,
  AlertCircle
} from "lucide-react";
import { Skeleton } from "@/shared/components/ui/skeleton";

export default function DashboardPage() {
  return (
    <AppLayout>
      <PageHeader
        title="Dashboard"
        description="Welcome back, Administrator. Here's what's happening in your legal workspace."
      />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
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

      <h2 className="text-xl font-bold tracking-tight mb-4">Quick Actions</h2>
      <QuickActions />

      <div className="mt-8 grid gap-6 md:grid-cols-2">
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center gap-4">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="space-y-2 flex-1">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/4" />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">AI Insight Summary</h3>
          <div className="space-y-4">
             <Skeleton className="h-32 w-full" />
             <Skeleton className="h-4 w-1/2" />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
