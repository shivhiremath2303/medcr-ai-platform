"use client";

import dynamic from "next/dynamic";
import { useSystemHealth } from "@/features/admin/hooks/use-system-health";
import { AppLayout } from "@/shared/layouts/app-layout";
import { AdminLoadingState } from "@/features/admin/components/admin-loading-state";
import { AdminEmptyState } from "@/features/admin/components/admin-empty-state";
import {
  Activity,
  Database,
  Globe,
  Zap,
  Cpu,
  Cloud,
  Layout,
  HardDrive,
  RefreshCw,
  LineChart,
  Lock
} from "lucide-react";
import { motion } from "framer-motion";
import { AdminServiceInfo, InfrastructureStatus } from "@/features/admin/types";

// Dynamic Imports for Performance
const AdminSidebar = dynamic(() => import("@/features/admin/components/admin-sidebar").then(mod => mod.AdminSidebar));
const AdminLayout = dynamic(() => import("@/features/admin/components/admin-layout").then(mod => mod.AdminLayout));
const StatusCard = dynamic(() => import("@/features/admin/components/status-card").then(mod => mod.StatusCard));
const HealthCard = dynamic(() => import("@/features/admin/components/health-card").then(mod => mod.HealthCard));
const ServiceCard = dynamic(() => import("@/features/admin/components/service-card").then(mod => mod.ServiceCard));
const InfrastructureCard = dynamic(() => import("@/features/admin/components/infrastructure-card").then(mod => mod.InfrastructureCard));
const AdminSectionHeader = dynamic(() => import("@/features/admin/components/admin-section-header").then(mod => mod.AdminSectionHeader));
const Tabs = dynamic(() => import("@/shared/components/ui/tabs").then(mod => mod.Tabs));
const TabsContent = dynamic(() => import("@/shared/components/ui/tabs").then(mod => mod.TabsContent));
const TabsList = dynamic(() => import("@/shared/components/ui/tabs").then(mod => mod.TabsList));
const TabsTrigger = dynamic(() => import("@/shared/components/ui/tabs").then(mod => mod.TabsTrigger));

