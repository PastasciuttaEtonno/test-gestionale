import { apiClient } from "../lib/http";

export async function avviaGenerazioneReport(payload) {
  const response = await apiClient.post("/reports/generate", payload);
  return response.data;
}

export async function recuperaStatoTask(taskId) {
  const response = await apiClient.get(`/tasks/${taskId}/status`);
  return response.data;
}
