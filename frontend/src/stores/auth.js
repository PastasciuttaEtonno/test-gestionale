import { reactive } from "vue";

import {
  aggiornaToken,
  eseguiLogin,
  eseguiLogout,
  recuperaUtenteCorrente,
} from "../services/auth";

const STORAGE_KEY = "esseduesoft.auth.sessione";

const stato = reactive({
  accessToken: null,
  refreshToken: null,
  user: null,
  isInitialized: false,
});

function salvaSessioneSuStorage() {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      accessToken: stato.accessToken,
      refreshToken: stato.refreshToken,
      user: stato.user,
    }),
  );
}

function caricaSessioneDaStorage() {
  const raw = localStorage.getItem(STORAGE_KEY);

  if (!raw) {
    return;
  }

  try {
    const sessione = JSON.parse(raw);
    stato.accessToken = sessione.accessToken ?? null;
    stato.refreshToken = sessione.refreshToken ?? null;
    stato.user = sessione.user ?? null;
  } catch {
    localStorage.removeItem(STORAGE_KEY);
  }
}

async function initialize() {
  if (stato.isInitialized) {
    return;
  }

  caricaSessioneDaStorage();

  if (stato.accessToken) {
    try {
      stato.user = await recuperaUtenteCorrente();
      salvaSessioneSuStorage();
    } catch {
      await clearSessioneLocale();
    }
  }

  stato.isInitialized = true;
}

async function login(payload) {
  const sessione = await eseguiLogin(payload);
  applicaSessione(sessione);
}

function applicaSessione(sessione) {
  stato.accessToken = sessione.access_token;
  stato.refreshToken = sessione.refresh_token;
  stato.user = sessione.user;
  salvaSessioneSuStorage();
}

async function refreshSessione() {
  if (!stato.refreshToken) {
    throw new Error("Refresh token assente.");
  }

  const sessione = await aggiornaToken(stato.refreshToken);
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
  stato.refreshToken = null;
  stato.user = null;
  localStorage.removeItem(STORAGE_KEY);
}

export function useAuthStore() {
  return {
    get accessToken() {
      return stato.accessToken;
    },
    get refreshToken() {
      return stato.refreshToken;
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
