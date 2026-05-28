<script setup>
import { computed, ref, watch } from "vue";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Tag from "primevue/tag";
import BaseButton from "../components/ui/BaseButton.vue";
import BaseCard from "../components/ui/BaseCard.vue";
import KpiTile from "../components/ui/KpiTile.vue";
import SectionLabel from "../components/ui/SectionLabel.vue";
import { useAuthStore } from "../stores/auth";
import { useDashboardStore } from "../stores/dashboard";
import { useTasksStore } from "../stores/tasks";
import { avviaGenerazioneReport } from "../services/reports";
import { ptIconField, ptInputIcon, makePtInputText, makePtSelect } from "../lib/prime-pt";
const authStore = useAuthStore();
const tasksStore = useTasksStore();
const dashboardStore = useDashboardStore();

const filtroTesto = ref("");
const filtroTipo = ref(null);
const filtroStato = ref(null);

const opzioniTipo = ["Fattura", "Bolla"];
const opzioniStato = ["Aperta", "Bozza", "Confermata", "Da chiudere", "Da inviare", "Emessa"];

const ptInputText = makePtInputText("sm:w-auto sm:min-w-[200px]");
const ptSelect = makePtSelect("min-w-[132px]");

const ptTagStato = {
  root: {
    class:
      "inline-flex min-w-[108px] items-center justify-center rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-brand-700",
  },
};

const indicatori = [
  {
    label: "Documenti aperti",
    value: "84",
    note: "Bolle, ordini e fatture in lavorazione.",
  },
  {
    label: "Da evadere oggi",
    value: "16",
    note: "Pratiche in coda per il team operativo.",
  },
  {
    label: "Clienti attivi",
    value: "264",
    note: "Anagrafiche abilitate a ordini e fatturazione.",
  },
  {
    label: "Alert anagrafici",
    value: "4",
    note: "Record con dati incompleti o da validare.",
  },
];

const azioniRapide = [
  "Nuova fattura",
  "Nuova bolla",
  "Apri cliente",
  "Cerca documento",
];

const tenantIdInput = ref(authStore.user?.tenant_id || "");
const taskId = ref("");
const loadingTask = ref(false);

const taskState = computed(() =>
  taskId.value ? tasksStore.getTask(taskId.value) : null,
);
const taskStatus = computed(() => taskState.value?.status || "idle");
const taskProgress = computed(() => taskState.value?.progress || 0);
const taskMessage = computed(
  () => taskState.value?.message || "Nessun report asincrono avviato.",
);
const resultUrl = computed(() => taskState.value?.resultUrl || "");

watch(taskStatus, (status) => {
  if (["success", "failure"].includes(status)) {
    loadingTask.value = false;
  }
});

async function avviaTaskReport() {
  if (!tenantIdInput.value) {
    return;
  }

  loadingTask.value = true;

  try {
    const response = await avviaGenerazioneReport({
      tenant_id: tenantIdInput.value,
    });
    taskId.value = response.task_id;
    tasksStore.initTask(response.task_id);
  } catch (error) {
    loadingTask.value = false;
    taskId.value = "";
    console.error("Avvio report fallito:", error?.response?.data?.detail);
  }
}

const righeDocumenti = [
  {
    data: "15/05/2026",
    tipo: "Fattura",
    numero: "FT-2026-0184",
    cliente: "Ceramiche Aurora S.p.A.",
    causale: "Fornitura gres porcellanato",
    importo: "12.480,00 EUR",
    stato: "Da inviare",
  },
  {
    data: "15/05/2026",
    tipo: "Bolla",
    numero: "BL-2026-0441",
    cliente: "Logistica Tirrena S.r.l.",
    causale: "Consegna lotti magazzino nord",
    importo: "-",
    stato: "Aperta",
  },
  {
    data: "14/05/2026",
    tipo: "Fattura",
    numero: "FT-2026-0183",
    cliente: "Edilceram Group",
    causale: "Saldo commessa showroom",
    importo: "8.930,00 EUR",
    stato: "Bozza",
  },
  {
    data: "14/05/2026",
    tipo: "Bolla",
    numero: "BL-2026-0438",
    cliente: "Trasporti Vela S.r.l.",
    causale: "Partenza merce area export",
    importo: "-",
    stato: "Confermata",
  },
  {
    data: "13/05/2026",
    tipo: "Fattura",
    numero: "FT-2026-0182",
    cliente: "Rivestimenti Domus",
    causale: "Vendita campionatura tecnica",
    importo: "2.140,00 EUR",
    stato: "Emessa",
  },
  {
    data: "13/05/2026",
    tipo: "Bolla",
    numero: "BL-2026-0431",
    cliente: "Ceramica Nuova Linea",
    causale: "Prelievo rapido stock interno",
    importo: "-",
    stato: "Da chiudere",
  },
];

