import { apiClient } from "@/core/api/client";
import { FullHealthReport } from "../types";

export const adminApi = {
  getHealth: () => apiClient.get<FullHealthReport>("/health"),
  getMetrics: () => apiClient.get<string>("/metrics"),
};
