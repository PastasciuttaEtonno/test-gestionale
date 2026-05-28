<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Tooltip from "primevue/tooltip";

import BaseCard from "@/components/ui/BaseCard.vue";
import {
  deleteArticolo,
  fetchArticolo,
  fetchCategorie,
  updateArticolo,
} from "@/services/articoli";
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
const puoScrivere = computed(() => authStore.hasPermission("articoli.write"));
const puoEliminare = computed(() => authStore.hasPermission("articoli.delete"));

// ── Caricamento ───────────────────────────────────────────────────────────

const articolo = ref(null);
const categorie = ref([]);
const loading = ref(true);
const errore = ref(null);

const fmtPrezzo = new Intl.NumberFormat("it-IT", {
  style: "currency",
  currency: "EUR",
  minimumFractionDigits: 2,
});

const nomeCategoria = computed(() => {
  const cid = articolo.value?.categoria_id;
  return cid ? (categorie.value.find((c) => c.id === cid)?.nome ?? null) : null;
});

const opzioniCategoria = computed(() =>
  categorie.value.map((c) => ({ label: c.nome, value: c.id })),
);
const opzioniUnita = [
  { label: "m²", value: "m²" },
  { label: "pz", value: "pz" },
  { label: "pallet", value: "pallet" },
  { label: "kg", value: "kg" },
  { label: "scatola", value: "scatola" },
  { label: "ml", value: "ml" },
  { label: "cf", value: "cf" },
];
const opzioniIva = [
  { label: "22%", value: 22 },
  { label: "10%", value: 10 },
  { label: "5%", value: 5 },
  { label: "4%", value: 4 },
  { label: "0% (esente)", value: 0 },
];

async function carica() {
  loading.value = true;
  errore.value = null;
  try {
    const [art, cat] = await Promise.all([fetchArticolo(props.id), fetchCategorie()]);
    articolo.value = art;
    categorie.value = cat.items;
  } catch {
    errore.value = "Articolo non trovato o non accessibile.";
  } finally {
    loading.value = false;
  }
}

onMounted(carica);

// ── Soft delete ───────────────────────────────────────────────────────────

async function disattiva() {
  const ok = await confirm({
    title: "Disattivare l'articolo",
    message: `Confermare la disattivazione di "${articolo.value?.codice}"? L'articolo sarà nascosto dall'elenco ma non eliminato.`,
    confirmLabel: "Disattiva",
    danger: true,
  });
  if (!ok) return;
  try {
    await deleteArticolo(props.id);
    router.push({ name: "articoli" });
  } catch (e) {
    if (!(e.response?.status === 403 && e.response?.data?.demo_readonly)) {
      await notify({ message: "Errore durante la disattivazione. Riprovare." });
    }
  }
}

// ── Modale modifica ───────────────────────────────────────────────────────

const mostraMod = ref(false);
const salvataggio = ref(false);
const erroreForm = ref(null);

const form = reactive({
  version: 1,
  codice: "",
  categoria_id: null,
  descrizione: "",
  unita_misura: "pz",
  prezzo_unitario: 0,
  aliquota_iva: 22,
  giacenza: 0,
  codice_ean: "",
  note: "",
});

function apriModifica() {
  const a = articolo.value;
  Object.assign(form, {
    version: a.version,
    codice: a.codice,
    categoria_id: a.categoria_id ?? null,
    descrizione: a.descrizione,
    unita_misura: a.unita_misura,
    prezzo_unitario: Number(a.prezzo_unitario),
    aliquota_iva: Number(a.aliquota_iva),
    giacenza: Number(a.giacenza),
    codice_ean: a.codice_ean ?? "",
    note: a.note ?? "",
  });
  erroreForm.value = null;
  mostraMod.value = true;
}

