import { computed, ref } from "vue";
import { defineStore } from "pinia";

import {
  aggiornaToken,
  eseguiLogin,
  eseguiLogout,
} from "../services/auth";

export const useAuthStore = defineStore("auth", () => {
  const accessToken = ref(null);
  const user = ref(null);
  const isInitialized = ref(false);
  const isAuthenticated = computed(() => Boolean(accessToken.value && user.value));
  const roleCode = computed(() => user.value?.role_code || null);
  const permissions = computed(() => user.value?.permissions || []);

  async function initialize() {
    if (isInitialized.value) {
      return;
    }
    try {
      await refreshSessione();
    } catch {
      await clearSessioneLocale();
    }

    isInitialized.value = true;
  }

  async function login(payload) {
    const sessione = await eseguiLogin(payload);
    applicaSessione(sessione);
  }

  function applicaSessione(sessione) {
    accessToken.value = sessione.access_token;
    user.value = sessione.user;
  }

  async function refreshSessione() {
    const sessione = await aggiornaToken();
    applicaSessione(sessione);
  }

  async function logout() {
    try {
      if (accessToken.value) {
        await eseguiLogout();
      }
    } finally {
      await clearSessioneLocale();
    }
  }

  async function clearSessioneLocale() {
    accessToken.value = null;
    user.value = null;
  }

  function hasRole(...roles) {
    return Boolean(roleCode.value && roles.includes(roleCode.value));
  }

  function hasPermission(permissionCode) {
    return permissions.value.includes(permissionCode);
  }

  function hasEveryPermission(permissionCodes = []) {
    return permissionCodes.every((permissionCode) => hasPermission(permissionCode));
  }

  function hasAnyPermission(permissionCodes = []) {
    return permissionCodes.some((permissionCode) => hasPermission(permissionCode));
  }

  return {
    accessToken,
    user,
    isInitialized,
    isAuthenticated,
    roleCode,
    permissions,
    initialize,
    login,
    logout,
    refreshSessione,
    clearSessioneLocale,
    hasRole,
    hasPermission,
    hasEveryPermission,
    hasAnyPermission,
  };
});
