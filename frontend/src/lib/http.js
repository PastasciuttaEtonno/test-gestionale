import axios from "axios";

import { useAuthStore } from "../stores/auth";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

let refreshInCorso = null;

apiClient.interceptors.request.use((config) => {
  const authStore = useAuthStore();

  if (authStore.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`;
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore();
    const richiestaOriginale = error.config;
    const statusCode = error.response?.status;

    if (
      statusCode === 401 &&
      !richiestaOriginale?._retry &&
      !richiestaOriginale?.url?.includes("/auth/login") &&
      !richiestaOriginale?.url?.includes("/auth/refresh")
    ) {
      richiestaOriginale._retry = true;

      try {
        refreshInCorso ??= authStore.refreshSessione();
        await refreshInCorso;
        richiestaOriginale.headers.Authorization = `Bearer ${authStore.accessToken}`;
        return apiClient(richiestaOriginale);
      } catch (refreshError) {
        await authStore.clearSessioneLocale();
        return Promise.reject(refreshError);
      } finally {
        refreshInCorso = null;
      }
    }

    return Promise.reject(error);
  },
);

export { apiClient };
