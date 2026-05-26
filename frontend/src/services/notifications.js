import { apiClient } from "@/lib/http";

export async function fetchNotifications({ limit = 30, offset = 0 } = {}) {
  const { data } = await apiClient.get("/notifications", {
    params: { limit, offset },
  });
  return data;
}

export async function markNotificationRead(id) {
  const { data } = await apiClient.patch(`/notifications/${id}/read`);
  return data;
}

export async function markAllNotificationsRead() {
  const { data } = await apiClient.post("/notifications/read-all");
  return data;
}

export async function sendTestNotification() {
  const { data } = await apiClient.post("/notifications/test");
  return data;
}
