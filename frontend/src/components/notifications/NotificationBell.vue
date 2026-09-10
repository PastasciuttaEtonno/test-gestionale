<script setup>
import { ref } from "vue";

import { useNotificationsStore } from "@/stores/notifications";
import NotificationPanel from "./NotificationPanel.vue";

const notificationsStore = useNotificationsStore();
const isOpen = ref(false);

function toggle() {
  isOpen.value = !isOpen.value;
  if (isOpen.value && notificationsStore.items.length === 0) {
    notificationsStore.load();
  }
}

function close() {
  isOpen.value = false;
}
</script>

<template>
  <div class="relative">
    <button
      v-tooltip.bottom="'Notifiche'"
      aria-label="Notifiche"
      type="button"
      class="relative flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-steel-200 bg-steel-50 text-steel-700 transition hover:bg-steel-100"
      @click="toggle"
    >
      <!-- Icona campanellino -->
      <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0a3 3 0 11-6 0m6 0H9" />
      </svg>

      <!-- Badge contatore -->
      <span
        v-if="notificationsStore.unreadCount > 0"
        class="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-brand-500 px-1 text-[10px] font-bold text-white"
      >
        {{ notificationsStore.unreadCount > 99 ? "99+" : notificationsStore.unreadCount }}
      </span>
    </button>

    <!-- Panel dropdown -->
    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="opacity-0 scale-95 -translate-y-1"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 -translate-y-1"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 top-13 z-50 origin-top-right"
      >
        <NotificationPanel />
      </div>
    </Transition>

    <!-- Overlay click-fuori -->
    <div
      v-if="isOpen"
      class="fixed inset-0 z-40"
      @click="close"
    />
  </div>
</template>
