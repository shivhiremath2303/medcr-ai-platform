import { useQuery } from "@tanstack/react-query";
import { adminApi } from "../api/admin-api";

export function useSystemHealth() {
  return useQuery({
    queryKey: ["admin", "health"],
    queryFn: adminApi.getHealth,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}
