import axios from "axios";

import { useDemo } from "../composables/useDemo";
import { useAuthStore } from "../stores/auth";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// Lock single-flight in-memory: blocca refresh paralleli nella stessa tab.
let refreshInCorso = null;

// Serializza il refresh anche fra tab del browser (Web Locks API).
// Allineato a Auth0 SPA SDK e altre librerie enterprise: la prima tab che
// ottiene il lock esegue il refresh, le altre attendono e poi rileggono lo
// stato auth gia' aggiornato senza rifare un secondo refresh.
async function refreshConLockCrossTab() {
  const authStore = useAuthStore();

  if (typeof navigator !== "undefined" && navigator.locks?.request) {
    return navigator.locks.request("Gestionale-auth-refresh", async () => {
      // Quando vinciamo il lock potremmo essere la prima tab oppure la seconda
      // che attendeva: se la sessione e' gia' fresca, non rifacciamo refresh.
      if (authStore.accessTokenEFresco()) return;
      await authStore.refreshSessione();
    });
  }

  // Fallback per browser legacy senza Web Locks: solo lock in-memory.
  await authStore.refreshSessione();
}

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

    // Modalita demo: scrittura bloccata dal backend con 403 + flag demo_readonly.
    if (statusCode === 403 && error.response?.data?.demo_readonly) {
      useDemo().segnalaBlocco(error.response.data.detail);
      return Promise.reject(error);
    }

    if (
      statusCode === 401 &&
      !richiestaOriginale?._retry &&
      !richiestaOriginale?.url?.includes("/auth/login") &&
      !richiestaOriginale?.url?.includes("/auth/refresh")
    ) {
      richiestaOriginale._retry = true;

      try {
        refreshInCorso ??= refreshConLockCrossTab();
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