async function salva() {
  erroreForm.value = null;
  if (!form.codice.trim()) {
    erroreForm.value = "Il codice è obbligatorio.";
    return;
  }
  if (!form.descrizione.trim()) {
    erroreForm.value = "La descrizione è obbligatoria.";
    return;
  }
  salvataggio.value = true;
  try {
    await updateArticolo(props.id, {
      version: form.version,
      codice: form.codice,
      categoria_id: form.categoria_id,
      descrizione: form.descrizione,
      unita_misura: form.unita_misura,
      prezzo_unitario: form.prezzo_unitario,
      aliquota_iva: form.aliquota_iva,
      giacenza: form.giacenza,
      codice_ean: form.codice_ean || null,
      note: form.note || null,
    });
    mostraMod.value = false;
    await carica();
  } catch (e) {
    if (e.response?.status === 403 && e.response?.data?.demo_readonly) {
      mostraMod.value = false;
    } else {
      erroreForm.value = e.response?.data?.detail ?? "Errore durante il salvataggio.";
    }
  } finally {
    salvataggio.value = false;
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-4">
      <div class="h-8 w-48 animate-pulse rounded-xl bg-steel-100" />
      <div class="h-40 animate-pulse rounded-2xl bg-steel-100" />
      <div class="h-32 animate-pulse rounded-2xl bg-steel-100" />
    </div>

    <!-- Errore -->
    <div v-else-if="errore" class="rounded-2xl border border-red-200 bg-red-50 px-6 py-8 text-center">
      <p class="text-sm font-medium text-red-700">{{ errore }}</p>
      <button class="mt-4 text-sm text-brand-600 underline" @click="router.push({ name: 'articoli' })">
        Torna all'elenco
      </button>
    </div>

    <template v-else-if="articolo">
      <!-- Breadcrumb + azioni -->
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-2 text-sm">
          <button
            class="group flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-steel-500 transition-all hover:bg-steel-100 hover:text-steel-900 active:bg-steel-200"
            @click="router.push({ name: 'articoli' })"
          >
            <svg class="h-4 w-4 transition-transform group-hover:-translate-x-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            Articoli
          </button>
          <span class="text-steel-300">/</span>
          <span class="font-medium text-steel-700">{{ articolo.codice }}</span>
        </div>

        <div class="flex items-center gap-2">
          <span
            v-if="!articolo.is_active"
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
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
            Modifica
          </button>
          <button
            v-if="puoEliminare && articolo.is_active"
            v-tooltip.bottom="'Disattiva articolo'"
            class="flex items-center gap-2 rounded-xl border border-steel-200 bg-white px-4 py-2 text-sm font-medium text-steel-700 transition hover:border-red-200 hover:bg-red-50 hover:text-red-700"
            @click="disattiva"
          >
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" /><line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
            </svg>
            Disattiva
          </button>
        </div>
      </div>

      <!-- Hero -->
      <BaseCard class="p-6">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:gap-6">
          <div class="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-brand-100 text-brand-700">
            <svg class="h-7 w-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-14L4 7m8 4v10m0 0l-8-4V7" />
            </svg>
          </div>
          <div class="flex-1 space-y-2">
            <div class="flex flex-wrap items-center gap-3">
              <h2 class="text-xl font-semibold text-steel-900">{{ articolo.descrizione }}</h2>
              <span
                v-if="nomeCategoria"
                class="inline-flex items-center rounded-full border border-steel-200 bg-steel-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-steel-600"
              >
                {{ nomeCategoria }}
              </span>
            </div>
            <p class="font-mono text-sm text-steel-400">{{ articolo.codice }}</p>
            <div class="flex flex-wrap gap-6 pt-1">
              <div>
                <p class="text-xs text-steel-500">Prezzo unitario</p>
                <p class="text-lg font-semibold text-steel-900">{{ fmtPrezzo.format(Number(articolo.prezzo_unitario)) }}</p>
              </div>
              <div>
                <p class="text-xs text-steel-500">IVA</p>
                <p class="text-lg font-semibold text-steel-900">{{ Number(articolo.aliquota_iva) }}%</p>
              </div>
              <div>
                <p class="text-xs text-steel-500">Giacenza</p>
                <p class="text-lg font-semibold text-steel-900">
                  {{ Number(articolo.giacenza).toLocaleString("it-IT", { maximumFractionDigits: 3 }) }}
                  <span class="text-sm font-normal text-steel-500">{{ articolo.unita_misura }}</span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- Corpo: 2 colonne -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div class="space-y-6 lg:col-span-2">
          <BaseCard class="p-6">
            <h3 class="mb-4 text-xs font-semibold uppercase tracking-widest text-steel-400">Dati articolo</h3>
            <dl class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-2">
              <div>
                <dt class="text-xs text-steel-600">Codice</dt>
                <dd class="mt-0.5 font-mono text-sm text-steel-900">{{ articolo.codice }}</dd>
              </div>
              <div>
                <dt class="text-xs text-steel-600">Categoria</dt>
                <dd class="mt-0.5 text-sm text-steel-700">{{ nomeCategoria ?? "—" }}</dd>
              </div>
              <div>
                <dt class="text-xs text-steel-600">Unità di misura</dt>
                <dd class="mt-0.5 text-sm text-steel-700">{{ articolo.unita_misura }}</dd>
              </div>
              <div>
                <dt class="text-xs text-steel-600">Codice EAN</dt>
                <dd class="mt-0.5 font-mono text-sm text-steel-900">{{ articolo.codice_ean ?? "—" }}</dd>
              </div>
            </dl>
          </BaseCard>

          <BaseCard v-if="articolo.note" class="p-6">
            <h3 class="mb-3 text-xs font-semibold uppercase tracking-widest text-steel-400">Note</h3>
            <p class="text-sm leading-relaxed text-steel-700">{{ articolo.note }}</p>
          </BaseCard>
        </div>

        <div class="space-y-6">
          <BaseCard class="p-6">
            <h3 class="mb-4 text-xs font-semibold uppercase tracking-widest text-steel-400">Riepilogo</h3>
            <dl class="space-y-3">
              <div class="flex justify-between text-sm">
                <dt class="text-steel-500">Stato</dt>
                <dd>
                  <span
                    :class="articolo.is_active
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      : 'bg-steel-50 text-steel-500 border-steel-200'"
                    class="rounded-full border px-2.5 py-0.5 text-xs font-semibold"
                  >
                    {{ articolo.is_active ? "Attivo" : "Disattivato" }}
                  </span>
                </dd>
              </div>
              <div class="flex justify-between text-sm">
                <dt class="text-steel-500">Versione</dt>
                <dd class="text-steel-900">{{ articolo.version }}</dd>
              </div>
              <div class="flex justify-between text-sm">
                <dt class="text-steel-500">Creato il</dt>
                <dd class="text-steel-900">{{ new Date(articolo.created_at).toLocaleDateString("it-IT") }}</dd>
              </div>
              <div class="flex justify-between text-sm">
                <dt class="text-steel-500">Aggiornato il</dt>
                <dd class="text-steel-900">{{ new Date(articolo.updated_at).toLocaleDateString("it-IT") }}</dd>
              </div>
            </dl>
          </BaseCard>

          <BaseCard class="p-6">
            <h3 class="mb-3 text-xs font-semibold uppercase tracking-widest text-steel-400">In arrivo (v2)</h3>
            <ul class="space-y-2 text-xs text-steel-400">
              <li class="flex items-center gap-2">
                <svg class="h-3.5 w-3.5 shrink-0 text-steel-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="16" /><line x1="8" y1="12" x2="16" y2="12" /></svg>
                Listini multipli e sconti per cliente
              </li>
              <li class="flex items-center gap-2">
                <svg class="h-3.5 w-3.5 shrink-0 text-steel-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="16" /><line x1="8" y1="12" x2="16" y2="12" /></svg>
                Movimenti di magazzino con storico
              </li>
              <li class="flex items-center gap-2">
                <svg class="h-3.5 w-3.5 shrink-0 text-steel-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="16" /><line x1="8" y1="12" x2="16" y2="12" /></svg>
                Varianti (taglie, colori, lotti)
              </li>
              <li class="flex items-center gap-2">
                <svg class="h-3.5 w-3.5 shrink-0 text-steel-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="16" /><line x1="8" y1="12" x2="16" y2="12" /></svg>
                Uso nelle righe di bolle e fatture
              </li>
            </ul>
          </BaseCard>
        </div>
      </div>
    </template>

    <!-- Modale modifica -->
    <Dialog
      v-model:visible="mostraMod"
      header="Modifica articolo"
      :modal="true"
      :closable="true"
      :draggable="false"
      :pt="dialogPt"
    >
      <form class="space-y-5" @submit.prevent="salva">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Codice *</label>
            <InputText v-model="form.codice" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Categoria</label>
            <Select v-model="form.categoria_id" :options="opzioniCategoria" option-label="label" option-value="value" placeholder="Nessuna" show-clear :pt="ptFormSelect" />
          </div>
        </div>
        <div>
          <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Descrizione *</label>
          <InputText v-model="form.descrizione" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Prezzo unitario (€)</label>
            <input v-model.number="form.prezzo_unitario" type="number" min="0" step="0.0001" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm text-steel-900 focus:outline-none focus:ring-2 focus:ring-brand-400" />
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Aliquota IVA</label>
            <Select v-model="form.aliquota_iva" :options="opzioniIva" option-label="label" option-value="value" :pt="ptFormSelect" />
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Unità di misura</label>
            <Select v-model="form.unita_misura" :options="opzioniUnita" option-label="label" option-value="value" :pt="ptFormSelect" />
          </div>
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Giacenza</label>
            <input v-model.number="form.giacenza" type="number" min="0" step="0.001" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm text-steel-900 focus:outline-none focus:ring-2 focus:ring-brand-400" />
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Codice EAN</label>
            <InputText v-model="form.codice_ean" maxlength="14" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </div>
        </div>
        <div>
          <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-steel-500">Note</label>
          <textarea v-model="form.note" rows="2" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm text-steel-900 placeholder-steel-400 focus:outline-none focus:ring-2 focus:ring-brand-400" />
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
