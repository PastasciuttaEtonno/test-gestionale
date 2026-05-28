import { apiClient } from "@/lib/http";

// ── Articoli ───────────────────────────────────────────────────────────────

export async function fetchArticoli(params = {}) {
  const { data } = await apiClient.get("/articoli", { params });
  return data;
}

export async function fetchArticolo(id) {
  const { data } = await apiClient.get(`/articoli/${id}`);
  return data;
}

export async function createArticolo(payload) {
  const { data } = await apiClient.post("/articoli", payload);
  return data;
}

export async function updateArticolo(id, payload) {
  const { data } = await apiClient.patch(`/articoli/${id}`, payload);
  return data;
}

export async function deleteArticolo(id) {
  await apiClient.delete(`/articoli/${id}`);
}

// ── Categorie articolo ───────────────────────────────────────────────────────

export async function fetchCategorie(params = {}) {
  const { data } = await apiClient.get("/articoli/categorie", { params });
  return data;
}

export async function createCategoria(payload) {
  const { data } = await apiClient.post("/articoli/categorie", payload);
  return data;
}

export async function updateCategoria(id, payload) {
  const { data } = await apiClient.patch(`/articoli/categorie/${id}`, payload);
  return data;
}

export async function deleteCategoria(id) {
  await apiClient.delete(`/articoli/categorie/${id}`);
}
