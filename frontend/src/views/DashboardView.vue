<script setup>
import { onBeforeUnmount, ref } from "vue";

import BaseButton from "../components/ui/BaseButton.vue";
import BaseCard from "../components/ui/BaseCard.vue";
import KpiTile from "../components/ui/KpiTile.vue";
import SectionLabel from "../components/ui/SectionLabel.vue";
import SidebarSection from "../components/ui/SidebarSection.vue";
import { useAuthStore } from "../stores/auth";
import { avviaGenerazioneReport, recuperaStatoTask } from "../services/reports";

const authStore = useAuthStore();

const vociSidebar = [
  {
    gruppo: "Operativita",
    items: ["Dashboard", "Clienti", "Articoli", "Bolle", "Fatture", "Spedizioni"],
  },
  {
    gruppo: "Consultazione",
    items: ["Scadenze", "Listini", "Movimenti", "Archivio documenti"],
  },
];

const voceAttivaSidebar = "Bolle";

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
const taskStatus = ref("idle");
const taskMessage = ref("Nessun report asincrono avviato.");
const taskProgress = ref(0);
const resultUrl = ref("");
const loadingTask = ref(false);

let pollingId = null;

function fermaPolling() {
  if (pollingId) {
    window.clearInterval(pollingId);
    pollingId = null;
  }
}

async function aggiornaStatoTask() {
  if (!taskId.value) {
    return;
  }

  const stato = await recuperaStatoTask(taskId.value);
  taskStatus.value = stato.status;
  taskMessage.value = stato.message;
  taskProgress.value = stato.progress;
  resultUrl.value = stato.result_url || "";

  if (["success", "failure"].includes(stato.status)) {
    loadingTask.value = false;
    fermaPolling();
  }
}

async function avviaTaskReport() {
  if (!tenantIdInput.value) {
    taskStatus.value = "failure";
    taskMessage.value = "Inserire un tenant_id valido prima di avviare il report.";
    return;
  }

  fermaPolling();
  loadingTask.value = true;
  taskProgress.value = 0;
  resultUrl.value = "";
  taskStatus.value = "pending";
  taskMessage.value = "Accodamento task in corso.";

  try {
    const response = await avviaGenerazioneReport({
      tenant_id: tenantIdInput.value,
    });
    taskId.value = response.task_id;
    taskStatus.value = "accepted";
    taskMessage.value = response.message;
    await aggiornaStatoTask();
    pollingId = window.setInterval(() => {
      aggiornaStatoTask().catch((error) => {
        loadingTask.value = false;
        taskStatus.value = "failure";
        taskMessage.value =
          error?.response?.data?.detail || "Polling task non riuscito.";
        fermaPolling();
      });
    }, 2000);
  } catch (error) {
    loadingTask.value = false;
    taskStatus.value = "failure";
    taskMessage.value =
      error?.response?.data?.detail || "Accodamento report non riuscito.";
  }
}

onBeforeUnmount(() => {
  fermaPolling();
});

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
</script>

