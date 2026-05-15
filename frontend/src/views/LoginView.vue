<script setup>
import axios from "axios";
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import BaseButton from "../components/ui/BaseButton.vue";
import BaseCard from "../components/ui/BaseCard.vue";
import SectionLabel from "../components/ui/SectionLabel.vue";
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
      errore.value = "Si e verificato un errore inatteso durante il login.";
    }
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="flex min-h-[calc(100vh-5rem)] items-center justify-center">
    <div class="grid w-full max-w-5xl gap-10 lg:grid-cols-[1.15fr_0.85fr]">
      <section class="hidden rounded-[2rem] border border-brand-900/10 bg-[linear-gradient(180deg,_#2b3138_0%,_#1e252c_58%,_#5e1313_100%)] p-10 text-white shadow-panel lg:block">
        <p class="text-xs font-semibold uppercase tracking-[0.3em] text-brand-100">
          Accesso operativo
        </p>
        <h1 class="mt-4 text-4xl font-semibold leading-tight">
          Verifica sicura del flusso JWT del gestionale.
        </h1>
        <p class="mt-6 max-w-xl text-base text-white/84">
          La vista usa una palette grigio tecnico e rosso operativo per distinguere
          contesto, azione e stato. Il focus resta sulla leggibilita d'uso quotidiana.
        </p>
      </section>

      <BaseCard class="mx-auto w-full max-w-xl" :highlight="true">
        <SectionLabel>Accesso</SectionLabel>
        <h2 class="mt-3 text-3xl font-semibold text-steel-900">
          Login al backend Esseduesoft
        </h2>
        <p class="mt-3 text-sm leading-6 text-steel-700">
          Il client mantiene l'access token solo in memoria e usa un cookie
          `HttpOnly` per il refresh della sessione autenticata.
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

          <label class="block">
            <span class="mb-2 block text-sm font-medium text-steel-700">Password</span>
            <input
              v-model="form.password"
              class="campo-input"
              type="password"
              autocomplete="current-password"
              placeholder="Inserire la password"
            />
          </label>

          <p
            v-if="errore"
            class="rounded-2xl border border-brand-100 bg-brand-50 px-4 py-3 text-sm text-brand-700"
          >
            {{ errore }}
          </p>

          <BaseButton type="submit" :disabled="loading" :block="true">
            {{ loading ? "Accesso in corso..." : "Accedi" }}
          </BaseButton>
        </form>
      </BaseCard>
    </div>
  </div>
</template>
