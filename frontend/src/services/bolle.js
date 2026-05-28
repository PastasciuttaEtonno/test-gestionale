import { apiClient } from "@/lib/http";

// ── Testata ──────────────────────────────────────────────────────────────

export async function fetchBolle(params = {}) {
  const { data } = await apiClient.get("/bolle", { params });
  return data;
}

export async function fetchBolla(id) {
  const { data } = await apiClient.get(`/bolle/${id}`);
  return data;
}

export async function createBolla(payload) {
  const { data } = await apiClient.post("/bolle", payload);
  return data;
}

export async function updateBolla(id, payload) {
  const { data } = await apiClient.patch(`/bolle/${id}`, payload);
  return data;
}

export async function deleteBolla(id) {
  await apiClient.delete(`/bolle/${id}`);
}

export async function emettiBolla(id) {
  const { data } = await apiClient.post(`/bolle/${id}/emetti`);
  return data;
}

export async function annullaBolla(id) {
  const { data } = await apiClient.post(`/bolle/${id}/annulla`);
  return data;
}

// ── Righe ──────────────────────────────────────────────────────────────────

export async function addRiga(bollaId, payload) {
  const { data } = await apiClient.post(`/bolle/${bollaId}/righe`, payload);
  return data;
}

export async function updateRiga(bollaId, rigaId, payload) {
  const { data } = await apiClient.patch(`/bolle/${bollaId}/righe/${rigaId}`, payload);
  return data;
}

export async function deleteRiga(bollaId, rigaId) {
  const { data } = await apiClient.delete(`/bolle/${bollaId}/righe/${rigaId}`);
  return data;
}
