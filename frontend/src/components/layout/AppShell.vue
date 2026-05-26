<script setup>
import { RouterLink } from "vue-router";
import Avatar from "primevue/avatar";

import NotificationBell from "../notifications/NotificationBell.vue";
import BaseButton from "../ui/BaseButton.vue";
import RoleBadge from "../ui/RoleBadge.vue";
import { useSidebar } from "../../composables/useSidebar";

defineProps({
  mostraShell: {
    type: Boolean,
    default: true,
  },
  routeName: {
    type: String,
    default: "",
  },
  username: {
    type: String,
    default: "",
  },
  roleCode: {
    type: String,
    default: "",
  },
  mostraNavigazioneAdmin: {
    type: Boolean,
    default: false,
  },
  mostraNavigazioneTenantAdmin: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["logout"]);

const { toggleDrawer } = useSidebar();
</script>

<template>
  <div class="min-h-screen w-full bg-[radial-gradient(circle_at_top,_rgba(198,40,40,0.14),_transparent_34%),linear-gradient(180deg,_#fafbfc_0%,_#f1f3f5_100%)]">
    <header
      v-if="mostraShell"
      class="border-b border-steel-200 bg-white/92 backdrop-blur"
    >
      <div class="flex w-full items-center gap-4 px-4 py-4 sm:px-6 xl:gap-8 2xl:px-8">

        <!-- Burger menu (mobile only) -->
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
        <div class="flex flex-1 items-center gap-3 xl:flex-none">
          <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-brand-500 text-sm font-semibold uppercase tracking-[0.2em] text-white">
            ES
          </div>
          <div class="min-w-0">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-brand-700">
              Gestionale
            </p>
            <h1 class="truncate text-base font-semibold text-steel-900">
              Gestionale aziendale
            </h1>
          </div>
        </div>

        <!-- Nav (desktop only) -->
        <nav class="hidden flex-1 items-center justify-center gap-3 xl:flex">
          <RouterLink
            class="inline-flex h-11 items-center rounded-xl px-4 text-sm font-medium text-steel-700 transition hover:bg-steel-100"
            :class="{ 'bg-brand-50 text-brand-700': routeName === 'dashboard' }"
            :to="{ name: 'dashboard' }"
          >
            Dashboard
          </RouterLink>
          <RouterLink
            v-if="mostraNavigazioneTenantAdmin"
            class="inline-flex h-11 items-center rounded-xl px-4 text-sm font-medium text-steel-700 transition hover:bg-steel-100"
            :class="{ 'bg-brand-50 text-brand-700': routeName === 'tenant-admin' }"
            :to="{ name: 'tenant-admin' }"
          >
            Tenant Admin
          </RouterLink>
          <RouterLink
            v-if="mostraNavigazioneAdmin"
            class="inline-flex h-11 items-center rounded-xl px-4 text-sm font-medium text-steel-700 transition hover:bg-steel-100"
            :class="{ 'bg-brand-50 text-brand-700': routeName === 'admin-only' }"
            :to="{ name: 'admin-only' }"
          >
            Super Admin
          </RouterLink>
        </nav>

        <!-- User area -->
        <div class="flex items-center justify-end gap-3">
          <NotificationBell />
          <div class="hidden h-11 items-center gap-3 rounded-xl border border-steel-200 bg-steel-50 px-3 xl:flex">
            <Avatar
              :label="username ? username.charAt(0).toUpperCase() : '?'"
              :pt="{
                root: {
                  class:
                    'flex h-7 w-7 shrink-0 select-none items-center justify-center rounded-full bg-brand-500 text-xs font-semibold text-white',
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

    <main class="w-full px-4 py-6 sm:px-6 sm:py-8 2xl:px-8">
      <slot />
    </main>
  </div>
</template>
