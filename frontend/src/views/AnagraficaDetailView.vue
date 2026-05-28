<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Tag from "primevue/tag";
import Tooltip from "primevue/tooltip";

import BaseCard from "@/components/ui/BaseCard.vue";
import {
  deleteAnagrafica,
  fetchAnagrafica,
  updateAnagrafica,
} from "@/services/anagrafiche";
import { useAuthStore } from "@/stores/auth";
import { confirm, notify } from "@/composables/useConfirm";
import { makeDialogPt, makePtSelect } from "@/lib/prime-pt";

const vTooltip = Tooltip;
const dialogPt = makeDialogPt("max-w-2xl");
const ptFormSelect = makePtSelect("w-full", "bg-white");

const props = defineProps({
  id: { type: String, required: true },
});

const router = useRouter();
const authStore = useAuthStore();
const puoScrivere = computed(() => authStore.hasPermission("anagrafiche.write"));
const puoEliminare = computed(() => authStore.hasPermission("anagrafiche.delete"));

// ── Caricamento ───────────────────────────────────────────────────────────

const anagrafica = ref(null);
const loading = ref(true);
const errore = ref(null);

async function carica() {
  loading.value = true;
  errore.value = null;
  try {
    anagrafica.value = await fetchAnagrafica(props.id);
  } catch {
    errore.value = "Anagrafica non trovata o non accessibile.";
  } finally {
    loading.value = false;
  }
}

onMounted(carica);

// ── Helpers display ───────────────────────────────────────────────────────

const TIPO_LABEL = {
  cliente: "Cliente",
  fornitore: "Fornitore",
  cliente_fornitore: "Cliente + Fornitore",
  agente: "Agente",
  altro: "Altro",
};

const REGIME_LABEL = {
  RF01: "RF01 — Ordinario",
  RF02: "RF02 — Contribuenti minimi",
  RF04: "RF04 — Agricoltura",
  RF18: "RF18 — IVA per cassa",
  RF19: "RF19 — Forfettario",
};

const TIPO_INDIRIZZO_LABEL = {
  legale: "Sede legale",
  operativo: "Sede operativa",
  spedizione: "Spedizione",
  fatturazione: "Fatturazione",
};

function ptTipoTag(tipo) {
  const palette = {
    cliente: "border-emerald-300 bg-emerald-50 text-emerald-800",
    fornitore: "border-blue-300 bg-blue-50 text-blue-800",
    cliente_fornitore: "border-violet-300 bg-violet-50 text-violet-800",
    agente: "border-amber-300 bg-amber-50 text-amber-800",
    altro: "border-steel-300 bg-steel-50 text-steel-600",
  };
  return {
    root: {
      class: `inline-flex items-center rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] ${palette[tipo] ?? palette.altro}`,
    },
  };
}

// ── Soft delete ───────────────────────────────────────────────────────────

async function disattiva() {
  const ok = await confirm({
    title: "Disattivare l'anagrafica",
    message: `Confermare la disattivazione di "${anagrafica.value?.display_name}"? Il record sarà nascosto dall'elenco ma non eliminato.`,
    confirmLabel: "Disattiva",
    danger: true,
  });
  if (!ok) return;
  try {
    await deleteAnagrafica(props.id);
    router.push({ name: "anagrafiche" });
  } catch {
    await notify({ message: "Errore durante la disattivazione. Riprovare." });
  }
}

// ── Modale modifica ───────────────────────────────────────────────────────

const mostraMod = ref(false);
const salvataggio = ref(false);
const erroreForm = ref(null);

const form = reactive({
  tipo: "",
  is_persona_fisica: false,
  ragione_sociale: "",
  cognome: "",
  nome: "",
  partita_iva: "",
  codice_fiscale: "",
  codice_sdi: "",
  pec: "",
  regime_fiscale: "RF01",
  natura_giuridica: "",
  email: "",
  telefono: "",
  website: "",
  note: "",
});

function apriModifica() {
  const a = anagrafica.value;
  Object.assign(form, {
    tipo: a.tipo,
    is_persona_fisica: a.is_persona_fisica,
    ragione_sociale: a.ragione_sociale ?? "",
    cognome: a.cognome ?? "",
    nome: a.nome ?? "",
    partita_iva: a.partita_iva ?? "",
    codice_fiscale: a.codice_fiscale ?? "",
    codice_sdi: a.codice_sdi ?? "",
    pec: a.pec ?? "",
    regime_fiscale: a.regime_fiscale ?? "RF01",
    natura_giuridica: a.natura_giuridica ?? "",
    email: a.email ?? "",
    telefono: a.telefono ?? "",
    website: a.website ?? "",
    note: a.note ?? "",
  });
  erroreForm.value = null;
  mostraMod.value = true;
}

