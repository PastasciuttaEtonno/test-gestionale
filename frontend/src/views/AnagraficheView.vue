<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Tag from "primevue/tag";
import Tooltip from "primevue/tooltip";

import BaseCard from "@/components/ui/BaseCard.vue";
import CampoForm from "@/components/ui/CampoForm.vue";
import SectionLabel from "@/components/ui/SectionLabel.vue";
import {
  createAnagrafica,
  deleteAnagrafica,
  fetchAnagrafiche,
  updateAnagrafica,
} from "@/services/anagrafiche";
import { useAuthStore } from "@/stores/auth";
import { confirm, notify } from "@/composables/useConfirm";
import { ptIconField, ptInputIcon, makePtInputText, makePtSelect, makeDialogPt } from "@/lib/prime-pt";

const vTooltip = Tooltip;

const router = useRouter();
const authStore = useAuthStore();
const puoScrivere = computed(() => authStore.hasPermission("anagrafiche.write"));
const puoEliminare = computed(() => authStore.hasPermission("anagrafiche.delete"));

// ── Stato lista ───────────────────────────────────────────────────────────

const items = ref([]);
const total = ref(0);
const loading = ref(false);
const errore = ref(null);

const filtroQ = ref("");
const filtroTipo = ref(null);
const filtroAttivi = ref(true);
const skip = ref(0);
const limit = 20;

const opzioniTipo = [
  { label: "Clienti", value: "cliente" },
  { label: "Fornitori", value: "fornitore" },
  { label: "Cliente + Fornitore", value: "cliente_fornitore" },
  { label: "Agenti", value: "agente" },
  { label: "Altro", value: "altro" },
];

const ptInputText = makePtInputText();
const ptSelect = makePtSelect("w-full sm:w-44");
const ptFormSelect = makePtSelect("w-full", "bg-white");
const dialogPt = makeDialogPt("max-w-2xl");

async function caricaAnagrafiche() {
  loading.value = true;
  errore.value = null;
  try {
    const params = {
      is_active: filtroAttivi.value,
      skip: skip.value,
      limit,
    };
    if (filtroTipo.value) params.tipo = filtroTipo.value;
    if (filtroQ.value.trim()) params.q = filtroQ.value.trim();
    const res = await fetchAnagrafiche(params);
    items.value = res.items;
    total.value = res.total;
  } catch {
    errore.value = "Errore nel caricamento delle anagrafiche.";
  } finally {
    loading.value = false;
  }
}

watch([filtroQ, filtroTipo, filtroAttivi], () => {
  skip.value = 0;
  caricaAnagrafiche();
});

caricaAnagrafiche();

// ── Modale create / edit ──────────────────────────────────────────────────

const mostraMod = ref(false);
const modTitolo = computed(() => (form.id ? "Modifica anagrafica" : "Nuova anagrafica"));
const salvataggio = ref(false);
const erroreForm = ref(null);

const formVuoto = () => ({
  id: null,
  tipo: "cliente",
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
    erroreForm.value = "La ragione sociale è obbligatoria per ente o società.";
    return;
  }
  salvataggio.value = true;
  try {
    const payload = { ...form };
    delete payload.id;
    // Pulizia campi vuoti
    Object.keys(payload).forEach((k) => {
      if (payload[k] === "") payload[k] = null;
    });
    if (form.id) {
      await updateAnagrafica(form.id, payload);
    } else {
      await createAnagrafica(payload);
    }
    mostraMod.value = false;
    await caricaAnagrafiche();
  } catch (e) {
    erroreForm.value =
      e.response?.data?.detail ?? "Errore durante il salvataggio.";
  } finally {
    salvataggio.value = false;
  }
}

// ── Filtri helpers ────────────────────────────────────────────────────────

const filtriApplicati = computed(
  () => filtroQ.value.trim() !== "" || filtroTipo.value !== null || !filtroAttivi.value
);

function azzeraFiltri() {
  filtroQ.value = "";
  filtroTipo.value = null;
  filtroAttivi.value = true;
}

