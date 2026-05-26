<script setup>
import { useNotificationsStore } from "@/stores/notifications";

const notificationsStore = useNotificationsStore();

function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return d.toLocaleDateString("it-IT", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const eventTypeLabel = {
  "task.completed": "Task completato",
  "task.failed": "Task fallito",
  "report.ready": "Report pronto",
  "notification.new": "Notifica",
  "system.alert": "Avviso sistema",
  "kpi.updated": "KPI aggiornati",
};

function labelFor(type) {
  return eventTypeLabel[type] || type;
}
</script>

<template>
  <div class="w-80 rounded-2xl border border-steel-200 bg-white shadow-xl">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-steel-100 px-4 py-3">
      <span class="text-sm font-semibold text-steel-900">Notifiche</span>
      <button
        v-if="notificationsStore.unreadCount > 0"
        class="text-xs font-medium text-brand-600 hover:underline"
        @click="notificationsStore.markAllRead()"
      >
        Segna tutte come lette
      </button>
    </div>

    <!-- List -->
    <div class="max-h-96 overflow-y-auto">
      <div
        v-if="notificationsStore.isLoading"
        class="flex items-center justify-center py-8 text-sm text-steel-400"
      >
        Caricamento…
      </div>

      <div
        v-else-if="notificationsStore.items.length === 0"
        class="flex flex-col items-center gap-2 py-10 text-sm text-steel-400"
      >
        <svg class="h-8 w-8 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0a3 3 0 11-6 0m6 0H9" />
        </svg>
        <span>Nessuna notifica</span>
      </div>

      <ul v-else>
        <li
          v-for="n in notificationsStore.items"
          :key="n.id"
          class="flex cursor-pointer gap-3 border-b border-steel-50 px-4 py-3 transition hover:bg-steel-50"
          :class="{ 'bg-brand-50/40': !n.is_read }"
          @click="!n.is_read && notificationsStore.markRead(n.id)"
        >
          <!-- Dot non letto -->
          <span
            class="mt-1 h-2 w-2 shrink-0 rounded-full"
            :class="n.is_read ? 'bg-transparent' : 'bg-brand-500'"
          />
          <div class="min-w-0 flex-1">
            <div class="flex items-start justify-between gap-2">
              <p class="text-sm font-medium text-steel-900 leading-tight">{{ n.title }}</p>
              <span class="shrink-0 text-[10px] text-steel-400">{{ formatDate(n.created_at) }}</span>
            </div>
            <p class="mt-0.5 text-xs text-steel-500 leading-snug">{{ n.body }}</p>
            <span class="mt-1 inline-block rounded-md bg-steel-100 px-1.5 py-0.5 text-[10px] font-medium text-steel-500">
              {{ labelFor(n.event_type) }}
            </span>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>
