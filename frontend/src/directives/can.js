import { watchEffect } from "vue";

import { useAuthStore } from "../stores/auth";

function resolvePermission(binding) {
  if (typeof binding.value === "string") {
    return { permission: binding.value, mode: "single" };
  }

  if (Array.isArray(binding.value)) {
    return { permissions: binding.value, mode: "every" };
  }

  if (binding.value && typeof binding.value === "object") {
    return {
      permission: binding.value.permission,
      permissions: binding.value.permissions || [],
      mode: binding.value.mode || "single",
    };
  }

  return { permission: null, permissions: [], mode: "single" };
}

function evaluatePermission(authStore, binding) {
  const resolved = resolvePermission(binding);

  if (resolved.mode === "any") {
    return authStore.hasAnyPermission(resolved.permissions);
  }

  if (resolved.mode === "every") {
    return authStore.hasEveryPermission(resolved.permissions);
  }

  if (resolved.permission) {
    return authStore.hasPermission(resolved.permission);
  }

  return false;
}

export function createCanDirective() {
  return {
    mounted(element, binding) {
      const authStore = useAuthStore();
      const parent = element.parentNode;
      const placeholder = document.createComment("v-can");

      const stopWatcher = watchEffect(() => {
        const isAllowed = evaluatePermission(authStore, binding);

        if (isAllowed) {
          if (placeholder.parentNode) {
            placeholder.parentNode.replaceChild(element, placeholder);
          }
          return;
        }

        if (parent && element.parentNode === parent) {
          parent.replaceChild(placeholder, element);
        }
      });

      element.__canCleanup = stopWatcher;
    },
    unmounted(element) {
      element.__canCleanup?.();
      delete element.__canCleanup;
    },
  };
}
