import { defineStore } from "pinia";
import { ref } from "vue";

import { fetchDashboardKpis } from "@/services/dashboard";
import { useEventsStore } from "./events";

export const useDashboardStore = defineStore("dashboard", () => {
  const kpis = ref(null);
  const isLoading = ref(false);
  const lastUpdated = ref(null);

  async function loadKpis() {
    isLoading.value = true;
    try {
      kpis.value = await fetchDashboardKpis();
      lastUpdated.value = new Date();
    } catch {
      // utente senza tenant (es. admin) — non mostrare KPI tenant-aware
    } finally {
      isLoading.value = false;
    }
  }

  function setupEventListeners() {
    const eventsStore = useEventsStore();
    eventsStore.on("kpi.updated", () => {
      loadKpis();
    });
  }

  return { kpis, isLoading, lastUpdated, loadKpis, setupEventListeners };
});
