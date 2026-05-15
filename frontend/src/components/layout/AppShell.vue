<script setup>
import { RouterLink } from "vue-router";

import BaseButton from "../ui/BaseButton.vue";
import RoleBadge from "../ui/RoleBadge.vue";

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
</script>

<template>
  <div class="min-h-screen w-full bg-[radial-gradient(circle_at_top,_rgba(198,40,40,0.14),_transparent_34%),linear-gradient(180deg,_#fafbfc_0%,_#f1f3f5_100%)]">
    <header
      v-if="mostraShell"
      class="border-b border-steel-200 bg-white/92 backdrop-blur"
    >
      <div class="flex w-full items-center gap-8 px-6 py-4 2xl:px-8">
        <div class="flex min-w-0 items-center gap-4">
          <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-brand-500 text-sm font-semibold uppercase tracking-[0.2em] text-white">
            ES
          </div>
          <div class="min-w-0">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-brand-700">
              Esseduesoft
            </p>
            <h1 class="truncate text-base font-semibold text-steel-900">
              Frontend di test Auth
            </h1>
          </div>
        </div>

        <nav class="flex flex-1 items-center justify-center gap-3">
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

        <div class="flex items-center justify-end gap-3">
          <div class="flex h-11 items-center gap-3 rounded-xl border border-steel-200 bg-steel-50 px-4">
            <p class="truncate text-sm font-medium text-steel-900">{{ username }}</p>
            <RoleBadge :role-code="roleCode" />
          </div>
          <BaseButton type="button" variant="secondary" @click="$emit('logout')">
            Logout
          </BaseButton>
        </div>
      </div>
    </header>

    <main class="w-full px-6 py-8 2xl:px-8">
      <slot />
    </main>
  </div>
</template>
