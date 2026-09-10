<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Select from "primevue/select";
import Tooltip from "primevue/tooltip";

import BaseCard from "@/components/ui/BaseCard.vue";
import CampoForm from "@/components/ui/CampoForm.vue";
import {
  addRiga,
  annullaBolla,
  deleteBolla,
  deleteRiga,
  emettiBolla,
  fetchBolla,
} from "@/services/bolle";
import { fetchArticoli } from "@/services/articoli";
import { fetchAnagrafiche } from "@/services/anagrafiche";
import { useAuthStore } from "@/stores/auth";
import { confirm, notify } from "@/composables/useConfirm";
import { makePtSelect } from "@/lib/prime-pt";
import { stileStato } from "@/lib/stato";

const vTooltip = Tooltip;
const ptFormSelect = makePtSelect("w-full", "bg-white");

const props = defineProps({ id: { type: String, required: true } });

const router = useRouter();
const authStore = useAuthStore();
const puoScrivere = computed(() => authStore.hasPermission("bolle.write"));
const puoEliminare = computed(() => authStore.hasPermission("bolle.delete"));

const bolla = ref(null);
const articoli = ref([]);
const anagrafiche = ref([]);
const loading = ref(true);
const errore = ref(null);

const fmtPrezzo = new Intl.NumberFormat("it-IT", { style: "currency", currency: "EUR" });

const isBozza = computed(() => bolla.value?.stato === "bozza");
const isEmessa = computed(() => bolla.value?.stato === "emessa");

const destinatario = computed(
  () => anagrafiche.value.find((a) => a.id === bolla.value?.anagrafica_id)?.display_name ?? "—",
);
const opzioniArticoli = computed(() =>
  articoli.value.map((a) => ({ label: `${a.codice} — ${a.descrizione}`, value: a.id })),
);

const CAUSALE_LABEL = {
  vendita: "Vendita",
  conto_visione: "Conto visione",
  reso: "Reso",
  riparazione: "Riparazione",
  omaggio: "Omaggio",
};
const TRASPORTO_LABEL = {
  mittente: "A cura del mittente",
  destinatario: "A cura del destinatario",
  vettore: "A cura del vettore",
};



async function carica() {
  loading.value = true;
  errore.value = null;
  try {
    const [b, art, anag] = await Promise.all([
      fetchBolla(props.id),
      fetchArticoli({ limit: 200 }),
      fetchAnagrafiche({ limit: 200 }),
    ]);
    bolla.value = b;
    articoli.value = art.items;
    anagrafiche.value = anag.items;
  } catch {
    errore.value = "Bolla non trovata o non accessibile.";
  } finally {
    loading.value = false;
  }
}

onMounted(carica);

function gestisciErrore(e, messaggioDefault) {
  if (e.response?.status === 403 && e.response?.data?.demo_readonly) return;
  notify({ message: e.response?.data?.detail ?? messaggioDefault });
}

// ── Composizione righe (solo bozza) ────────────────────────────────────────

const nuovoArticolo = ref(null);
const nuovaQuantita = ref(1);
const aggiungendo = ref(false);

async function aggiungiRiga() {
  if (!nuovoArticolo.value || !(nuovaQuantita.value > 0)) return;
  aggiungendo.value = true;
  try {
    bolla.value = await addRiga(props.id, {
      articolo_id: nuovoArticolo.value,
      quantita: nuovaQuantita.value,
    });
    nuovoArticolo.value = null;
    nuovaQuantita.value = 1;
  } catch (e) {
    gestisciErrore(e, "Errore durante l'aggiunta della riga.");
  } finally {
    aggiungendo.value = false;
  }
}

async function rimuoviRiga(riga) {
  try {
    bolla.value = await deleteRiga(props.id, riga.id);
  } catch (e) {
    gestisciErrore(e, "Errore durante la rimozione della riga.");
  }
}

// ── Transizioni di stato ───────────────────────────────────────────────────

const elaborando = ref(false);

async function emetti() {
  const ok = await confirm({
    title: "Emettere la bolla",
    message: "Verra' assegnato il numero progressivo e il documento non sara' piu' modificabile. Procedere?",
    confirmLabel: "Emetti",
  });
  if (!ok) return;
  elaborando.value = true;
  try {
    bolla.value = await emettiBolla(props.id);
  } catch (e) {
    gestisciErrore(e, "Errore durante l'emissione.");
  } finally {
    elaborando.value = false;
  }
}

async function annulla() {
  const ok = await confirm({
    title: "Annullare la bolla",
    message: `Confermare l'annullamento della bolla ${bolla.value?.numero}? L'operazione e' irreversibile.`,
    confirmLabel: "Annulla bolla",
    danger: true,
  });
  if (!ok) return;
  elaborando.value = true;
  try {
    bolla.value = await annullaBolla(props.id);
  } catch (e) {
    gestisciErrore(e, "Errore durante l'annullamento.");
  } finally {
    elaborando.value = false;
  }
}

