import { apiClient } from "@/lib/http";

export async function fetchAnagrafiche(params = {}) {
  const { data } = await apiClient.get("/anagrafiche", { params });
  return data;
}

export async function fetchAnagrafica(id) {
  const { data } = await apiClient.get(`/anagrafiche/${id}`);
  return data;
}

export async function createAnagrafica(payload) {
  const { data } = await apiClient.post("/anagrafiche", payload);
  return data;
}

export async function updateAnagrafica(id, payload) {
  const { data } = await apiClient.patch(`/anagrafiche/${id}`, payload);
  return data;
}

export async function deleteAnagrafica(id) {
  await apiClient.delete(`/anagrafiche/${id}`);
}