export default function AdminPage() {
  const { data: health, isLoading, isError, refetch, isFetching } = useSystemHealth();

  if (isLoading) {
    return (
      <AppLayout>
        <AdminLoadingState />
      </AppLayout>
    );
  }

  if (isError || !health) {
    return (
      <AppLayout>
        <AdminEmptyState onRetry={refetch} />
      </AppLayout>
    );
  }

  const apiStatus = health.status;
  const redisStatus = health.checks?.redis?.status || "unknown";
  const vectorStatus = health.checks?.vector_store?.status || "unknown";
  const storageStatus = health.checks?.storage?.status || "unknown";

  const aiServices: AdminServiceInfo[] = [
    {
      id: "llm",
      name: "Language Model",
      description: "Core reasoning engine powered by Google Gemini API.",
      status: "up",
      provider: "Google Cloud",
      modelName: "gemini-1.5-pro",
      version: "v1.5",
      metrics: [
        { name: "Avg Token/sec", value: 45 },
        { name: "Success Rate", value: "99.8%" }
      ]
    },
    {
      id: "embedding",
      name: "Embeddings Engine",
      description: "Local vector embedding generation for semantic search.",
      status: "up",
      provider: "HuggingFace",
      modelName: "sentence-transformers/all-MiniLM-L6-v2",
      metrics: [
        { name: "Dim Size", value: 384 },
        { name: "Batch Latency", value: "12ms" }
      ]
    },
    {
      id: "reranker",
      name: "Cross-Encoder Reranker",
      description: "Secondary relevance verification for hybrid retrieval.",
      status: "up",
      provider: "HuggingFace",
      modelName: "cross-encoder/ms-marco-MiniLM-L-6-v2",
      metrics: [
        { name: "Re-rank Time", value: "150ms" }
      ]
    }
  ];

  const infrastructure: InfrastructureStatus[] = [
    { id: "docker", name: "Docker Containerization", status: "configured", description: "Multi-stage production builds for backend and frontend." },
    { id: "actions", name: "CI/CD Pipeline", status: "integrated", description: "GitHub Actions automated testing and deployment." },
    { id: "prometheus", name: "Prometheus Monitoring", status: "integrated", description: "Real-time metrics collection and alerting." }
  ];

  return (
    <AppLayout>
      <div className="flex gap-8">
        <AdminSidebar />

        <div className="flex-1">
          <AdminLayout onRefresh={refetch} isRefreshing={isFetching}>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-10">
              <StatusCard
                title="API Service"
                description="Core Backend Engine"
                status={apiStatus}
                icon={Globe}
                metric="v1.0.0"
              />
              <StatusCard
                title="Redis Cache"
                description="State & Session Store"
                status={redisStatus}
                icon={Zap}
                metric={health.checks?.redis?.ping === 'pong' ? 'PONG' : 'Down'}
              />
              <StatusCard
                title="Vector Store"
                description="Semantic Search Index"
                status={vectorStatus}
                icon={Database}
                metric={`${health.checks?.vector_store?.index_size || 0} Chunks`}
              />
              <StatusCard
                title="File Storage"
                description="Legal Document Repository"
                status={storageStatus}
                icon={HardDrive}
                metric="Local FS"
              />
            </div>

            <Tabs defaultValue="health" className="space-y-6">
              <TabsList className="bg-muted/50 p-1 border rounded-lg">
                <TabsTrigger value="health" className="gap-2">
                  <Activity className="h-4 w-4" /> System Health
                </TabsTrigger>
                <TabsTrigger value="services" className="gap-2">
                  <Cpu className="h-4 w-4" /> AI Services
                </TabsTrigger>
                <TabsTrigger value="infra" className="gap-2">
                  <Cloud className="h-4 w-4" /> Infrastructure
                </TabsTrigger>
                <TabsTrigger value="ops" className="gap-2">
                  <Layout className="h-4 w-4" /> Operations
                </TabsTrigger>
              </TabsList>

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <TabsContent value="health" className="space-y-6">
                  <AdminSectionHeader
                    title="Live System Health"
                    description="Real-time monitoring of critical backend subsystems."
                  />
                  <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    <HealthCard
                      name="Application Instance"
                      status={apiStatus}
                      message={`Instance running in ${health.environment} mode.`}
                      details={{
                        version: health.version,
                        environment: health.environment,
                        timestamp: health.timestamp
                      }}
                    />
                    <HealthCard
                      name="Vector Database"
                      status={vectorStatus}
                      message={health.checks?.vector_store?.status === 'up' ? "FAISS Index is loaded and ready." : "Index failure detected."}
                      details={health.checks?.vector_store}
                    />
                    <HealthCard
                      name="Redis Persistence"
                      status={redisStatus}
                      message={health.checks?.redis?.message}
                      details={health.checks?.redis}
                    />
                  </div>
                </TabsContent>

                <TabsContent value="services" className="space-y-6">
                  <AdminSectionHeader
                    title="AI Services & Models"
                    description="Status and metrics for deployed LLM and Embedding models."
                  />
                  <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {aiServices.map((service) => (
                      <ServiceCard key={service.id} service={service} />
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="infra" className="space-y-6">
                  <AdminSectionHeader
                    title="Infrastructure & Deployment"
                    description="Readiness and configuration status of the platform infrastructure stack."
                  />
                  <div className="grid gap-6 md:grid-cols-2">
                    {infrastructure.map((item) => (
                      <InfrastructureCard key={item.id} item={item} />
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="ops" className="space-y-6">
                  <AdminSectionHeader
                    title="Platform Operations"
                    description="Administrative controls and maintenance tasks."
                  />
                  <div className="grid gap-6 md:grid-cols-2">
                    <div className="p-6 rounded-xl border bg-card space-y-4 shadow-sm hover:shadow-md transition-all">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-primary/10 text-primary">
                                <Database className="h-5 w-5" />
                            </div>
                            <h4 className="font-black uppercase tracking-tight">Cache Management</h4>
                        </div>
                        <p className="text-sm text-muted-foreground leading-relaxed">Clear Redis cache, reset session states, and invalidate RAG response buffers.</p>
                        <div className="pt-2 flex flex-wrap gap-3">
                            <button className="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-destructive/90 transition-colors shadow-sm">
                                FLUSH ALL CACHE
                            </button>
                            <button className="px-4 py-2 border rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-muted transition-colors shadow-sm">
                                RE-INDEX FRAGMENTS
                            </button>
                        </div>
                    </div>

                    <div className="p-6 rounded-xl border bg-card space-y-4 shadow-sm hover:shadow-md transition-all">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-primary/10 text-primary">
                                <LineChart className="h-5 w-5" />
                            </div>
                            <h4 className="font-black uppercase tracking-tight">System Maintenance</h4>
                        </div>
                        <p className="text-sm text-muted-foreground leading-relaxed">Perform cleanup of orphaned document fragments and expired user sessions.</p>
                        <div className="pt-2">
                            <button className="w-full px-4 py-2 border rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-muted transition-colors flex items-center justify-center gap-2 shadow-sm">
                                <RefreshCw className="h-3.5 w-3.5" />
                                RUN MAINTENANCE SERVICE
                            </button>
                        </div>
                    </div>

                    <div className="md:col-span-2 p-10 border-2 border-dashed rounded-2xl bg-muted/20 text-center space-y-4">
                        <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mx-auto mb-2 border border-muted-foreground/20">
                           <Lock className="h-6 w-6 text-muted-foreground/50" />
                        </div>
                        <h5 className="text-sm font-black uppercase tracking-[0.2em] text-muted-foreground/60">Advanced Controls (Roadmap)</h5>
                        <p className="text-xs text-muted-foreground max-w-lg mx-auto italic leading-relaxed">
                          User RBAC, API Key Governance, and Production Audit Logs will be available in the upcoming Enterprise Governance v2.0 update.
                        </p>
                    </div>
                  </div>
                </TabsContent>
              </motion.div>
            </Tabs>
          </AdminLayout>
        </div>
      </div>
    </AppLayout>
  );
}