// ── Soft delete ───────────────────────────────────────────────────────────

async function disattiva(a) {
  const ok = await confirm({
    title: "Disattivare l'anagrafica",
    message: `Confermare la disattivazione di "${a.display_name}"? Il record sarà nascosto dall'elenco ma non eliminato.`,
    confirmLabel: "Disattiva",
    danger: true,
  });
  if (!ok) return;
  try {
    await deleteAnagrafica(a.id);
    await caricaAnagrafiche();
  } catch {
    await notify({ message: "Errore durante la disattivazione. Riprovare." });
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────

function ptTipoTag() {
  // Il tipo soggetto e' una categoria, non uno stato: la parola la porta gia'
  // tutta. Restano neutri e squadrati, cosi' il colore e la pillola tonda
  // continuano a significare soltanto "stato del documento".
  return { root: { class: "tag-categoria" } };
}

function labelTipo(tipo) {
  return (
    {
      cliente: "Cliente",
      fornitore: "Fornitore",
      cliente_fornitore: "Cli + For",
      agente: "Agente",
      altro: "Altro",
    }[tipo] ?? tipo
  );
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
    <!-- Intestazione pagina -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <SectionLabel label="Anagrafiche" />
      <Button
        v-if="puoScrivere"
        label="Nuova anagrafica"
        icon="pi pi-plus"
        size="small"
        class="shrink-0 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600"
        @click="apriCrea"
      />
    </div>

    <!-- Filtri -->
    <BaseCard class="p-4">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">

        <!-- Ricerca testuale -->
        <IconField :pt="ptIconField" class="flex-1 sm:max-w-sm">
          <InputIcon :pt="ptInputIcon">
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </InputIcon>
          <InputText
            v-model="filtroQ"
            placeholder="Cerca per nome, P.IVA, CF…"
            aria-label="Cerca anagrafica per nome, partita IVA o codice fiscale"
            :pt="ptInputText"
          />
        </IconField>

        <!-- Filtro tipo -->
        <Select
          v-model="filtroTipo"
          :options="opzioniTipo"
          option-label="label"
          option-value="value"
          placeholder="Tutti i tipi"
          aria-label="Filtra per tipo di soggetto"
          show-clear
          :pt="ptSelect"
        />

        <!-- Toggle solo attivi -->
        <button
          type="button"
          class="flex shrink-0 items-center gap-2.5"
          @click="filtroAttivi = !filtroAttivi"
        >
          <span
            class="relative inline-flex h-5 w-9 shrink-0 rounded-full border-2 border-transparent transition-colors duration-200"
            :class="filtroAttivi ? 'bg-steel-700' : 'bg-steel-200'"
          >
            <span
              class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition-transform duration-200"
              :class="filtroAttivi ? 'translate-x-4' : 'translate-x-0'"
            />
          </span>
          <span
            class="text-sm transition-colors"
            :class="filtroAttivi ? 'font-medium text-steel-900' : 'text-steel-500'"
          >
            Solo attivi
          </span>
        </button>

        <!-- Contatore + reset -->
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
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
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
      <div
        v-for="n in 5"
        :key="n"
        class="h-14 animate-pulse rounded-xl bg-steel-100"
      />
    </div>

    <!-- Tabella -->
    <BaseCard v-else-if="items.length">
      <div class="overflow-hidden rounded-2xl border border-steel-200">
        <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <caption class="sr-only">Elenco anagrafiche: soggetto, tipo, partita IVA o codice fiscale, contatti e azioni.</caption>
          <thead class="border-b border-steel-100 bg-steel-50">
            <tr>
              <th scope="col" class="px-4 py-3 text-left intestazione-tabella">
                Soggetto
              </th>
              <th scope="col" class="hidden px-4 py-3 text-left intestazione-tabella sm:table-cell">
                Tipo
              </th>
              <th scope="col" class="hidden px-4 py-3 text-left intestazione-tabella md:table-cell">
                P.IVA / CF
              </th>
              <th scope="col" class="hidden px-4 py-3 text-left intestazione-tabella lg:table-cell">
                Contatti
              </th>
              <th scope="col" class="px-4 py-3 text-right intestazione-tabella">
                Azioni
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-steel-100">
            <tr
              v-for="a in items"
              :key="a.id"
              class="cursor-pointer transition-colors hover:bg-steel-50"
              @click="router.push({ name: 'anagrafica-detail', params: { id: a.id } })"
            >
              <!-- Nome + sede -->
              <td class="px-4 py-3">
                <p class="font-medium text-steel-900">
                  <RouterLink
                    :to="{ name: 'anagrafica-detail', params: { id: a.id } }"
                    class="link-riga"
                    @click.stop
                  >{{ a.display_name }}</RouterLink>
                </p>
                <p
                  v-if="a.indirizzi?.[0]"
                  class="mt-0.5 text-xs text-steel-600"
                >
                  {{ a.indirizzi[0].citta }}
                  <span v-if="a.indirizzi[0].provincia">({{ a.indirizzi[0].provincia }})</span>
                </p>
              </td>
              <!-- Tipo -->
              <td class="hidden px-4 py-3 sm:table-cell">
                <Tag :pt="ptTipoTag()" :value="labelTipo(a.tipo)" />
              </td>
              <!-- P.IVA / CF -->
              <td class="hidden px-4 py-3 text-steel-600 md:table-cell">
                <span v-if="a.partita_iva">{{ a.partita_iva }}</span>
                <span v-else-if="a.codice_fiscale" class="text-steel-600">{{ a.codice_fiscale }}</span>
                <span v-else class="text-steel-300">—</span>
              </td>
              <!-- Contatti -->
              <td class="hidden px-4 py-3 lg:table-cell">
                <div class="space-y-0.5 text-steel-600">
                  <p v-if="a.email" class="text-xs">{{ a.email }}</p>
                  <p v-if="a.telefono" class="text-xs">{{ a.telefono }}</p>
                  <p v-if="!a.email && !a.telefono" class="text-xs text-steel-300">—</p>
                </div>
              </td>
              <!-- Azioni -->
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
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
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
                      <circle cx="12" cy="12" r="10"/>
                      <line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/>
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
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
      </div>
      <p class="text-sm font-medium text-steel-700">Nessuna anagrafica trovata</p>
      <p class="mt-1 text-xs text-steel-700">
        {{ filtroQ || filtroTipo ? "Prova a modificare i filtri di ricerca." : "Crea la prima anagrafica per iniziare." }}
      </p>
      <button
        v-if="puoScrivere && !filtroQ && !filtroTipo"
        class="mt-4 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600"
        @click="apriCrea"
      >
        Crea anagrafica
      </button>
    </BaseCard>

    <!-- Modale create / edit -->
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

        <!-- Tipo + persona fisica -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CampoForm v-slot="{ combo }" label="Tipo" obbligatorio>
            <Select v-bind="combo"
              v-model="form.tipo"
              
              :options="opzioniTipoForm"
              option-label="label"
              option-value="value"
              :pt="ptFormSelect"
            />
          </CampoForm>
          <div class="flex items-end pb-1">
            <label class="flex cursor-pointer items-center gap-2 text-sm text-steel-700">
              <input
                v-model="form.is_persona_fisica"
                type="checkbox"
                class="h-4 w-4 rounded border-steel-300 text-brand-500"
              />
              Persona fisica
            </label>
          </div>
        </div>

        <!-- Nome / Ragione sociale -->
        <div v-if="form.is_persona_fisica" class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CampoForm v-slot="{ campo }" label="Cognome" obbligatorio>
            <InputText
              v-model="form.cognome"
              v-bind="campo"
              placeholder="Ferrari"
              autocomplete="family-name"
              class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm"
            />
          </CampoForm>
          <CampoForm v-slot="{ campo }" label="Nome">
            <InputText
              v-model="form.nome"
              v-bind="campo"
              placeholder="Marco"
              autocomplete="given-name"
              class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm"
            />
          </CampoForm>
        </div>
        <CampoForm v-else v-slot="{ campo }" label="Ragione sociale" obbligatorio>
          <InputText
            v-model="form.ragione_sociale"
            v-bind="campo"
            placeholder="Edilceram S.r.l."
            autocomplete="organization"
            class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm"
          />
        </CampoForm>

        <!-- P.IVA + CF -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CampoForm v-slot="{ campo }" label="Partita IVA" aiuto="11 cifre, senza il prefisso IT.">
            <InputText
              v-model="form.partita_iva"
              v-bind="campo"
              placeholder="03456789012"
              inputmode="numeric"
              maxlength="11"
              class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm"
            />
          </CampoForm>
          <CampoForm
            v-slot="{ campo }"
            label="Codice fiscale"
            aiuto="16 caratteri per le persone fisiche, 11 cifre per le società."
          >
            <InputText
              v-model="form.codice_fiscale"
              v-bind="campo"
              placeholder="03456789012"
              maxlength="16"
              class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm"
            />
          </CampoForm>
        </div>

        <!-- SDI + PEC -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CampoForm
            v-slot="{ campo }"
            label="Codice SDI"
            aiuto="7 caratteri. Vale 0000000 se il destinatario riceve via PEC."
          >
            <InputText
              v-model="form.codice_sdi"
              v-bind="campo"
              placeholder="M5UXCR1"
              maxlength="7"
              class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm"
            />
          </CampoForm>
          <CampoForm
            v-slot="{ campo }"
            label="PEC"
            aiuto="Serve quando il codice SDI è 0000000."
          >
            <InputText
              v-model="form.pec"
              v-bind="campo"
              placeholder="azienda@pec.it"
              type="email"
              autocomplete="off"
              class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm"
            />
          </CampoForm>
        </div>

        <!-- Regime fiscale + Natura giuridica -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CampoForm v-slot="{ combo }" label="Regime fiscale">
            <Select v-bind="combo"
              v-model="form.regime_fiscale"
              
              :options="opzioniRegime"
              option-label="label"
              option-value="value"
              :pt="ptFormSelect"
            />
          </CampoForm>
          <CampoForm v-slot="{ campo }" label="Natura giuridica" aiuto="Forma societaria, per esempio SRL o SPA.">
            <InputText
              v-model="form.natura_giuridica"
              v-bind="campo"
              placeholder="SRL"
              class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm"
            />
          </CampoForm>
        </div>

        <!-- Email + Telefono -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CampoForm v-slot="{ campo }" label="Email">
            <InputText
              v-model="form.email"
              v-bind="campo"
              placeholder="info@azienda.it"
              type="email"
              autocomplete="email"
              class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm"
            />
          </CampoForm>
          <CampoForm v-slot="{ campo }" label="Telefono">
            <InputText
              v-model="form.telefono"
              v-bind="campo"
              placeholder="059 123456"
              type="tel"
              autocomplete="tel"
              class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm"
            />
          </CampoForm>
        </div>

        <!-- Note -->
        <CampoForm v-slot="{ campo }" label="Note">
          <textarea
            v-model="form.note"
            v-bind="campo"
            rows="2"
            placeholder="Annotazioni libere…"
            class="w-full rounded-xl border border-steel-200 px-3 py-2 text-sm text-steel-900 placeholder-steel-400 focus:outline-none focus:ring-2 focus:ring-brand-400"
          />
        </CampoForm>

        <!-- Errore form -->
        <p
          v-if="erroreForm"
          role="alert"
          class="rounded-xl border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700"
        >
          {{ erroreForm }}
        </p>
      </form>

      <template #footer>
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="rounded-xl border border-steel-200 bg-white px-4 py-2 text-sm font-medium text-steel-700 hover:bg-steel-50"
            @click="mostraMod = false"
          >
            Annulla
          </button>
          <button
            type="button"
            :disabled="salvataggio"
            class="rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-60"
            @click="salva"
          >
            {{ salvataggio ? "Salvataggio…" : form.id ? "Salva modifiche" : "Crea anagrafica" }}
          </button>
        </div>
      </template>
    </Dialog>
  </div>
</template>
