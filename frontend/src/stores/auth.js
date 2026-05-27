import { computed, ref } from "vue";
import { defineStore } from "pinia";

import {
  aggiornaToken,
  eseguiLogin,
  eseguiLogout,
} from "../services/auth";

const SECONDI_BUFFER_FRESHEZZA = 30;

function decodificaScadenzaJwt(token) {
  if (!token || typeof token !== "string") return null;
  const parti = token.split(".");
  if (parti.length !== 3) return null;
  try {
    const payload = JSON.parse(atob(parti[1].replace(/-/g, "+").replace(/_/g, "/")));
    return typeof payload.exp === "number" ? payload.exp : null;
  } catch {
    return null;
  }
}

export const useAuthStore = defineStore("auth", () => {
  const accessToken = ref(null);
  const user = ref(null);
  const isInitialized = ref(false);
  const isAuthenticated = computed(() => Boolean(accessToken.value && user.value));
  const roleCode = computed(() => user.value?.role_code || null);
  const permissions = computed(() => user.value?.permissions || []);

  function accessTokenEFresco() {
    const exp = decodificaScadenzaJwt(accessToken.value);
    if (exp === null) return false;
    const adessoSec = Math.floor(Date.now() / 1000);
    return exp - adessoSec > SECONDI_BUFFER_FRESHEZZA;
  }

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
    accessTokenEFresco,
  };
});
