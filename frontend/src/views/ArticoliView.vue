<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Tooltip from "primevue/tooltip";

import BaseCard from "@/components/ui/BaseCard.vue";
import CampoForm from "@/components/ui/CampoForm.vue";
import SectionLabel from "@/components/ui/SectionLabel.vue";
import {
  createArticolo,
  createCategoria,
  deleteArticolo,
  deleteCategoria,
  fetchArticoli,
  fetchCategorie,
  updateArticolo,
} from "@/services/articoli";
import { useAuthStore } from "@/stores/auth";
import { confirm, notify } from "@/composables/useConfirm";
import {
  ptIconField,
  ptInputIcon,
  makePtInputText,
  makePtSelect,
  makeDialogPt,
} from "@/lib/prime-pt";

const vTooltip = Tooltip;

const router = useRouter();
const authStore = useAuthStore();
const puoScrivere = computed(() => authStore.hasPermission("articoli.write"));
const puoEliminare = computed(() => authStore.hasPermission("articoli.delete"));

// ── Stato lista ───────────────────────────────────────────────────────────

const items = ref([]);
const total = ref(0);
const loading = ref(false);
const errore = ref(null);

const categorie = ref([]);
const filtroQ = ref("");
const filtroCategoria = ref(null);
const filtroAttivi = ref(true);
const skip = ref(0);
const limit = 20;

const ptInputText = makePtInputText();
const ptSelect = makePtSelect("w-full sm:w-52");
const ptFormSelect = makePtSelect("w-full", "bg-white");
const dialogPt = makeDialogPt("max-w-2xl");
const dialogCategoriePt = makeDialogPt("max-w-lg");

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

async function caricaCategorie() {
  try {
    const res = await fetchCategorie();
    categorie.value = res.items;
  } catch {
    categorie.value = [];
  }
}

function nomeCategoria(id) {
  return categorie.value.find((c) => c.id === id)?.nome ?? null;
}

async function caricaArticoli() {
  loading.value = true;
  errore.value = null;
  try {
    const params = { is_active: filtroAttivi.value, skip: skip.value, limit };
    if (filtroCategoria.value) params.categoria_id = filtroCategoria.value;
    if (filtroQ.value.trim()) params.q = filtroQ.value.trim();
    const res = await fetchArticoli(params);
    items.value = res.items;
    total.value = res.total;
  } catch {
    errore.value = "Errore nel caricamento degli articoli.";
  } finally {
    loading.value = false;
  }
}

watch([filtroQ, filtroCategoria, filtroAttivi], () => {
  skip.value = 0;
  caricaArticoli();
});

caricaCategorie();
caricaArticoli();

// ── Formattazione ───────────────────────────────────────────────────────────

const fmtPrezzo = new Intl.NumberFormat("it-IT", {
  style: "currency",
  currency: "EUR",
  minimumFractionDigits: 2,
});

function formattaPrezzo(value) {
  return fmtPrezzo.format(Number(value ?? 0));
}

function formattaGiacenza(value, unita) {
  const n = Number(value ?? 0);
  return `${n.toLocaleString("it-IT", { maximumFractionDigits: 3 })} ${unita}`;
}

// ── Modale create / edit articolo ─────────────────────────────────────────

const mostraMod = ref(false);
const modTitolo = computed(() => (form.id ? "Modifica articolo" : "Nuovo articolo"));
const salvataggio = ref(false);
const erroreForm = ref(null);

