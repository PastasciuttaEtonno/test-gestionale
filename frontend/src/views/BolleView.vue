<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";
import InputText from "primevue/inputtext";
import Select from "primevue/select";

import BaseCard from "@/components/ui/BaseCard.vue";
import CampoForm from "@/components/ui/CampoForm.vue";
import SectionLabel from "@/components/ui/SectionLabel.vue";
import { createBolla, fetchBolle } from "@/services/bolle";
import { fetchAnagrafiche } from "@/services/anagrafiche";
import { useAuthStore } from "@/stores/auth";
import { stileStato } from "@/lib/stato";
import {
  ptIconField,
  ptInputIcon,
  makePtInputText,
  makePtSelect,
  makeDialogPt,
} from "@/lib/prime-pt";

const router = useRouter();
const authStore = useAuthStore();
const puoScrivere = computed(() => authStore.hasPermission("bolle.write"));

const items = ref([]);
const total = ref(0);
const loading = ref(false);
const errore = ref(null);
const anagrafiche = ref([]);

const filtroQ = ref("");
const filtroStato = ref(null);
const skip = ref(0);
const limit = 20;

const ptInputText = makePtInputText();
const ptSelect = makePtSelect("w-full sm:w-48");
const ptFormSelect = makePtSelect("w-full", "bg-white");
const dialogPt = makeDialogPt("max-w-xl");

const opzioniStato = [
  { label: "Bozze", value: "bozza" },
  { label: "Emesse", value: "emessa" },
  { label: "Annullate", value: "annullata" },
];
const opzioniCausale = [
  { label: "Vendita", value: "vendita" },
  { label: "Conto visione", value: "conto_visione" },
  { label: "Reso", value: "reso" },
  { label: "Riparazione", value: "riparazione" },
  { label: "Omaggio", value: "omaggio" },
];
const opzioniTrasporto = [
  { label: "A cura del mittente", value: "mittente" },
  { label: "A cura del destinatario", value: "destinatario" },
  { label: "A cura del vettore", value: "vettore" },
];

const fmtPrezzo = new Intl.NumberFormat("it-IT", { style: "currency", currency: "EUR" });

const opzioniAnagrafiche = computed(() =>
  anagrafiche.value.map((a) => ({ label: a.display_name, value: a.id })),
);

function nomeAnagrafica(id) {
  return anagrafiche.value.find((a) => a.id === id)?.display_name ?? "—";
}

async function caricaAnagrafiche() {
  try {
    const res = await fetchAnagrafiche({ limit: 200 });
    anagrafiche.value = res.items;
  } catch {
    anagrafiche.value = [];
  }
}

async function caricaBolle() {
  loading.value = true;
  errore.value = null;
  try {
    const params = { skip: skip.value, limit };
    if (filtroStato.value) params.stato = filtroStato.value;
    if (filtroQ.value.trim()) params.q = filtroQ.value.trim();
    const res = await fetchBolle(params);
    items.value = res.items;
    total.value = res.total;
  } catch {
    errore.value = "Errore nel caricamento delle bolle.";
  } finally {
    loading.value = false;
  }
}

watch([filtroQ, filtroStato], () => {
  skip.value = 0;
  caricaBolle();
});

caricaAnagrafiche();
caricaBolle();

// ── Stato badge ────────────────────────────────────────────────────────────



// ── Modale crea bozza ────────────────────────────────────────────────────

const mostraMod = ref(false);
const salvataggio = ref(false);
const erroreForm = ref(null);

const oggi = new Date().toISOString().slice(0, 10);
const formVuoto = () => ({
  anagrafica_id: null,
  data_documento: oggi,
  causale_trasporto: "vendita",
  aspetto_beni: "",
  trasporto_a_cura: "destinatario",
  vettore: "",
  note: "",
});
const form = reactive(formVuoto());

function apriCrea() {
  Object.assign(form, formVuoto());
  erroreForm.value = null;
  mostraMod.value = true;
}

