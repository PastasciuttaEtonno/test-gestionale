import { apiClient } from "../lib/http";

export async function eseguiLogin(payload) {
  const response = await apiClient.post("/auth/login", payload);
  return response.data;
}

export async function aggiornaToken() {
  const response = await apiClient.post("/auth/refresh");
  return response.data;
}

export async function eseguiLogout() {
  const response = await apiClient.post("/auth/logout");
  return response.data;
}
