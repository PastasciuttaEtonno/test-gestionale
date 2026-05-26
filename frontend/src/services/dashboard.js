import { apiClient } from "@/lib/http";

export async function fetchDashboardKpis() {
  const { data } = await apiClient.get("/dashboard/kpis");
  return data;
}