const formVuoto = () => ({
  id: null,
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

const form = reactive(formVuoto());

function apriCrea() {
  Object.assign(form, formVuoto());
  erroreForm.value = null;
  mostraMod.value = true;
}

function apriModifica(a) {
  Object.assign(form, {
    id: a.id,
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
    if (form.id) {
      await updateArticolo(form.id, {
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
    } else {
      await createArticolo({
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
    }
    mostraMod.value = false;
    await caricaArticoli();
  } catch (e) {
    // In modalità demo il 403 viene gestito globalmente con un toast: chiudiamo il form.
    if (e.response?.status === 403 && e.response?.data?.demo_readonly) {
      mostraMod.value = false;
    } else {
      erroreForm.value = e.response?.data?.detail ?? "Errore durante il salvataggio.";
    }
  } finally {
    salvataggio.value = false;
  }
}

// ── Filtri helpers ────────────────────────────────────────────────────────

const filtriApplicati = computed(
  () => filtroQ.value.trim() !== "" || filtroCategoria.value !== null || !filtroAttivi.value,
);

function azzeraFiltri() {
  filtroQ.value = "";
  filtroCategoria.value = null;
  filtroAttivi.value = true;
}

// ── Soft delete articolo ───────────────────────────────────────────────────

async function disattiva(a) {
  const ok = await confirm({
    title: "Disattivare l'articolo",
    message: `Confermare la disattivazione di "${a.codice}"? L'articolo sarà nascosto dall'elenco ma non eliminato.`,
    confirmLabel: "Disattiva",
    danger: true,
  });
  if (!ok) return;
  try {
    await deleteArticolo(a.id);
    await caricaArticoli();
  } catch (e) {
    if (!(e.response?.status === 403 && e.response?.data?.demo_readonly)) {
      await notify({ message: "Errore durante la disattivazione. Riprovare." });
    }
  }
}

// ── Gestione categorie ──────────────────────────────────────────────────────

const mostraCategorie = ref(false);
const nuovaCategoria = ref("");
const salvataggioCat = ref(false);
const erroreCat = ref(null);

function apriCategorie() {
  erroreCat.value = null;
  nuovaCategoria.value = "";
  mostraCategorie.value = true;
}

async function creaCategoria() {
  erroreCat.value = null;
  if (!nuovaCategoria.value.trim()) {
    erroreCat.value = "Il nome della categoria è obbligatorio.";
    return;
  }
  salvataggioCat.value = true;
  try {
    await createCategoria({ nome: nuovaCategoria.value.trim() });
    nuovaCategoria.value = "";
    await caricaCategorie();
  } catch (e) {
    if (e.response?.status === 403 && e.response?.data?.demo_readonly) {
      mostraCategorie.value = false;
    } else {
      erroreCat.value = e.response?.data?.detail ?? "Errore durante la creazione.";
    }
  } finally {
    salvataggioCat.value = false;
  }
}

async function disattivaCategoria(c) {
  const ok = await confirm({
    title: "Disattivare la categoria",
    message: `Confermare la disattivazione di "${c.nome}"? Non sarà più selezionabile per nuovi articoli.`,
    confirmLabel: "Disattiva",
    danger: true,
  });
  if (!ok) return;
  try {
    await deleteCategoria(c.id);
    await caricaCategorie();
  } catch (e) {
    if (!(e.response?.status === 403 && e.response?.data?.demo_readonly)) {
      await notify({ message: e.response?.data?.detail ?? "Errore durante la disattivazione." });
    }
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Intestazione pagina -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <SectionLabel label="Articoli" />
      <div class="flex items-center gap-2">
        <button
          v-if="puoScrivere"
          type="button"
          class="flex shrink-0 items-center gap-2 rounded-xl border border-steel-200 bg-white px-4 py-2 text-sm font-medium text-steel-700 transition hover:bg-steel-50"
          @click="apriCategorie"
        >
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 7h18M3 12h18M3 17h18" />
          </svg>
          Categorie
        </button>
        <Button
          v-if="puoScrivere"
          label="Nuovo articolo"
          icon="pi pi-plus"
          size="small"
          class="shrink-0 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600"
          @click="apriCrea"
        />
      </div>
    </div>

    <!-- Filtri -->
    <BaseCard class="p-4">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
        <IconField :pt="ptIconField" class="flex-1 sm:max-w-sm">
          <InputIcon :pt="ptInputIcon">
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          </InputIcon>
          <InputText v-model="filtroQ" placeholder="Cerca per codice o descrizione…" aria-label="Cerca articolo per codice o descrizione" :pt="ptInputText" />
        </IconField>

        <Select
          v-model="filtroCategoria"
          :options="opzioniCategoria"
          option-label="label"
          option-value="value"
          placeholder="Tutte le categorie"
          aria-label="Filtra per categoria"
          show-clear
          :pt="ptSelect"
        />

        <button type="button" class="flex shrink-0 items-center gap-2.5" @click="filtroAttivi = !filtroAttivi">
          <span
            class="relative inline-flex h-5 w-9 shrink-0 rounded-full border-2 border-transparent transition-colors duration-200"
            :class="filtroAttivi ? 'bg-steel-700' : 'bg-steel-200'"
          >
            <span
              class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition-transform duration-200"
              :class="filtroAttivi ? 'translate-x-4' : 'translate-x-0'"
            />
          </span>
          <span class="text-sm transition-colors" :class="filtroAttivi ? 'font-medium text-steel-900' : 'text-steel-500'">
            Solo attivi
          </span>
        </button>

        <div class="flex items-center gap-3 sm:ml-auto">
          <span class="text-xs text-steel-700">
            <span class="font-semibold text-steel-900">{{ total }}</span> risultati
          </span>
          <button
            v-if="filtriApplicati"
            type="button"
            class="flex items-center gap-1 rounded-lg border border-steel-200 bg-white px-2.5 py-1 text-xs font-medium text-steel-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
            @click="azzeraFiltri"
          >
            <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
            Azzera
          </button>
        </div>
      </div>
    </BaseCard>

    <!-- Errore -->
    <p v-if="errore" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ errore }}
    </p>

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-3">
      <div v-for="n in 5" :key="n" class="h-14 animate-pulse rounded-xl bg-steel-100" />
    </div>

    <!-- Tabella -->
    <BaseCard v-else-if="items.length">
      <div class="overflow-hidden rounded-2xl border border-steel-200">
        <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <caption class="sr-only">Elenco articoli: codice e descrizione, categoria, prezzo, IVA, giacenza e azioni.</caption>
          <thead class="border-b border-steel-100 bg-steel-50">
            <tr>
              <th scope="col" class="px-4 py-3 text-left intestazione-tabella">Articolo</th>
              <th scope="col" class="hidden px-4 py-3 text-left intestazione-tabella sm:table-cell">Categoria</th>
              <th scope="col" class="px-4 py-3 text-right intestazione-tabella">Prezzo</th>
              <th scope="col" class="hidden px-4 py-3 text-right intestazione-tabella md:table-cell">IVA</th>
              <th scope="col" class="hidden px-4 py-3 text-right intestazione-tabella lg:table-cell">Giacenza</th>
              <th scope="col" class="px-4 py-3 text-right intestazione-tabella">Azioni</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-steel-100">
            <tr
              v-for="a in items"
              :key="a.id"
              class="cursor-pointer transition-colors hover:bg-steel-50"
              @click="router.push({ name: 'articolo-detail', params: { id: a.id } })"
            >
              <td class="px-4 py-3">
                <p class="font-mono text-xs text-steel-600">{{ a.codice }}</p>
                <p class="mt-0.5 font-medium text-steel-900">
                  <RouterLink
                    :to="{ name: 'articolo-detail', params: { id: a.id } }"
                    class="link-riga"
                    @click.stop
                  >{{ a.descrizione }}</RouterLink>
                </p>
              </td>
              <td class="hidden px-4 py-3 sm:table-cell">
                <span
                  v-if="nomeCategoria(a.categoria_id)"
                  class="inline-flex items-center rounded-full border border-steel-200 bg-steel-50 px-2.5 py-0.5 text-[11px] font-semibold text-steel-600"
                >
                  {{ nomeCategoria(a.categoria_id) }}
                </span>
                <span v-else class="text-steel-300">—</span>
              </td>
              <td class="px-4 py-3 text-right cifre font-medium text-steel-900">{{ formattaPrezzo(a.prezzo_unitario) }}</td>
              <td class="hidden px-4 py-3 text-right cifre text-steel-600 md:table-cell">{{ Number(a.aliquota_iva) }}%</td>
              <td class="hidden px-4 py-3 text-right cifre text-steel-600 lg:table-cell">{{ formattaGiacenza(a.giacenza, a.unita_misura) }}</td>
              <td class="px-4 py-3 text-right cifre">
                <div class="flex items-center justify-end gap-2">
                  <button
                    v-if="puoScrivere"
                    v-tooltip.left="'Modifica'"
                    aria-label="Modifica"
                    type="button"
                    class="flex h-8 w-8 items-center justify-center rounded-lg border border-steel-200 bg-white text-steel-500 transition hover:bg-steel-50 hover:text-brand-600"
                    @click.stop="apriModifica(a)"
                  >
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                    </svg>
                  </button>
                  <button
                    v-if="puoEliminare"
                    v-tooltip.left="'Disattiva'"
                    aria-label="Disattiva"
                    type="button"
                    class="flex h-8 w-8 items-center justify-center rounded-lg border border-steel-200 bg-white text-steel-500 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
                    @click.stop="disattiva(a)"
                  >
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10" />
                      <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
    </BaseCard>

    <!-- Empty state -->
    <BaseCard v-else class="py-16 text-center">
      <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-steel-100 text-steel-400">
        <svg class="h-7 w-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-14L4 7m8 4v10m0 0l-8-4V7" />
        </svg>
      </div>
      <p class="text-sm font-medium text-steel-700">Nessun articolo trovato</p>
      <p class="mt-1 text-xs text-steel-700">
        {{ filtriApplicati ? "Prova a modificare i filtri di ricerca." : "Crea il primo articolo per iniziare." }}
      </p>
      <button
        v-if="puoScrivere && !filtriApplicati"
        class="mt-4 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600"
        @click="apriCrea"
      >
        Crea articolo
      </button>
    </BaseCard>

    <!-- Modale create / edit articolo -->
    <Dialog
      v-model:visible="mostraMod"
      :header="modTitolo"
      :modal="true"
      :closable="true"
      :draggable="false"
      :pt="dialogPt"
    >
      <form class="space-y-5" @submit.prevent="salva">
        <p class="text-xs text-steel-600">I campi contrassegnati con * sono obbligatori.</p>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CampoForm v-slot="{ campo }" label="Codice" obbligatorio>
            <InputText v-model="form.codice" v-bind="campo" placeholder="PAV-GRES-6060-GR" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </CampoForm>
          <CampoForm v-slot="{ combo }" label="Categoria">
            <Select v-bind="combo"
              v-model="form.categoria_id"
              
              :options="opzioniCategoria"
              option-label="label"
              option-value="value"
              placeholder="Nessuna"
              show-clear
              :pt="ptFormSelect"
            />
          </CampoForm>
        </div>

        <CampoForm v-slot="{ campo }" label="Descrizione" obbligatorio>
          <InputText v-model="form.descrizione" v-bind="campo" placeholder="Gres porcellanato 60x60 grigio" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
        </CampoForm>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <CampoForm v-slot="{ campo }" label="Prezzo unitario (€)">
            <input
              v-model.number="form.prezzo_unitario"
              v-bind="campo"
              type="number"
              min="0"
              step="0.0001"
              class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm text-steel-900 focus:outline-none focus:ring-2 focus:ring-brand-400"
            />
          </CampoForm>
          <CampoForm v-slot="{ combo }" label="Aliquota IVA">
            <Select v-bind="combo" v-model="form.aliquota_iva"  :options="opzioniIva" option-label="label" option-value="value" :pt="ptFormSelect" />
          </CampoForm>
          <CampoForm v-slot="{ combo }" label="Unità di misura">
            <Select v-bind="combo" v-model="form.unita_misura"  :options="opzioniUnita" option-label="label" option-value="value" :pt="ptFormSelect" />
          </CampoForm>
        </div>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CampoForm v-slot="{ campo }" label="Giacenza">
            <input
              v-model.number="form.giacenza"
              v-bind="campo"
              type="number"
              min="0"
              step="0.001"
              class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm text-steel-900 focus:outline-none focus:ring-2 focus:ring-brand-400"
            />
          </CampoForm>
          <CampoForm v-slot="{ campo }" label="Codice EAN" aiuto="13 o 14 cifre.">
            <InputText v-model="form.codice_ean" v-bind="campo" placeholder="8001234500011" maxlength="14" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </CampoForm>
        </div>

        <CampoForm v-slot="{ campo }" label="Note">
          <textarea
            v-model="form.note"
            v-bind="campo"
            rows="2"
            placeholder="Annotazioni libere…"
            class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm text-steel-900 placeholder-steel-400 focus:outline-none focus:ring-2 focus:ring-brand-400"
          />
        </CampoForm>

        <p v-if="erroreForm" role="alert" class="rounded-xl border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
          {{ erroreForm }}
        </p>
      </form>

      <template #footer>
        <div class="flex justify-end gap-3">
          <button type="button" class="rounded-xl border border-steel-200 bg-white px-4 py-2 text-sm font-medium text-steel-700 hover:bg-steel-50" @click="mostraMod = false">
            Annulla
          </button>
          <button
            type="button"
            :disabled="salvataggio"
            class="rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-60"
            @click="salva"
          >
            {{ salvataggio ? "Salvataggio…" : form.id ? "Salva modifiche" : "Crea articolo" }}
          </button>
        </div>
      </template>
    </Dialog>

    <!-- Modale gestione categorie -->
    <Dialog
      v-model:visible="mostraCategorie"
      header="Categorie articolo"
      :modal="true"
      :closable="true"
      :draggable="false"
      :pt="dialogCategoriePt"
    >
      <div class="space-y-4">
        <div class="flex items-end gap-2">
          <CampoForm v-slot="{ campo }" label="Nuova categoria">
            <InputText v-bind="campo" v-model="nuovaCategoria" placeholder="Es. Pavimenti" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" @keyup.enter="creaCategoria" />
          </CampoForm>
          <button
            type="button"
            :disabled="salvataggioCat"
            class="rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-60"
            @click="creaCategoria"
          >
            Aggiungi
          </button>
        </div>

        <p v-if="erroreCat" class="rounded-xl border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
          {{ erroreCat }}
        </p>

        <div v-if="categorie.length" class="divide-y divide-steel-100 rounded-xl border border-steel-100">
          <div v-for="c in categorie" :key="c.id" class="flex items-center justify-between px-4 py-2.5">
            <span class="text-sm text-steel-800">{{ c.nome }}</span>
            <button
              v-if="puoEliminare"
              v-tooltip.left="'Disattiva categoria'"
              aria-label="Disattiva categoria"
              type="button"
              class="flex h-7 w-7 items-center justify-center rounded-lg border border-steel-200 bg-white text-steel-400 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
              @click="disattivaCategoria(c)"
            >
              <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
              </svg>
            </button>
          </div>
        </div>
        <p v-else class="text-sm text-steel-500">Nessuna categoria. Aggiungine una per classificare gli articoli.</p>
      </div>
    </Dialog>
  </div>
</template>
