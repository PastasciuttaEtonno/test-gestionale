import { defineStore } from "pinia";
import { ref } from "vue";

import { useEventsStore } from "./events";

export const useTasksStore = defineStore("tasks", () => {
  // taskId -> { status, progress, message, resultUrl }
  const taskMap = ref({});

  function getTask(taskId) {
    return taskMap.value[taskId] || null;
  }

  function initTask(taskId) {
    taskMap.value[taskId] = {
      status: "pending",
      progress: 0,
      message: "Task accodato, in attesa di avvio.",
      resultUrl: null,
    };
  }

  function setupEventListeners() {
    const eventsStore = useEventsStore();

    eventsStore.on("task.progress", (event) => {
      const { task_id, progress, message } = event.payload;
      if (taskMap.value[task_id]) {
        taskMap.value[task_id] = {
          ...taskMap.value[task_id],
          status: "progress",
          progress,
          message,
        };
      }
    });

    eventsStore.on("task.completed", (event) => {
      const { task_id, progress, message, result_url } = event.payload;
      if (taskMap.value[task_id]) {
        taskMap.value[task_id] = {
          status: "success",
          progress: progress ?? 100,
          message,
          resultUrl: result_url || null,
        };
      }
    });

    eventsStore.on("task.failed", (event) => {
      const { task_id, message } = event.payload;
      if (taskMap.value[task_id]) {
        taskMap.value[task_id] = {
          ...taskMap.value[task_id],
          status: "failure",
          message,
        };
      }
    });
  }

  return { taskMap, getTask, initTask, setupEventListeners };
});