<template>
  <div class="grid gap-6 xl:grid-cols-[248px_minmax(0,1fr)]">
    <aside class="rounded-[1.75rem] border border-steel-200 bg-[#232a31] p-4 text-white shadow-panel">
      <div class="rounded-2xl border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.08)_0%,rgba(255,255,255,0.03)_100%)] px-4 py-4">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-500 text-xs font-semibold uppercase tracking-[0.2em] text-white">
            OP
          </div>
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-[0.28em] text-brand-100">
              Menu operativo
            </p>
            <p class="mt-1 text-sm font-medium text-white">Workspace standard</p>
          </div>
        </div>
        <p class="mt-3 text-sm leading-6 text-white/74">
          Navigazione laterale pensata per utenti standard del gestionale.
        </p>
      </div>

      <div class="mt-6 space-y-5">
        <SidebarSection
          v-for="sezione in vociSidebar"
          :key="sezione.gruppo"
          :title="sezione.gruppo"
          :items="sezione.items"
          :active-item="voceAttivaSidebar"
        />
      </div>

      <div class="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4">
        <p class="text-[11px] font-semibold uppercase tracking-[0.24em] text-white/42">
          Attenzione
        </p>
        <p class="mt-2 text-sm font-medium text-white">4 anagrafiche incomplete</p>
        <p class="mt-2 text-sm leading-6 text-white/68">
          Verificare indirizzi di consegna e dati fiscali prima della prossima emissione.
        </p>
      </div>
    </aside>

    <div class="space-y-6">
      <BaseCard :highlight="true">
        <div class="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
          <div>
            <SectionLabel>Workspace standard</SectionLabel>
            <h2 class="mt-3 text-3xl font-semibold text-steel-900">
              Vista elenco documenti
            </h2>
            <p class="mt-3 max-w-3xl text-sm leading-6 text-steel-700">
              Mockup statico di una home ERP enterprise con sidebar, toolbar e griglia
              dati densa. Serve solo a validare ingombri, gerarchia visiva e leggibilita.
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

        <div class="mt-8 grid gap-4 md:grid-cols-2 2xl:grid-cols-4">
          <KpiTile
            v-for="indicatore in indicatori"
            :key="indicatore.label"
            :label="indicatore.label"
            :value="indicatore.value"
            :note="indicatore.note"
          />
        </div>

        <div class="mt-8 rounded-[1.5rem] border border-steel-200 bg-steel-50/80 p-5">
          <div class="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
            <div class="max-w-2xl">
              <SectionLabel>Async Queue Demo</SectionLabel>
              <h3 class="mt-3 text-2xl font-semibold text-steel-900">
                Generazione report con Celery e Redis
              </h3>
              <p class="mt-3 text-sm leading-6 text-steel-700">
                Questo blocco dimostra il flusso `POST /reports/generate` seguito
                dal polling leggero su `GET /tasks/{taskId}/status`.
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
              Cliente: Tutti · Stato: Aperto/Bozza · Periodo: Ultimi 15 giorni
            </p>
          </div>
          <div class="flex flex-wrap gap-3">
            <div class="flex h-11 min-w-[160px] items-center rounded-xl border border-steel-200 bg-steel-50 px-4 text-sm text-steel-700">
              Cerca cliente o documento
            </div>
            <div class="flex h-11 min-w-[132px] items-center rounded-xl border border-steel-200 bg-steel-50 px-4 text-sm text-steel-700">
              Tipo documento
            </div>
            <div class="flex h-11 min-w-[116px] items-center rounded-xl border border-steel-200 bg-steel-50 px-4 text-sm text-steel-700">
              Stato
            </div>
          </div>
        </div>

        <div class="mt-5 overflow-hidden rounded-2xl border border-steel-200">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-steel-200 bg-white text-sm">
              <thead class="bg-steel-100">
                <tr class="text-left text-[11px] font-semibold uppercase tracking-[0.18em] text-steel-400">
                  <th class="px-4 py-3">Data</th>
                  <th class="px-4 py-3">Tipo</th>
                  <th class="px-4 py-3">Numero</th>
                  <th class="px-4 py-3">Cliente</th>
                  <th class="px-4 py-3">Causale</th>
                  <th class="px-4 py-3">Importo</th>
                  <th class="px-4 py-3">Stato</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-steel-100">
                <tr
                  v-for="riga in righeDocumenti"
                  :key="`${riga.numero}-${riga.stato}`"
                  class="transition hover:bg-brand-50/55"
                >
                  <td class="px-4 py-3 text-steel-700">{{ riga.data }}</td>
                  <td class="px-4 py-3 font-medium text-steel-900">{{ riga.tipo }}</td>
                  <td class="px-4 py-3 font-medium text-steel-900">{{ riga.numero }}</td>
                  <td class="px-4 py-3 text-steel-700">{{ riga.cliente }}</td>
                  <td class="px-4 py-3 text-steel-700">{{ riga.causale }}</td>
                  <td class="px-4 py-3 text-steel-700">{{ riga.importo }}</td>
                  <td class="px-4 py-3">
                    <span
                      class="inline-flex min-w-[108px] items-center justify-center rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-brand-700"
                    >
                      {{ riga.stato }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </BaseCard>
    </div>
  </div>
</template>