const righeFiltraite = computed(() => {
  return righeDocumenti.filter((riga) => {
    const testoOk =
      !filtroTesto.value ||
      riga.cliente.toLowerCase().includes(filtroTesto.value.toLowerCase()) ||
      riga.numero.toLowerCase().includes(filtroTesto.value.toLowerCase());
    const tipoOk = !filtroTipo.value || riga.tipo === filtroTipo.value;
    const statoOk = !filtroStato.value || riga.stato === filtroStato.value;
    return testoOk && tipoOk && statoOk;
  });
});
</script>

<template>
  <div class="space-y-4 sm:space-y-6">
      <BaseCard :highlight="true">
        <div class="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
          <div>
            <SectionLabel>Workspace standard</SectionLabel>
            <h2 class="mt-3 text-2xl font-semibold text-steel-900 sm:text-3xl">
              Vista elenco documenti
            </h2>
            <p class="mt-3 max-w-3xl text-sm leading-6 text-steel-700">
              Mockup statico di una home ERP enterprise con sidebar, toolbar e griglia
              dati densa. Serve solo a validare ingombri, gerarchia visiva e leggibilità.
            </p>
          </div>

          <div class="flex flex-wrap gap-3">
            <BaseButton
              v-for="azione in azioniRapide"
              :key="azione"
              type="button"
              variant="secondary"
            >
              {{ azione }}
            </BaseButton>
          </div>
        </div>

        <div class="mt-6 grid gap-3 sm:gap-4 md:grid-cols-2 xl:grid-cols-4">
          <KpiTile
            v-for="indicatore in indicatori"
            :key="indicatore.label"
            :label="indicatore.label"
            :value="indicatore.value"
            :note="indicatore.note"
          />
        </div>

        <!-- KPI reali tenant-aware (aggiornati via SSE) -->
        <div
          v-if="dashboardStore.kpis"
          class="mt-6 rounded-[1.5rem] border border-brand-100 bg-brand-50/40 p-5"
        >
          <div class="mb-4 flex items-center justify-between">
            <SectionLabel>KPI Tenant Live</SectionLabel>
            <span
              v-if="dashboardStore.lastUpdated"
              class="text-[11px] text-steel-400"
            >
              Aggiornato {{ dashboardStore.lastUpdated.toLocaleTimeString("it-IT") }}
            </span>
          </div>
          <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
            <KpiTile label="Utenti totali" :value="String(dashboardStore.kpis.total_users)" note="Utenti nel tenant." />
            <KpiTile label="Utenti attivi" :value="String(dashboardStore.kpis.active_users)" note="Account attivi." />
            <KpiTile label="Audit 24h" :value="String(dashboardStore.kpis.audit_events_last_24h)" note="Operazioni nelle ultime 24 ore." />
            <KpiTile label="Profilo azienda" :value="dashboardStore.kpis.company_profile_configured ? 'Configurato' : 'Mancante'" note="Dati aziendali." />
            <KpiTile label="SMTP" :value="dashboardStore.kpis.smtp_configured ? 'Configurato' : 'Non configurato'" note="Impostazioni email." />
          </div>
        </div>

        <div class="mt-8 rounded-[1.5rem] border border-steel-200 bg-steel-50/80 p-5">
          <div class="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
            <div class="max-w-2xl">
              <SectionLabel>Async Queue Demo</SectionLabel>
              <h3 class="mt-3 text-2xl font-semibold text-steel-900">
                Generazione report con Celery e SSE
              </h3>
              <p class="mt-3 text-sm leading-6 text-steel-700">
                Il task Celery pubblica gli aggiornamenti su Redis Pub/Sub.
                Il frontend riceve i progressi in tempo reale via Server-Sent Events,
                senza polling.
              </p>
            </div>

            <div class="flex w-full max-w-xl flex-col gap-3 xl:items-end">
              <input
                v-model="tenantIdInput"
                class="campo-input w-full"
                type="text"
                placeholder="Tenant ID da elaborare"
              />
              <BaseButton
                type="button"
                variant="secondary"
                :disabled="loadingTask"
                @click="avviaTaskReport"
              >
                {{ loadingTask ? "Report in esecuzione..." : "Avvia report asincrono" }}
              </BaseButton>
            </div>
          </div>

          <div class="mt-5 rounded-2xl border border-steel-200 bg-white p-4">
            <div class="mb-4 flex flex-wrap gap-3">
              <span class="rounded-full border border-steel-200 bg-steel-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-steel-700">
                Ruolo: {{ authStore.user?.role_code || "guest" }}
              </span>
              <span class="rounded-full border border-steel-200 bg-steel-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-steel-700">
                Permessi: {{ authStore.permissions.join(", ") || "nessuno" }}
              </span>
            </div>
            <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p class="text-[11px] font-semibold uppercase tracking-[0.2em] text-steel-400">
                  Stato task
                </p>
                <p class="mt-2 text-sm font-medium text-steel-900">
                  {{ taskStatus }}
                  <span v-if="taskId" class="text-steel-500">· {{ taskId }}</span>
                </p>
                <p class="mt-2 text-sm text-steel-700">{{ taskMessage }}</p>
              </div>
              <p class="text-2xl font-semibold text-brand-700">{{ taskProgress }}%</p>
            </div>

            <div class="mt-4 h-3 overflow-hidden rounded-full bg-steel-100">
              <div
                class="h-full rounded-full bg-[linear-gradient(90deg,#8c1d18_0%,#d2412e_100%)] transition-all duration-500"
                :style="{ width: `${taskProgress}%` }"
              />
            </div>

            <p v-if="resultUrl" class="mt-4 text-sm text-steel-700">
              File pronto: <span class="font-medium text-steel-900">{{ resultUrl }}</span>
            </p>
          </div>
        </div>
      </BaseCard>

      <BaseCard>
        <div class="flex flex-col gap-4 border-b border-steel-200 pb-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <SectionLabel>Filtro rapido</SectionLabel>
            <p class="mt-2 text-sm text-steel-700">
              {{ righeFiltraite.length }} document{{ righeFiltraite.length === 1 ? 'o' : 'i' }} trovati
            </p>
          </div>
          <div class="flex flex-wrap gap-3">
            <IconField :pt="ptIconField">
              <InputIcon :pt="ptInputIcon">
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="11" cy="11" r="8"/>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                </svg>
              </InputIcon>
              <InputText
                v-model="filtroTesto"
                placeholder="Cerca cliente o documento"
                :pt="ptInputText"
              />
            </IconField>
            <Select
              v-model="filtroTipo"
              :options="opzioniTipo"
              placeholder="Tipo documento"
              show-clear
              :pt="ptSelect"
            />
            <Select
              v-model="filtroStato"
              :options="opzioniStato"
              placeholder="Stato"
              show-clear
              :pt="{ ...ptSelect, root: { class: ptSelect.root.class + ' min-w-[116px]' } }"
            />
          </div>
        </div>

        <div class="mt-5 overflow-hidden rounded-2xl border border-steel-200">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-steel-200 bg-white text-sm">
              <thead class="bg-steel-100">
                <tr class="text-left text-[11px] font-semibold uppercase tracking-[0.18em] text-steel-400">
                  <th class="hidden px-4 py-3 md:table-cell">Data</th>
                  <th class="hidden px-4 py-3 sm:table-cell">Tipo</th>
                  <th class="px-4 py-3">Numero</th>
                  <th class="hidden px-4 py-3 md:table-cell">Cliente</th>
                  <th class="hidden px-4 py-3 lg:table-cell">Causale</th>
                  <th class="px-4 py-3">Importo</th>
                  <th class="px-4 py-3">Stato</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-steel-100">
                <tr
                  v-for="riga in righeFiltraite"
                  :key="`${riga.numero}-${riga.stato}`"
                  class="transition hover:bg-brand-50/55"
                >
                  <td class="hidden px-4 py-3 text-steel-700 md:table-cell">{{ riga.data }}</td>
                  <td class="hidden px-4 py-3 font-medium text-steel-900 sm:table-cell">{{ riga.tipo }}</td>
                  <td class="px-4 py-3 font-medium text-steel-900">{{ riga.numero }}</td>
                  <td class="hidden max-w-[160px] truncate px-4 py-3 text-steel-700 md:table-cell">{{ riga.cliente }}</td>
                  <td class="hidden max-w-[160px] truncate px-4 py-3 text-steel-700 lg:table-cell">{{ riga.causale }}</td>
                  <td class="px-4 py-3 text-steel-700">{{ riga.importo }}</td>
                  <td class="px-4 py-3">
                    <Tag :value="riga.stato" :pt="ptTagStato" />
                  </td>
                </tr>
                <tr v-if="righeFiltraite.length === 0">
                  <td colspan="7" class="px-4 py-8 text-center text-sm text-steel-400 italic">
                    Nessun documento corrisponde ai filtri applicati.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </BaseCard>
    </div>
</template>
