import { computed, ref } from "vue";
import { defineStore } from "pinia";

import {
  fetchNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from "@/services/notifications";
import { useEventsStore } from "./events";

export const useNotificationsStore = defineStore("notifications", () => {
  const items = ref([]);
  const unreadCount = computed(() => items.value.filter((n) => !n.is_read).length);
  const isLoading = ref(false);

  async function load() {
    isLoading.value = true;
    try {
      const data = await fetchNotifications();
      items.value = data.items;
    } finally {
      isLoading.value = false;
    }
  }

  async function markRead(id) {
    await markNotificationRead(id);
    const n = items.value.find((x) => x.id === id);
    if (n) n.is_read = true;
  }

  async function markAllRead() {
    await markAllNotificationsRead();
    items.value.forEach((n) => {
      n.is_read = true;
    });
  }

  function setupEventListeners() {
    const eventsStore = useEventsStore();
    eventsStore.on("notification.new", (event) => {
      items.value.unshift({ ...event.payload, is_read: false });
    });
  }

  return { items, unreadCount, isLoading, load, markRead, markAllRead, setupEventListeners };
});
