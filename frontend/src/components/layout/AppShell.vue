<script setup>
import { watch } from "vue";
import { RouterLink } from "vue-router";
import Avatar from "primevue/avatar";

import NotificationBell from "../notifications/NotificationBell.vue";
import BaseButton from "../ui/BaseButton.vue";
import RoleBadge from "../ui/RoleBadge.vue";
import { useSidebar } from "../../composables/useSidebar";

const props = defineProps({
  mostraShell: { type: Boolean, default: true },
  routeName: { type: String, default: "" },
  username: { type: String, default: "" },
  roleCode: { type: String, default: "" },
  mostraNavigazioneAdmin: { type: Boolean, default: false },
  mostraNavigazioneTenantAdmin: { type: Boolean, default: false },
});

defineEmits(["logout"]);

const { drawerAperto, toggleDrawer, chiudiDrawer } = useSidebar();

// Chiude il drawer quando cambia route (navigazione da mobile)
watch(() => props.routeName, chiudiDrawer);

const vociMockup = ["Bolle", "Fatture", "Spedizioni", "Scadenze"];
</script>

<template>
  <div class="min-h-screen w-full bg-[radial-gradient(circle_at_top,_rgba(198,40,40,0.14),_transparent_34%),linear-gradient(180deg,_#fafbfc_0%,_#f1f3f5_100%)]">

    <template v-if="mostraShell">

      <!-- ── Header ────────────────────────────────────────────────────── -->
      <header class="sticky top-0 z-20 border-b border-steel-200 bg-white/92 backdrop-blur">
        <div class="flex w-full items-center gap-4 px-4 py-4 sm:px-6 2xl:px-8">

          <!-- Burger (mobile) -->
          <button
            v-tooltip.right="'Apri menu laterale'"
            type="button"
            class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-steel-200 bg-steel-50 text-steel-700 transition hover:bg-steel-100 xl:hidden"
            @click="toggleDrawer"
          >
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>

          <!-- Brand -->
          <div class="flex items-center gap-3">
            <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-brand-500 text-sm font-semibold uppercase tracking-[0.2em] text-white">
              ES
            </div>
            <div class="min-w-0 hidden sm:block">
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-brand-700">Gestionale</p>
              <h1 class="truncate text-base font-semibold text-steel-900">Gestionale aziendale</h1>
            </div>
          </div>

          <!-- Spacer -->
          <div class="flex-1" />

          <!-- User area -->
          <div class="flex items-center gap-3">
            <NotificationBell />
            <div class="hidden h-11 items-center gap-3 rounded-xl border border-steel-200 bg-steel-50 px-3 xl:flex">
              <Avatar
                :label="username ? username.charAt(0).toUpperCase() : '?'"
                :pt="{
                  root: {
                    class: 'flex h-7 w-7 shrink-0 select-none items-center justify-center rounded-full bg-brand-500 text-xs font-semibold text-white',
                  },
                }"
              />
              <p class="truncate text-sm font-medium text-steel-900">{{ username }}</p>
              <RoleBadge :role-code="roleCode" />
            </div>
            <BaseButton
              v-tooltip.bottom="'Esegui logout'"
              type="button"
              variant="secondary"
              @click="$emit('logout')"
            >
              <span class="xl:hidden">Esci</span>
              <span class="hidden xl:inline">Logout</span>
            </BaseButton>
          </div>

        </div>
      </header>

      <!-- ── Layout: sidebar + contenuto ──────────────────────────────── -->
      <div class="relative xl:grid xl:grid-cols-[248px_minmax(0,1fr)]">

        <!-- Overlay scrim (mobile) -->
        <Transition name="fade">
          <div
            v-if="drawerAperto"
            class="fixed inset-0 z-30 bg-steel-900/60 xl:hidden"
            @click="chiudiDrawer"
          />
        </Transition>

        <!-- Sidebar -->
        <aside
          :class="drawerAperto ? 'translate-x-0' : '-translate-x-full'"
          class="fixed inset-y-0 left-0 z-40 flex w-72 flex-col overflow-y-auto bg-[#232a31] p-4 text-white transition-transform duration-300 xl:sticky xl:top-0 xl:z-auto xl:h-screen xl:w-auto xl:translate-x-0 xl:overflow-y-auto"
        >

          <!-- Chiudi (mobile) -->
          <div class="mb-5 flex items-center justify-between xl:hidden">
            <span class="text-xs font-semibold uppercase tracking-[0.28em] text-brand-100">Navigazione</span>
            <button
              type="button"
              class="flex h-9 w-9 items-center justify-center rounded-xl text-white/60 transition hover:bg-white/10 hover:text-white"
              @click="chiudiDrawer"
            >
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <!-- Navigazione reale -->
          <nav class="space-y-1">
            <p class="mb-2 px-3 text-[11px] font-semibold uppercase tracking-[0.24em] text-white/38">
              Moduli
            </p>

            <!-- Dashboard -->
            <RouterLink
              to="/dashboard"
              class="group flex h-12 w-full items-center rounded-xl border border-transparent px-3 text-sm font-medium text-white/76 transition hover:border-white/8 hover:bg-white/8 hover:text-white"
              :class="{ 'border-brand-300/22 bg-brand-500 text-white shadow-[0_10px_24px_-16px_rgba(198,40,40,0.9)]': routeName === 'dashboard' }"
            >
              <span
                class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/8 transition group-hover:bg-white/12"
                :class="{ 'bg-white/14': routeName === 'dashboard' }"
              >
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="7" height="7" rx="1"/>
                  <rect x="14" y="3" width="7" height="7" rx="1"/>
                  <rect x="3" y="14" width="7" height="7" rx="1"/>
                  <rect x="14" y="14" width="7" height="7" rx="1"/>
                </svg>
              </span>
              <span class="ml-3 truncate">Dashboard</span>
            </RouterLink>

            <!-- Anagrafiche -->
            <RouterLink
              to="/anagrafiche"
              class="group flex h-12 w-full items-center rounded-xl border border-transparent px-3 text-sm font-medium text-white/76 transition hover:border-white/8 hover:bg-white/8 hover:text-white"
              :class="{ 'border-brand-300/22 bg-brand-500 text-white shadow-[0_10px_24px_-16px_rgba(198,40,40,0.9)]': routeName === 'anagrafiche' || routeName === 'anagrafica-detail' }"
            >
              <span
                class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/8 transition group-hover:bg-white/12"
                :class="{ 'bg-white/14': routeName === 'anagrafiche' || routeName === 'anagrafica-detail' }"
              >
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
              </span>
              <span class="ml-3 truncate">Anagrafiche</span>
            </RouterLink>

            <!-- Articoli -->
            <RouterLink
              to="/articoli"
              class="group flex h-12 w-full items-center rounded-xl border border-transparent px-3 text-sm font-medium text-white/76 transition hover:border-white/8 hover:bg-white/8 hover:text-white"
              :class="{ 'border-brand-300/22 bg-brand-500 text-white shadow-[0_10px_24px_-16px_rgba(198,40,40,0.9)]': routeName === 'articoli' || routeName === 'articolo-detail' }"
            >
              <span
                class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/8 transition group-hover:bg-white/12"
                :class="{ 'bg-white/14': routeName === 'articoli' || routeName === 'articolo-detail' }"
              >
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-14L4 7m8 4v10m0 0l-8-4V7"/>
                </svg>
              </span>
              <span class="ml-3 truncate">Articoli</span>
            </RouterLink>

            <!-- Tenant Admin -->
            <RouterLink
              v-if="mostraNavigazioneTenantAdmin"
              to="/tenant-admin"
              class="group flex h-12 w-full items-center rounded-xl border border-transparent px-3 text-sm font-medium text-white/76 transition hover:border-white/8 hover:bg-white/8 hover:text-white"
              :class="{ 'border-brand-300/22 bg-brand-500 text-white shadow-[0_10px_24px_-16px_rgba(198,40,40,0.9)]': routeName === 'tenant-admin' }"
            >
              <span
                class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/8 transition group-hover:bg-white/12"
                :class="{ 'bg-white/14': routeName === 'tenant-admin' }"
              >
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                  <polyline points="9 22 9 12 15 12 15 22"/>
                </svg>
              </span>
              <span class="ml-3 truncate">Tenant Admin</span>
            </RouterLink>

            <!-- Super Admin -->
            <RouterLink
              v-if="mostraNavigazioneAdmin"
              to="/admin-only"
              class="group flex h-12 w-full items-center rounded-xl border border-transparent px-3 text-sm font-medium text-white/76 transition hover:border-white/8 hover:bg-white/8 hover:text-white"
              :class="{ 'border-brand-300/22 bg-brand-500 text-white shadow-[0_10px_24px_-16px_rgba(198,40,40,0.9)]': routeName === 'admin-only' }"
            >
              <span
                class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/8 transition group-hover:bg-white/12"
                :class="{ 'bg-white/14': routeName === 'admin-only' }"
              >
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
              </span>
              <span class="ml-3 truncate">Super Admin</span>
            </RouterLink>
          </nav>

          <!-- Moduli in arrivo (mockup, non cliccabili) -->
          <div class="mt-6">
            <p class="mb-2 px-3 text-[11px] font-semibold uppercase tracking-[0.24em] text-white/38">
              In arrivo
            </p>
            <div class="space-y-1">
              <div
                v-for="voce in vociMockup"
                :key="voce"
                class="flex h-12 w-full cursor-not-allowed items-center rounded-xl px-3 text-sm font-medium text-white/28"
              >
                <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/4 text-[11px] font-semibold uppercase tracking-[0.14em] text-white/24">
                  {{ voce.slice(0, 2) }}
                </span>
                <span class="ml-3 truncate">{{ voce }}</span>
                <span class="ml-auto text-[10px] uppercase tracking-widest text-white/20">Presto</span>
              </div>
            </div>
          </div>

          <!-- Spacer -->
          <div class="flex-1" />

          <!-- Alert card -->
          <div class="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-[11px] font-semibold uppercase tracking-[0.24em] text-white/42">Attenzione</p>
            <p class="mt-2 text-sm font-medium text-white">4 anagrafiche incomplete</p>
            <p class="mt-2 text-sm leading-6 text-white/68">
              Verificare indirizzi e dati fiscali prima della prossima emissione.
            </p>
          </div>

        </aside>

        <!-- Contenuto pagina -->
        <main class="min-w-0 px-4 py-6 sm:px-6 sm:py-8 2xl:px-8">
          <slot />
        </main>

      </div>

    </template>

    <!-- Pagine senza shell (login, 404) -->
    <template v-else>
      <slot />
    </template>

  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
