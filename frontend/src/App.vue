<script setup>
import { computed, onMounted, watch } from "vue";
import { RouterView, useRoute, useRouter } from "vue-router";

import AppShell from "./components/layout/AppShell.vue";
import ConfirmDialog from "./components/ui/ConfirmDialog.vue";
import { useDemo } from "./composables/useDemo";
import { apiClient } from "./lib/http";
import { useAuthStore } from "./stores/auth";
import { useDashboardStore } from "./stores/dashboard";
import { useEventsStore } from "./stores/events";
import { useNotificationsStore } from "./stores/notifications";
import { useTasksStore } from "./stores/tasks";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const eventsStore = useEventsStore();
const notificationsStore = useNotificationsStore();
const tasksStore = useTasksStore();
const dashboardStore = useDashboardStore();
const demo = useDemo();

onMounted(async () => {
  try {
    const { data } = await apiClient.get("/meta");
    demo.impostaReadonly(data?.demo_readonly);
  } catch {
    // Se /meta non risponde, si assume modalita scrivibile.
  }
});

notificationsStore.setupEventListeners();
tasksStore.setupEventListeners();
dashboardStore.setupEventListeners();

const utente = computed(() => authStore.user);
const mostraShell = computed(() => route.meta.hideShell !== true);
const mostraNavigazioneAdmin = computed(() => authStore.hasRole("admin"));
const mostraNavigazioneTenantAdmin = computed(() => authStore.hasRole("tenant_admin"));

watch(
  () => authStore.accessToken,
  (token) => {
    if (token) {
      eventsStore.connect(token);
      notificationsStore.load();
      dashboardStore.loadKpis();
    } else {
      eventsStore.disconnect();
    }
  },
  { immediate: true },
);

async function eseguiLogout() {
  await authStore.logout();
  router.push({ name: "login" });
}
</script>

<template>
  <!-- Banner persistente modalita demo -->
  <div
    v-if="demo.readonly.value"
    class="flex items-center justify-center gap-2 bg-amber-500 px-4 py-1.5 text-center text-xs font-semibold text-amber-950"
  >
    <span class="inline-block h-2 w-2 rounded-full bg-amber-900"></span>
    Modalità demo — sola lettura: le modifiche non vengono salvate. La
    generazione report asincrona resta attiva.
  </div>

  <AppShell
    :mostra-shell="mostraShell"
    :route-name="String(route.name || '')"
    :username="utente?.username || ''"
    :role-code="utente?.role_code || ''"
    :mostra-navigazione-admin="mostraNavigazioneAdmin"
    :mostra-navigazione-tenant-admin="mostraNavigazioneTenantAdmin"
    @logout="eseguiLogout"
  >
    <RouterView />
  </AppShell>

  <!-- Toast transiente quando una scrittura viene bloccata in demo -->
  <Transition name="fade">
    <div
      v-if="demo.avviso.value"
      class="fixed bottom-6 left-1/2 z-[60] -translate-x-1/2 rounded-lg bg-steel-900 px-4 py-2.5 text-sm font-medium text-white shadow-xl"
      role="status"
    >
      {{ demo.avviso.value }}
    </div>
  </Transition>

  <ConfirmDialog />
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