async function salva() {
  erroreForm.value = null;
  if (form.is_persona_fisica && !form.cognome.trim()) {
    erroreForm.value = "Il cognome è obbligatorio per persona fisica.";
    return;
  }
  if (!form.is_persona_fisica && !form.ragione_sociale.trim()) {
    erroreForm.value = "La ragione sociale è obbligatoria.";
    return;
  }
  salvataggio.value = true;
  try {
    const payload = { ...form };
    Object.keys(payload).forEach((k) => { if (payload[k] === "") payload[k] = null; });
    await updateAnagrafica(props.id, payload);
    mostraMod.value = false;
    await carica();
  } catch (e) {
    erroreForm.value = e.response?.data?.detail ?? "Errore durante il salvataggio.";
  } finally {
    salvataggio.value = false;
  }
}

const opzioniTipoForm = [
  { label: "Cliente", value: "cliente" },
  { label: "Fornitore", value: "fornitore" },
  { label: "Cliente + Fornitore", value: "cliente_fornitore" },
  { label: "Agente", value: "agente" },
  { label: "Altro", value: "altro" },
];

const opzioniRegime = [
  { label: "RF01 — Ordinario", value: "RF01" },
  { label: "RF02 — Contribuenti minimi", value: "RF02" },
  { label: "RF04 — Agricoltura", value: "RF04" },
  { label: "RF18 — IVA per cassa", value: "RF18" },
  { label: "RF19 — Forfettario", value: "RF19" },
];
</script>