async function eliminaBozza() {
  const ok = await confirm({
    title: "Eliminare la bozza",
    message: "La bozza verra' eliminata definitivamente. Procedere?",
    confirmLabel: "Elimina",
    danger: true,
  });
  if (!ok) return;
  try {
    await deleteBolla(props.id);
    router.push({ name: "bolle" });
  } catch (e) {
    gestisciErrore(e, "Errore durante l'eliminazione.");
  }
}
</script>

<template>
  <div class="space-y-6">
    <div v-if="loading" class="space-y-4">
      <div class="h-8 w-48 animate-pulse rounded-xl bg-steel-100" />
      <div class="h-40 animate-pulse rounded-2xl bg-steel-100" />
      <div class="h-48 animate-pulse rounded-2xl bg-steel-100" />
    </div>

    <div v-else-if="errore" class="rounded-2xl border border-red-200 bg-red-50 px-6 py-8 text-center">
      <p class="text-sm font-medium text-red-700">{{ errore }}</p>
      <button class="mt-4 text-sm text-brand-600 underline" @click="router.push({ name: 'bolle' })">
        Torna all'elenco
      </button>
    </div>

    <template v-else-if="bolla">
      <!-- Header -->
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-2 text-sm">
          <button
            class="group flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-steel-500 transition-all hover:bg-steel-100 hover:text-steel-900"
            @click="router.push({ name: 'bolle' })"
          >
            <svg class="h-4 w-4 transition-transform group-hover:-translate-x-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            Bolle
          </button>
          <span class="text-steel-300">/</span>
          <span class="font-medium text-steel-700">{{ bolla.numero ?? "Bozza" }}</span>
        </div>

        <div class="flex items-center gap-2">
          <span :class="stileStato(bolla.stato).classe">
            <span aria-hidden="true">{{ stileStato(bolla.stato).glifo }}</span>
            {{ bolla.stato }}
          </span>
          <button
            v-if="isBozza && puoScrivere"
            :disabled="elaborando || !bolla.righe.length"
            class="flex items-center gap-2 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-600 disabled:opacity-50"
            @click="emetti"
          >
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
            Emetti
          </button>
          <button
            v-if="isEmessa && puoEliminare"
            :disabled="elaborando"
            class="flex items-center gap-2 rounded-xl border border-steel-200 bg-white px-4 py-2 text-sm font-medium text-steel-700 transition hover:border-red-200 hover:bg-red-50 hover:text-red-700 disabled:opacity-50"
            @click="annulla"
          >
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" /><line x1="4.93" y1="4.93" x2="19.07" y2="19.07" /></svg>
            Annulla
          </button>
          <button
            v-if="isBozza && puoEliminare"
            v-tooltip.bottom="'Elimina bozza'"
            aria-label="Elimina bozza"
            class="flex h-9 w-9 items-center justify-center rounded-xl border border-steel-200 bg-white text-steel-500 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
            @click="eliminaBozza"
          >
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6" /><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /></svg>
          </button>
        </div>
      </div>

      <!-- Testata -->
      <BaseCard class="p-6">
        <h3 class="mb-4 etichetta-sezione">Documento di trasporto</h3>
        <dl class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <dt class="text-xs text-steel-600">Numero</dt>
            <dd class="mt-0.5 font-mono text-sm text-steel-900">{{ bolla.numero ?? "— (bozza)" }}</dd>
          </div>
          <div>
            <dt class="text-xs text-steel-600">Data documento</dt>
            <dd class="mt-0.5 text-sm text-steel-900">{{ new Date(bolla.data_documento).toLocaleDateString("it-IT") }}</dd>
          </div>
          <div>
            <dt class="text-xs text-steel-600">Destinatario</dt>
            <dd class="mt-0.5 text-sm font-medium text-steel-900">{{ destinatario }}</dd>
          </div>
          <div>
            <dt class="text-xs text-steel-600">Causale trasporto</dt>
            <dd class="mt-0.5 text-sm text-steel-700">{{ CAUSALE_LABEL[bolla.causale_trasporto] ?? bolla.causale_trasporto }}</dd>
          </div>
          <div>
            <dt class="text-xs text-steel-600">Aspetto dei beni</dt>
            <dd class="mt-0.5 text-sm text-steel-700">{{ bolla.aspetto_beni ?? "—" }}</dd>
          </div>
          <div>
            <dt class="text-xs text-steel-600">Trasporto</dt>
            <dd class="mt-0.5 text-sm text-steel-700">{{ TRASPORTO_LABEL[bolla.trasporto_a_cura] ?? "—" }}</dd>
          </div>
          <div v-if="bolla.vettore">
            <dt class="text-xs text-steel-600">Vettore</dt>
            <dd class="mt-0.5 text-sm text-steel-700">{{ bolla.vettore }}</dd>
          </div>
          <div v-if="bolla.note" class="sm:col-span-2 lg:col-span-3">
            <dt class="text-xs text-steel-600">Note</dt>
            <dd class="mt-0.5 text-sm text-steel-700">{{ bolla.note }}</dd>
          </div>
        </dl>
      </BaseCard>

      <!-- Righe -->
      <BaseCard class="overflow-hidden p-0">
        <div class="flex items-center justify-between border-b border-steel-100 px-6 py-4">
          <h3 class="etichetta-sezione">
            Righe ({{ bolla.righe.length }})
          </h3>
        </div>

        <div v-if="bolla.righe.length" class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="border-b border-steel-100 bg-steel-50">
              <tr>
                <th scope="col" class="px-4 py-2.5 text-left intestazione-tabella">Articolo</th>
                <th scope="col" class="px-4 py-2.5 text-right intestazione-tabella">Qta</th>
                <th scope="col" class="px-4 py-2.5 text-right intestazione-tabella">Prezzo</th>
                <th scope="col" class="hidden px-4 py-2.5 text-right intestazione-tabella sm:table-cell">IVA</th>
                <th scope="col" class="px-4 py-2.5 text-right intestazione-tabella">Importo</th>
                <th scope="col" v-if="isBozza && puoScrivere" class="px-4 py-2.5"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-steel-100">
              <tr v-for="riga in bolla.righe" :key="riga.id">
                <td class="px-4 py-3">
                  <p class="font-mono text-xs text-steel-600">{{ riga.codice_articolo }}</p>
                  <p class="text-steel-900">{{ riga.descrizione }}</p>
                </td>
                <td class="px-4 py-3 text-right cifre text-steel-700">
                  {{ Number(riga.quantita).toLocaleString("it-IT") }} {{ riga.unita_misura }}
                </td>
                <td class="px-4 py-3 text-right cifre text-steel-700">{{ fmtPrezzo.format(Number(riga.prezzo_unitario)) }}</td>
                <td class="hidden px-4 py-3 text-right cifre text-steel-600 sm:table-cell">{{ Number(riga.aliquota_iva) }}%</td>
                <td class="px-4 py-3 text-right cifre font-medium text-steel-900">{{ fmtPrezzo.format(Number(riga.importo_riga)) }}</td>
                <td v-if="isBozza && puoScrivere" class="px-4 py-3 text-right">
                  <button
                    v-tooltip.left="'Rimuovi riga'"
                    aria-label="Rimuovi riga"
                    class="flex h-8 w-8 items-center justify-center rounded-lg border border-steel-200 bg-white text-steel-500 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
                    @click="rimuoviRiga(riga)"
                  >
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12" /></svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="px-6 py-8 text-center text-sm text-steel-500">
          Nessuna riga. {{ isBozza ? "Aggiungi articoli per comporre il documento." : "" }}
        </p>

        <!-- Aggiunta riga (solo bozza) -->
        <div v-if="isBozza && puoScrivere" class="flex flex-col gap-3 border-t border-steel-100 bg-steel-50 px-6 py-4 sm:flex-row sm:items-end">
          <CampoForm v-slot="{ combo }" label="Articolo">
            <Select v-bind="combo"
              v-model="nuovoArticolo"
              :options="opzioniArticoli"
              option-label="label"
              option-value="value"
              placeholder="Seleziona un articolo"
              filter
              :pt="ptFormSelect"
            />
          </CampoForm>
          <CampoForm v-slot="{ campo }" label="Quantità">
            <input v-bind="campo"
              v-model.number="nuovaQuantita"
              type="number"
              min="0"
              step="0.001"
              class="w-full rounded-xl border border-steel-200 bg-white px-3 py-2 text-sm text-steel-900 focus:outline-none focus:ring-2 focus:ring-brand-400"
            />
          </CampoForm>
          <button
            type="button"
            :disabled="aggiungendo || !nuovoArticolo"
            class="rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-600 disabled:opacity-50"
            @click="aggiungiRiga"
          >
            {{ aggiungendo ? "…" : "Aggiungi" }}
          </button>
        </div>
      </BaseCard>

      <!-- Totali -->
      <BaseCard class="p-6">
        <dl class="ml-auto max-w-xs space-y-2">
          <div class="flex justify-between text-sm">
            <dt class="text-steel-500">Imponibile</dt>
            <dd class="text-steel-900">{{ fmtPrezzo.format(Number(bolla.totale_imponibile)) }}</dd>
          </div>
          <div class="flex justify-between text-sm">
            <dt class="text-steel-500">IVA</dt>
            <dd class="text-steel-900">{{ fmtPrezzo.format(Number(bolla.totale_iva)) }}</dd>
          </div>
          <div class="flex justify-between border-t border-steel-100 pt-2 text-base font-semibold">
            <dt class="text-steel-700">Totale</dt>
            <dd class="text-steel-900">{{ fmtPrezzo.format(Number(bolla.totale)) }}</dd>
          </div>
        </dl>
      </BaseCard>
    </template>
  </div>
</template>
