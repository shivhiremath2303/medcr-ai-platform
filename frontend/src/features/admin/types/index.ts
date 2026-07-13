export type SystemStatus = "up" | "down" | "degraded" | "unknown";

export interface HealthCheckResult {
  status: SystemStatus;
  message?: string;
  timestamp?: string;
  [key: string]: any;
}

export interface FullHealthReport {
  status: SystemStatus;
  version: string;
  environment: string;
  timestamp: string;
  checks: Record<string, HealthCheckResult>;
}

export interface SystemMetric {
  name: string;
  value: number | string;
  unit?: string;
  status?: SystemStatus;
}

export interface AdminServiceInfo {
  id: string;
  name: string;
  description: string;
  status: SystemStatus;
  version?: string;
  modelName?: string;
  provider?: string;
  metrics?: SystemMetric[];
}

export interface InfrastructureStatus {
  id: string;
  name: string;
  status: "configured" | "integrated" | "planned" | "unavailable";
  description: string;
}