<template>
  <div class="space-y-6">

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-4">
      <div class="h-8 w-48 animate-pulse rounded-xl bg-steel-100" />
      <div class="h-48 animate-pulse rounded-2xl bg-steel-100" />
      <div class="h-32 animate-pulse rounded-2xl bg-steel-100" />
    </div>

    <!-- Errore -->
    <div v-else-if="errore" class="rounded-2xl border border-red-200 bg-red-50 px-6 py-8 text-center">
      <p class="text-sm font-medium text-red-700">{{ errore }}</p>
      <button
        class="mt-4 text-sm text-brand-600 underline"
        @click="router.push({ name: 'anagrafiche' })"
      >
        Torna all'elenco
      </button>
    </div>

    <template v-else-if="anagrafica">

      <!-- Breadcrumb + azioni header -->
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-2 text-sm">
          <button
            class="group flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-steel-500 transition-all hover:bg-steel-100 hover:text-steel-900 active:bg-steel-200"
            @click="router.push({ name: 'anagrafiche' })"
          >
            <svg
              class="h-4 w-4 transition-transform group-hover:-translate-x-0.5"
              viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
            >
              <polyline points="15 18 9 12 15 6"/>
            </svg>
            Anagrafiche
          </button>
          <span class="text-steel-300">/</span>
          <span class="font-medium text-steel-700">{{ anagrafica.display_name }}</span>
        </div>

        <div class="flex items-center gap-2">
          <span
            v-if="!anagrafica.is_active"
            class="rounded-full border border-steel-200 bg-steel-50 px-3 py-1 text-xs font-semibold uppercase tracking-widest text-steel-400"
          >
            Disattivato
          </span>
          <button
            v-if="puoScrivere"
            class="flex items-center gap-2 rounded-xl border border-steel-200 bg-white px-4 py-2 text-sm font-medium text-steel-700 transition hover:bg-steel-50"
            @click="apriModifica"
          >
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            Modifica
          </button>
          <button
            v-if="puoEliminare && anagrafica.is_active"
            v-tooltip.bottom="'Disattiva anagrafica'"
            class="flex items-center gap-2 rounded-xl border border-steel-200 bg-white px-4 py-2 text-sm font-medium text-steel-700 transition hover:border-red-200 hover:bg-red-50 hover:text-red-700"
            @click="disattiva"
          >
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/>
            </svg>
            Disattiva
          </button>
        </div>
      </div>

      <!-- Hero header scheda -->
      <BaseCard class="p-6">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:gap-6">
          <!-- Avatar iniziali -->
          <div class="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-brand-100 text-xl font-bold text-brand-700">
            {{ anagrafica.display_name.charAt(0).toUpperCase() }}
          </div>
          <!-- Info principale -->
          <div class="flex-1 space-y-2">
            <div class="flex flex-wrap items-center gap-3">
              <h2 class="text-xl font-semibold text-steel-900">{{ anagrafica.display_name }}</h2>
              <Tag :pt="ptTipoTag(anagrafica.tipo)" :value="TIPO_LABEL[anagrafica.tipo] ?? anagrafica.tipo" />
            </div>
            <div class="flex flex-wrap gap-4 text-sm text-steel-500">
              <span v-if="anagrafica.natura_giuridica" class="flex items-center gap-1">
                <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="18" height="18" rx="2"/>
                </svg>
                {{ anagrafica.natura_giuridica }}
              </span>
              <span v-if="anagrafica.partita_iva" class="flex items-center gap-1">
                <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                </svg>
                P.IVA {{ anagrafica.partita_iva }}
              </span>
              <span v-if="anagrafica.regime_fiscale" class="flex items-center gap-1">
                <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/>
                </svg>
                {{ REGIME_LABEL[anagrafica.regime_fiscale] ?? anagrafica.regime_fiscale }}
              </span>
            </div>
            <!-- Contatti rapidi -->
            <div class="flex flex-wrap gap-4 pt-1">
              <a
                v-if="anagrafica.email"
                :href="`mailto:${anagrafica.email}`"
                class="flex items-center gap-1.5 text-sm text-brand-600 hover:underline"
              >
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                  <polyline points="22,6 12,13 2,6"/>
                </svg>
                {{ anagrafica.email }}
              </a>
              <span
                v-if="anagrafica.telefono"
                class="flex items-center gap-1.5 text-sm text-steel-600"
              >
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.65 3.44a2 2 0 0 1 2-2.18h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 8.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                </svg>
                {{ anagrafica.telefono }}
              </span>
              <a
                v-if="anagrafica.website"
                :href="anagrafica.website.startsWith('http') ? anagrafica.website : `https://${anagrafica.website}`"
                target="_blank"
                rel="noopener"
                class="flex items-center gap-1.5 text-sm text-brand-600 hover:underline"
              >
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="2" y1="12" x2="22" y2="12"/>
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                </svg>
                {{ anagrafica.website }}
              </a>
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- Corpo: 2 colonne su desktop -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">

        <!-- Colonna sinistra: dati fiscali + fatturazione elettronica -->
        <div class="space-y-6 lg:col-span-2">

          <!-- Dati anagrafici -->
          <BaseCard class="p-6">
            <h3 class="mb-4 text-xs font-semibold uppercase tracking-widest text-steel-400">
              Dati anagrafici e fiscali
            </h3>
            <dl class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-2">
              <div v-if="!anagrafica.is_persona_fisica && anagrafica.ragione_sociale">
                <dt class="text-xs text-steel-600">Ragione sociale</dt>
                <dd class="mt-0.5 text-sm font-medium text-steel-900">{{ anagrafica.ragione_sociale }}</dd>
              </div>
              <div v-if="anagrafica.is_persona_fisica && (anagrafica.cognome || anagrafica.nome)">
                <dt class="text-xs text-steel-600">Nome e cognome</dt>
                <dd class="mt-0.5 text-sm font-medium text-steel-900">
                  {{ [anagrafica.cognome, anagrafica.nome].filter(Boolean).join(" ") }}
                </dd>
              </div>
              <div>
                <dt class="text-xs text-steel-600">Tipo soggetto</dt>
                <dd class="mt-0.5 text-sm text-steel-700">
                  {{ anagrafica.is_persona_fisica ? "Persona fisica" : "Persona giuridica" }}
                  <span v-if="anagrafica.natura_giuridica"> · {{ anagrafica.natura_giuridica }}</span>
                </dd>
              </div>
              <div v-if="anagrafica.partita_iva">
                <dt class="text-xs text-steel-600">Partita IVA</dt>
                <dd class="mt-0.5 font-mono text-sm text-steel-900">{{ anagrafica.partita_iva }}</dd>
              </div>
              <div v-if="anagrafica.codice_fiscale">
                <dt class="text-xs text-steel-600">Codice fiscale</dt>
                <dd class="mt-0.5 font-mono text-sm text-steel-900">{{ anagrafica.codice_fiscale }}</dd>
              </div>
              <div v-if="anagrafica.regime_fiscale">
                <dt class="text-xs text-steel-600">Regime fiscale</dt>
                <dd class="mt-0.5 text-sm text-steel-700">
                  {{ REGIME_LABEL[anagrafica.regime_fiscale] ?? anagrafica.regime_fiscale }}
                </dd>
              </div>
            </dl>
          </BaseCard>

          <!-- Fatturazione elettronica -->
          <BaseCard class="p-6">
            <h3 class="mb-4 text-xs font-semibold uppercase tracking-widest text-steel-400">
              Fatturazione elettronica (SDI)
            </h3>
            <dl class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-2">
              <div>
                <dt class="text-xs text-steel-600">Codice SDI</dt>
                <dd class="mt-0.5 font-mono text-sm text-steel-900">
                  {{ anagrafica.codice_sdi ?? "—" }}
                  <span
                    v-if="anagrafica.codice_sdi === '0000000'"
                    class="ml-2 rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-600"
                  >
                    Usa PEC
                  </span>
                </dd>
              </div>
              <div>
                <dt class="text-xs text-steel-600">PEC</dt>
                <dd class="mt-0.5 text-sm">
                  <a
                    v-if="anagrafica.pec"
                    :href="`mailto:${anagrafica.pec}`"
                    class="text-brand-600 hover:underline"
                  >
                    {{ anagrafica.pec }}
                  </a>
                  <span v-else class="text-steel-300">—</span>
                </dd>
              </div>
            </dl>
          </BaseCard>

          <!-- Indirizzi -->
          <BaseCard class="p-6">
            <h3 class="mb-4 text-xs font-semibold uppercase tracking-widest text-steel-400">
              Indirizzi ({{ anagrafica.indirizzi.length }})
            </h3>
            <div v-if="anagrafica.indirizzi.length" class="space-y-4">
              <div
                v-for="addr in anagrafica.indirizzi"
                :key="addr.id"
                class="flex items-start gap-4 rounded-xl border border-steel-100 p-4"
              >
                <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-steel-100 text-steel-500">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                    <circle cx="12" cy="10" r="3"/>
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-semibold uppercase tracking-widest text-steel-400">
                      {{ TIPO_INDIRIZZO_LABEL[addr.tipo] ?? addr.tipo }}
                    </span>
                    <span
                      v-if="addr.is_principale"
                      class="rounded-full bg-brand-50 px-2 py-0.5 text-[10px] font-semibold text-brand-600"
                    >
                      Principale
                    </span>
                  </div>
                  <p class="mt-1 text-sm text-steel-900">
                    {{ addr.indirizzo }}
                  </p>
                  <p class="text-sm text-steel-500">
                    {{ [addr.cap, addr.citta].filter(Boolean).join(" ") }}
                    <span v-if="addr.provincia"> ({{ addr.provincia }})</span>
                    <span v-if="addr.paese && addr.paese !== 'IT'"> · {{ addr.paese }}</span>
                  </p>
                </div>
              </div>
            </div>
            <p v-else class="text-sm text-steel-700">Nessun indirizzo registrato.</p>
          </BaseCard>

          <!-- Note -->
          <BaseCard v-if="anagrafica.note" class="p-6">
            <h3 class="mb-3 text-xs font-semibold uppercase tracking-widest text-steel-400">Note</h3>
            <p class="text-sm leading-relaxed text-steel-700">{{ anagrafica.note }}</p>
          </BaseCard>
        </div>

        <!-- Colonna destra: riepilogo + roadmap -->
        <div class="space-y-6">

          <!-- Riepilogo scheda -->
          <BaseCard class="p-6">
            <h3 class="mb-4 text-xs font-semibold uppercase tracking-widest text-steel-400">Riepilogo</h3>
            <dl class="space-y-3">
              <div class="flex justify-between text-sm">
                <dt class="text-steel-500">Stato</dt>
                <dd>
                  <span
                    :class="anagrafica.is_active
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      : 'bg-steel-50 text-steel-500 border-steel-200'"
                    class="rounded-full border px-2.5 py-0.5 text-xs font-semibold"
                  >
                    {{ anagrafica.is_active ? "Attivo" : "Disattivato" }}
                  </span>
                </dd>
              </div>
              <div class="flex justify-between text-sm">
                <dt class="text-steel-500">Creato il</dt>
                <dd class="text-steel-900">
                  {{ new Date(anagrafica.created_at).toLocaleDateString("it-IT") }}
                </dd>
              </div>
              <div class="flex justify-between text-sm">
                <dt class="text-steel-500">Aggiornato il</dt>
                <dd class="text-steel-900">
                  {{ new Date(anagrafica.updated_at).toLocaleDateString("it-IT") }}
                </dd>
              </div>
              <div class="flex justify-between text-sm">
                <dt class="text-steel-500">Indirizzi</dt>
                <dd class="text-steel-900">{{ anagrafica.indirizzi.length }}</dd>
              </div>
            </dl>
          </BaseCard>

          <!-- Prossime funzionalità (roadmap v2) -->
          <BaseCard class="p-6">
            <h3 class="mb-3 text-xs font-semibold uppercase tracking-widest text-steel-400">
              In arrivo (v2)
            </h3>
            <ul class="space-y-2 text-xs text-steel-400">
              <li class="flex items-center gap-2">
                <svg class="h-3.5 w-3.5 shrink-0 text-steel-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                Condizioni di pagamento (RIBA, bonifico, ecc.)
              </li>
              <li class="flex items-center gap-2">
                <svg class="h-3.5 w-3.5 shrink-0 text-steel-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                Banca e IBAN
              </li>
              <li class="flex items-center gap-2">
                <svg class="h-3.5 w-3.5 shrink-0 text-steel-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                Sconti e listini
              </li>
              <li class="flex items-center gap-2">
                <svg class="h-3.5 w-3.5 shrink-0 text-steel-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                Responsabile / agente assegnato
              </li>
              <li class="flex items-center gap-2">
                <svg class="h-3.5 w-3.5 shrink-0 text-steel-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                Storico documenti collegati
              </li>
              <li class="flex items-center gap-2">
                <svg class="h-3.5 w-3.5 shrink-0 text-steel-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                Gestione indirizzi da UI
              </li>
            </ul>
          </BaseCard>

        </div>
      </div>
    </template>

    <!-- Modale modifica -->
    <Dialog
      v-model:visible="mostraMod"
      header="Modifica anagrafica"
      :modal="true"
      :closable="true"
      :draggable="false"
      :pt="dialogPt"
    >
      <form class="space-y-5" @submit.prevent="salva">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Tipo *</label>
            <Select v-model="form.tipo" :options="opzioniTipoForm" option-label="label" option-value="value"
              :pt="ptFormSelect" />
          </div>
          <div class="flex items-end pb-1">
            <label class="flex cursor-pointer items-center gap-2 text-sm text-steel-700">
              <input v-model="form.is_persona_fisica" type="checkbox" class="h-4 w-4 rounded border-steel-300 text-brand-500" />
              Persona fisica
            </label>
          </div>
        </div>
        <div v-if="form.is_persona_fisica" class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Cognome *</label>
            <InputText v-model="form.cognome" placeholder="Ferrari" autocomplete="family-name" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Nome</label>
            <InputText v-model="form.nome" placeholder="Marco" autocomplete="given-name" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </div>
        </div>
        <div v-else>
          <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Ragione sociale *</label>
          <InputText v-model="form.ragione_sociale" placeholder="Edilceram S.r.l." autocomplete="organization" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Partita IVA</label>
            <InputText v-model="form.partita_iva" inputmode="numeric" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Codice fiscale</label>
            <InputText v-model="form.codice_fiscale" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </div>
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Codice SDI</label>
            <InputText v-model="form.codice_sdi" maxlength="7" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">PEC</label>
            <InputText v-model="form.pec" type="email" autocomplete="off" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </div>
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Regime fiscale</label>
            <Select v-model="form.regime_fiscale" :options="opzioniRegime" option-label="label" option-value="value"
              :pt="ptFormSelect" />
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Natura giuridica</label>
            <InputText v-model="form.natura_giuridica" placeholder="SRL / SPA" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </div>
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Email</label>
            <InputText v-model="form.email" type="email" autocomplete="email" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Telefono</label>
            <InputText v-model="form.telefono" type="tel" autocomplete="tel" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </div>
        </div>
        <div>
          <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Website</label>
          <InputText v-model="form.website" placeholder="www.azienda.it" type="url" autocomplete="url" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Note</label>
          <textarea v-model="form.note" rows="2"
            class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm text-steel-900 placeholder-steel-400 focus:outline-none focus:ring-2 focus:ring-brand-400" />
        </div>
        <p v-if="erroreForm" class="rounded-xl border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
          {{ erroreForm }}
        </p>
      </form>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button type="button" class="rounded-xl border border-steel-200 bg-white px-4 py-2 text-sm font-medium text-steel-700 hover:bg-steel-50" @click="mostraMod = false">
            Annulla
          </button>
          <button type="button" :disabled="salvataggio" class="rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-60" @click="salva">
            {{ salvataggio ? "Salvataggio…" : "Salva modifiche" }}
          </button>
        </div>
      </template>
    </Dialog>

  </div>
</template>
