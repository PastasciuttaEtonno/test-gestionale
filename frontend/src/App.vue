<script setup>
import { computed } from "vue";
import { RouterView, useRoute, useRouter } from "vue-router";

import AppShell from "./components/layout/AppShell.vue";
import { useAuthStore } from "./stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const utente = computed(() => authStore.user);
const mostraShell = computed(() => route.meta.hideShell !== true);
const mostraNavigazioneAdmin = computed(() => authStore.hasRole("admin"));
const mostraNavigazioneTenantAdmin = computed(() => authStore.hasRole("tenant_admin"));

async function eseguiLogout() {
  await authStore.logout();
  router.push({ name: "login" });
}
</script>

<template>
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
</template>