async function salva() {
  erroreForm.value = null;
  if (!form.anagrafica_id) {
    erroreForm.value = "Selezionare il destinatario.";
    return;
  }
  salvataggio.value = true;
  try {
    const creata = await createBolla({
      anagrafica_id: form.anagrafica_id,
      data_documento: form.data_documento,
      causale_trasporto: form.causale_trasporto,
      aspetto_beni: form.aspetto_beni || null,
      trasporto_a_cura: form.trasporto_a_cura || null,
      vettore: form.vettore || null,
      note: form.note || null,
    });
    mostraMod.value = false;
    router.push({ name: "bolla-detail", params: { id: creata.id } });
  } catch (e) {
    if (e.response?.status === 403 && e.response?.data?.demo_readonly) {
      mostraMod.value = false;
    } else {
      erroreForm.value = e.response?.data?.detail ?? "Errore durante la creazione.";
    }
  } finally {
    salvataggio.value = false;
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <SectionLabel label="Bolle / DDT" />
      <Button
        v-if="puoScrivere"
        label="Nuova bolla"
        icon="pi pi-plus"
        size="small"
        class="shrink-0 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600"
        @click="apriCrea"
      />
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
          <InputText v-model="filtroQ" placeholder="Cerca per numero (es. BL4441)…" aria-label="Cerca bolla per numero" :pt="ptInputText" />
        </IconField>
        <Select
          v-model="filtroStato"
          :options="opzioniStato"
          option-label="label"
          option-value="value"
          placeholder="Tutti gli stati"
          aria-label="Filtra per stato"
          show-clear
          :pt="ptSelect"
        />
        <div class="flex items-center gap-3 sm:ml-auto">
          <span class="text-xs text-steel-700">
            <span class="font-semibold text-steel-900">{{ total }}</span> risultati
          </span>
        </div>
      </div>
    </BaseCard>

    <p v-if="errore" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ errore }}
    </p>

    <div v-if="loading" class="space-y-3">
      <div v-for="n in 5" :key="n" class="h-14 animate-pulse rounded-xl bg-steel-100" />
    </div>

    <BaseCard v-else-if="items.length">
      <div class="overflow-hidden rounded-2xl border border-steel-200">
        <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <caption class="sr-only">Elenco bolle: numero, stato, destinatario, data e totale.</caption>
          <thead class="border-b border-steel-100 bg-steel-50">
            <tr>
              <th scope="col" class="px-4 py-3 text-left intestazione-tabella">Numero</th>
              <th scope="col" class="px-4 py-3 text-left intestazione-tabella">Stato</th>
              <th scope="col" class="hidden px-4 py-3 text-left intestazione-tabella sm:table-cell">Destinatario</th>
              <th scope="col" class="hidden px-4 py-3 text-left intestazione-tabella md:table-cell">Data</th>
              <th scope="col" class="px-4 py-3 text-right intestazione-tabella">Totale</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-steel-100">
            <tr
              v-for="b in items"
              :key="b.id"
              class="cursor-pointer transition-colors hover:bg-steel-50"
              @click="router.push({ name: 'bolla-detail', params: { id: b.id } })"
            >
              <td class="px-4 py-3 font-mono text-steel-900">
                <RouterLink
                  :to="{ name: 'bolla-detail', params: { id: b.id } }"
                  class="link-riga"
                  :aria-label="`Apri la bolla ${b.numero ?? 'ancora in bozza'}`"
                  @click.stop
                >{{ b.numero ?? "— bozza" }}</RouterLink>
              </td>
              <td class="px-4 py-3">
                <span :class="stileStato(b.stato).classe">
                  <span aria-hidden="true">{{ stileStato(b.stato).glifo }}</span>
                  {{ b.stato }}
                </span>
              </td>
              <td class="hidden px-4 py-3 text-steel-700 sm:table-cell">{{ nomeAnagrafica(b.anagrafica_id) }}</td>
              <td class="hidden px-4 py-3 text-steel-600 md:table-cell">
                {{ new Date(b.data_documento).toLocaleDateString("it-IT") }}
              </td>
              <td class="px-4 py-3 text-right cifre font-medium text-steel-900">{{ fmtPrezzo.format(Number(b.totale)) }}</td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
    </BaseCard>

    <BaseCard v-else class="py-16 text-center">
      <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-steel-100 text-steel-400">
        <svg class="h-7 w-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="8" y1="13" x2="16" y2="13" />
          <line x1="8" y1="17" x2="16" y2="17" />
        </svg>
      </div>
      <p class="text-sm font-medium text-steel-700">Nessuna bolla trovata</p>
      <p class="mt-1 text-xs text-steel-700">
        {{ filtroQ || filtroStato ? "Prova a modificare i filtri." : "Crea la prima bolla per iniziare." }}
      </p>
      <button
        v-if="puoScrivere && !filtroQ && !filtroStato"
        class="mt-4 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600"
        @click="apriCrea"
      >
        Crea bolla
      </button>
    </BaseCard>

    <!-- Modale crea bozza -->
    <Dialog
      v-model:visible="mostraMod"
      header="Nuova bolla (bozza)"
      :modal="true"
      :closable="true"
      :draggable="false"
      :pt="dialogPt"
    >
      <form class="space-y-5" @submit.prevent="salva">
        <p class="text-xs text-steel-600">I campi contrassegnati con * sono obbligatori.</p>

        <CampoForm v-slot="{ combo }" label="Destinatario" obbligatorio>
          <Select v-bind="combo"
            v-model="form.anagrafica_id"
            
            :options="opzioniAnagrafiche"
            option-label="label"
            option-value="value"
            placeholder="Seleziona cliente/destinatario"
            filter
            :pt="ptFormSelect"
          />
        </CampoForm>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CampoForm v-slot="{ campo }" label="Data documento">
            <input
              v-model="form.data_documento"
              v-bind="campo"
              type="date"
              class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm text-steel-900 focus:outline-none focus:ring-2 focus:ring-brand-400"
            />
          </CampoForm>
          <CampoForm v-slot="{ combo }" label="Causale trasporto">
            <Select v-bind="combo" v-model="form.causale_trasporto"  :options="opzioniCausale" option-label="label" option-value="value" :pt="ptFormSelect" />
          </CampoForm>
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CampoForm v-slot="{ campo }" label="Aspetto dei beni">
            <InputText v-model="form.aspetto_beni" v-bind="campo" placeholder="Pallet / Scatole / A vista" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
          </CampoForm>
          <CampoForm v-slot="{ combo }" label="Trasporto a cura di">
            <Select v-bind="combo" v-model="form.trasporto_a_cura"  :options="opzioniTrasporto" option-label="label" option-value="value" :pt="ptFormSelect" />
          </CampoForm>
        </div>
        <CampoForm v-slot="{ campo }" label="Vettore" aiuto="Facoltativo.">
          <InputText v-model="form.vettore" v-bind="campo" placeholder="Nome del vettore" class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm" />
        </CampoForm>
        <CampoForm v-slot="{ campo }" label="Note">
          <textarea
            v-model="form.note"
            v-bind="campo"
            rows="2"
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
          <button type="button" :disabled="salvataggio" class="rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-60" @click="salva">
            {{ salvataggio ? "Creazione…" : "Crea e componi" }}
          </button>
        </div>
      </template>
    </Dialog>
  </div>
</template>
