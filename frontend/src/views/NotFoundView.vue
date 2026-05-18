<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";

import BaseButton from "../components/ui/BaseButton.vue";
import BaseCard from "../components/ui/BaseCard.vue";
import SectionLabel from "../components/ui/SectionLabel.vue";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const destinazionePrincipale = computed(() =>
  authStore.isAuthenticated ? { name: "dashboard" } : { name: "login" },
);

const etichettaAzione = computed(() =>
  authStore.isAuthenticated ? "Torna alla dashboard" : "Vai al login",
);

function vaiAllaDestinazionePrincipale() {
  router.push(destinazionePrincipale.value);
}
</script>

<template>
  <div class="flex min-h-[calc(100vh-5rem)] items-center justify-center">
    <BaseCard class="w-full max-w-3xl" :highlight="true">
      <SectionLabel>Errore di navigazione</SectionLabel>
      <div class="mt-4 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="max-w-2xl">
          <p class="text-[11px] font-semibold uppercase tracking-[0.28em] text-brand-700">
            HTTP 404
          </p>
          <h1 class="mt-3 text-4xl font-semibold text-steel-900">
            Pagina non trovata
          </h1>
          <p class="mt-4 text-sm leading-7 text-steel-700">
            L'indirizzo richiesto non corrisponde a nessuna vista del frontend.
            Verificare l'URL oppure tornare a una sezione valida del gestionale.
          </p>
        </div>

        <div class="flex flex-wrap gap-3">
          <BaseButton type="button" variant="secondary" @click="router.back()">
            Torna indietro
          </BaseButton>
          <BaseButton type="button" @click="vaiAllaDestinazionePrincipale">
            {{ etichettaAzione }}
          </BaseButton>
        </div>
      </div>
    </BaseCard>
  </div>
</template>
