import { apiClient } from "../lib/http";

// Entrambe le rotte restituiscono gli eventi dal piu' recente.

export async function fetchAuditTenant(params = {}) {
  const { data } = await apiClient.get("/tenant-admin/audit-log", { params });
  return data;
}

export async function fetchAuditGlobale(params = {}) {
  const { data } = await apiClient.get("/admin/audit-log", { params });
  return data;
}
