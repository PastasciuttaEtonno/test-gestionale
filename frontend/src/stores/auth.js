import { reactive } from "vue";

import {
  aggiornaToken,
  eseguiLogin,
  eseguiLogout,
} from "../services/auth";

const stato = reactive({
  accessToken: null,
  user: null,
  isInitialized: false,
});

async function initialize() {
  if (stato.isInitialized) {
    return;
  }
  try {
    await refreshSessione();
  } catch {
    await clearSessioneLocale();
  }

  stato.isInitialized = true;
}

async function login(payload) {
  const sessione = await eseguiLogin(payload);
  applicaSessione(sessione);
}

function applicaSessione(sessione) {
  stato.accessToken = sessione.access_token;
  stato.user = sessione.user;
}

async function refreshSessione() {
  const sessione = await aggiornaToken();
  applicaSessione(sessione);
}

async function logout() {
  try {
    if (stato.accessToken) {
      await eseguiLogout();
    }
  } finally {
    await clearSessioneLocale();
  }
}

async function clearSessioneLocale() {
  stato.accessToken = null;
  stato.user = null;
}

export function useAuthStore() {
  return {
    get accessToken() {
      return stato.accessToken;
    },
    get user() {
      return stato.user;
    },
    get isInitialized() {
      return stato.isInitialized;
    },
    get isAuthenticated() {
      return Boolean(stato.accessToken && stato.user);
    },
    initialize,
    login,
    logout,
    refreshSessione,
    clearSessioneLocale,
  };
}
