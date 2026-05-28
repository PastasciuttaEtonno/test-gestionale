<script setup>
import axios from "axios";
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import BaseButton from "../components/ui/BaseButton.vue";
import BaseCard from "../components/ui/BaseCard.vue";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const form = reactive({
  identifier: "",
  password: "",
});

const errore = ref("");
const loading = ref(false);
const mostraPassword = ref(false);

async function onSubmit() {
  errore.value = "";
  loading.value = true;

  try {
    await authStore.login({
      identifier: form.identifier,
      password: form.password,
    });

    const redirectDestinazione =
      typeof route.query.redirect === "string" ? route.query.redirect : "/dashboard";

    router.push(redirectDestinazione);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errore.value =
        error.response?.data?.detail ||
        "Autenticazione non riuscita. Verificare le credenziali.";
    } else {
      errore.value = "Si è verificato un errore inatteso durante il login.";
    }
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="flex min-h-[calc(100vh-4rem)] items-center justify-center">
    <div class="grid w-full max-w-5xl gap-10 lg:grid-cols-[1.15fr_0.85fr]">

      <section class="hidden flex-col justify-between rounded-[2rem] border border-brand-900/10 bg-[linear-gradient(180deg,_#2b3138_0%,_#1e252c_58%,_#5e1313_100%)] p-10 text-white shadow-panel lg:flex">
        <div>
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-500 text-sm font-semibold uppercase tracking-[0.2em] text-white">
              ES
            </div>
            <span class="text-xs font-semibold uppercase tracking-[0.28em] text-brand-300">
              Gestionale
            </span>
          </div>

          <h1 class="mt-10 text-4xl font-semibold leading-tight">
            Il gestionale per la tua operatività quotidiana.
          </h1>
          <p class="mt-4 text-base leading-relaxed text-white/70">
            Piattaforma integrata per la gestione documentale, anagrafica e logistica aziendale.
          </p>

          <ul class="mt-8 space-y-3">
            <li class="flex items-center gap-3 text-sm text-white/80">
              <span class="h-1.5 w-1.5 shrink-0 rounded-full bg-brand-300"></span>
              Gestione ordini, bolle e fatture
            </li>
            <li class="flex items-center gap-3 text-sm text-white/80">
              <span class="h-1.5 w-1.5 shrink-0 rounded-full bg-brand-300"></span>
              Anagrafica clienti e fornitori
            </li>
            <li class="flex items-center gap-3 text-sm text-white/80">
              <span class="h-1.5 w-1.5 shrink-0 rounded-full bg-brand-300"></span>
              Controllo magazzino e spedizioni
            </li>
          </ul>
        </div>

        <p class="text-xs text-white/40">
          © 2026 Gestionale S.r.l. — Tutti i diritti riservati
        </p>
      </section>

      <BaseCard class="mx-auto w-full max-w-xl" :highlight="true">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-500 text-sm font-semibold uppercase tracking-[0.2em] text-white">
            ES
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-brand-700">Gestionale</p>
            <p class="text-xs text-steel-700">Gestionale aziendale</p>
          </div>
        </div>

        <h2 class="mt-8 text-2xl font-semibold text-steel-900">
          Accedi al tuo account
        </h2>
        <p class="mt-1.5 text-sm text-steel-700">
          Inserire le credenziali aziendali per continuare.
        </p>

        <form class="mt-8 space-y-5" @submit.prevent="onSubmit">
          <label class="block">
            <span class="mb-2 block text-sm font-medium text-steel-700">Username</span>
            <input
              v-model="form.identifier"
              class="campo-input"
              type="text"
              autocomplete="username"
              placeholder="Inserire lo username"
            />
          </label>

          <div class="block">
            <label
              for="password"
              class="mb-1.5 block text-sm font-medium text-steel-700"
            >
              Password
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="form.password"
                :type="mostraPassword ? 'text' : 'password'"
                class="campo-input pr-12"
                autocomplete="current-password"
                placeholder="Inserire la password"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center text-steel-400 transition hover:text-steel-700 focus:outline-none"
                @click="mostraPassword = !mostraPassword"
              >
                <svg v-if="!mostraPassword" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
          </div>

          <p
            v-if="errore"
            class="rounded-xl border border-brand-100 bg-brand-50 px-4 py-3 text-sm text-brand-700"
          >
            {{ errore }}
          </p>

          <BaseButton type="submit" :disabled="loading" :block="true">
            {{ loading ? "Accesso in corso..." : "Accedi" }}
          </BaseButton>
        </form>

        <p class="mt-6 text-center text-xs text-steel-700">
          Per assistenza contattare il proprio amministratore di sistema.
        </p>
      </BaseCard>

    </div>
  </div>
</template>
