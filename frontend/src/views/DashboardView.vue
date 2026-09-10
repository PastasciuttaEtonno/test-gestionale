<script setup>
import { computed, ref, watch } from "vue";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import BaseButton from "../components/ui/BaseButton.vue";
import BaseCard from "../components/ui/BaseCard.vue";
import KpiTile from "../components/ui/KpiTile.vue";
import SectionLabel from "../components/ui/SectionLabel.vue";
import { useAuthStore } from "../stores/auth";
import { useDashboardStore } from "../stores/dashboard";
import { useTasksStore } from "../stores/tasks";
import { avviaGenerazioneReport } from "../services/reports";
import { ptIconField, ptInputIcon, makePtInputText, makePtSelect } from "../lib/prime-pt";
import { stileStato } from "../lib/stato";
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

const azioniRapide = [
  "Nuova fattura",
  "Nuova bolla",
  "Apri cliente",
  "Cerca documento",
];

// Il report gira sempre sull'azienda dell'utente collegato.
const tenantId = computed(() => authStore.user?.tenant_id || "");
const taskId = ref("");
const erroreTask = ref("");
const loadingTask = ref(false);

// I codici permesso ("anagrafiche.write") sono nomi interni. A schermo
// serve l'area di lavoro, non la stringa con cui il backend la identifica.
const AREE = {
  anagrafiche: "Anagrafiche",
  articoli: "Articoli",
  bolle: "Bolle",
  bom: "Distinte base",
  finance: "Costi",
};

const areeConsentite = computed(() => {
  const viste = new Map();
  for (const permesso of authStore.permissions) {
    const [area, azione] = permesso.split(".");
    const nome = AREE[area];
    if (!nome) continue;
    viste.set(nome, viste.get(nome) || azione === "write");
  }
  return [...viste].map(([nome, scrittura]) =>
    scrittura ? nome : `${nome} (sola lettura)`,
  );
});

const taskState = computed(() =>
  taskId.value ? tasksStore.getTask(taskId.value) : null,
);
// Gli stati che arrivano da Celery sono nomi tecnici.
const ETICHETTA_TASK = {
  idle: "Non avviato",
  pending: "In coda",
  progress: "In corso",
  success: "Completato",
  failure: "Non riuscito",
};

const taskStatus = computed(() => taskState.value?.status || "idle");
const taskProgress = computed(() => taskState.value?.progress || 0);
const taskMessage = computed(
  () => taskState.value?.message || "Nessun report avviato.",
);
const resultUrl = computed(() => taskState.value?.resultUrl || "");

watch(taskStatus, (status) => {
  if (["success", "failure"].includes(status)) {
    loadingTask.value = false;
  }
});

async function avviaTaskReport() {
  erroreTask.value = "";

  // Un utente admin non e' legato a nessuna azienda: senza questo messaggio
  // il click uscirebbe in silenzio proprio per chi ha i permessi per avviarlo.
  if (!tenantId.value) {
    erroreTask.value =
      "Questo utente non è associato a nessuna azienda, quindi il report non può partire. Accedi con un utente aziendale.";
    return;
  }

  loadingTask.value = true;

  try {
    const response = await avviaGenerazioneReport({
      tenant_id: tenantId.value,
    });
    taskId.value = response.task_id;
    tasksStore.initTask(response.task_id);
  } catch (error) {
    loadingTask.value = false;
    taskId.value = "";
    erroreTask.value =
      error?.response?.data?.detail ||
      "Avvio del report non riuscito. Riprova fra qualche istante.";
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
            <SectionLabel>Documenti</SectionLabel>
            <h2 class="mt-3 text-2xl font-semibold text-steel-900 sm:text-3xl">
              Vista elenco documenti
            </h2>
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

        <!-- KPI reali tenant-aware (aggiornati via SSE) -->
        <div
          v-if="dashboardStore.kpis"
          class="mt-6 rounded-[1.5rem] border border-steel-200 bg-white p-5"
        >
          <div class="mb-4 flex items-center justify-between">
            <SectionLabel>La tua azienda</SectionLabel>
            <span
              v-if="dashboardStore.lastUpdated"
              class="text-[11px] text-steel-600"
            >
              Aggiornato {{ dashboardStore.lastUpdated.toLocaleTimeString("it-IT") }}
            </span>
          </div>
          <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
            <KpiTile label="Utenti totali" :value="String(dashboardStore.kpis.total_users)" note="Utenti dell'azienda." />
            <KpiTile label="Utenti attivi" :value="String(dashboardStore.kpis.active_users)" note="Account attivi." />
            <KpiTile label="Operazioni 24h" :value="String(dashboardStore.kpis.audit_events_last_24h)" note="Operazioni nelle ultime 24 ore." />
            <KpiTile label="Profilo azienda" :value="dashboardStore.kpis.company_profile_configured ? 'Configurato' : 'Mancante'" note="Dati aziendali." />
            <KpiTile label="SMTP" :value="dashboardStore.kpis.smtp_configured ? 'Configurato' : 'Non configurato'" note="Impostazioni email." />
          </div>
        </div>

        <div class="mt-8 rounded-[1.5rem] border border-steel-200 bg-steel-50/80 p-5">
          <div class="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
            <div class="max-w-2xl">
              <SectionLabel>Report periodico</SectionLabel>
              <h3 class="mt-3 text-2xl font-semibold text-steel-900">
                Generazione report in background
              </h3>
              <p class="mt-3 text-sm leading-6 text-steel-700">
                Il report viene elaborato dal server: puoi continuare a lavorare
                mentre procede, e l'avanzamento si aggiorna da solo. Richiede
                circa dieci secondi.
              </p>
              <p class="mt-2 text-sm leading-6 text-steel-600">
                Funziona anche in modalità demo, perché il report si limita a
                leggere i dati.
              </p>
            </div>

            <div class="flex w-full max-w-xl flex-col gap-3 xl:items-end">
              <BaseButton
                type="button"
                variant="secondary"
                :disabled="loadingTask"
                @click="avviaTaskReport"
              >
                {{ loadingTask ? "Report in corso…" : "Avvia il report" }}
              </BaseButton>
              <p
                v-if="erroreTask"
                class="text-sm font-medium text-red-700 xl:text-right"
                role="alert"
              >
                {{ erroreTask }}
              </p>
            </div>
          </div>

          <div class="mt-5 rounded-2xl border border-steel-200 bg-white p-4">
            <div class="mb-4 flex flex-wrap gap-3">
              <span class="rounded-full border border-steel-200 bg-steel-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-steel-700">
                Ruolo: {{ authStore.user?.role_code || "guest" }}
              </span>
              <span
                v-for="area in areeConsentite"
                :key="area"
                class="rounded-full border border-steel-200 bg-steel-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-steel-700"
              >
                {{ area }}
              </span>
            </div>
            <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p class="etichetta-dato">Stato</p>
                <p class="mt-2 text-sm font-medium text-steel-900">
                  {{ ETICHETTA_TASK[taskStatus] ?? taskStatus }}
                  
                </p>
                <p class="mt-2 text-sm text-steel-700">{{ taskMessage }}</p>
              </div>
              <p class="text-2xl font-semibold text-brand-700">{{ taskProgress }}%</p>
            </div>

            <div class="mt-4 h-3 overflow-hidden rounded-full bg-steel-100">
              <div
                class="h-full rounded-full bg-brand-500 transition-all duration-500"
                :style="{ width: `${taskProgress}%` }"
              />
            </div>

            <p v-if="resultUrl" class="mt-4 text-sm text-steel-700">
              File generato:
              <span class="font-medium text-steel-900">{{ resultUrl }}</span>
              <span class="mt-1 block text-xs text-steel-600">
                In questa demo il file non è scaricabile: l'elaborazione arriva
                fino in fondo, ma non produce un allegato.
              </span>
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
                aria-label="Cerca per cliente o numero documento"
                :pt="ptInputText"
              />
            </IconField>
            <Select
              v-model="filtroTipo"
              :options="opzioniTipo"
              placeholder="Tipo documento"
              aria-label="Filtra per tipo documento"
              show-clear
              :pt="ptSelect"
            />
            <Select
              v-model="filtroStato"
              :options="opzioniStato"
              placeholder="Stato"
              aria-label="Filtra per stato"
              show-clear
              :pt="{ ...ptSelect, root: { class: ptSelect.root.class + ' min-w-[116px]' } }"
            />
          </div>
        </div>

        <div class="mt-5 overflow-hidden rounded-2xl border border-steel-200">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-steel-200 bg-white text-sm">
                <caption class="sr-only">Documenti recenti: data, tipo, numero, cliente, causale, importo e stato.</caption>
              <thead class="bg-steel-100">
                <tr class="text-left intestazione-tabella">
                  <th scope="col" class="hidden px-4 py-3 md:table-cell">Data</th>
                  <th scope="col" class="hidden px-4 py-3 sm:table-cell">Tipo</th>
                  <th scope="col" class="px-4 py-3">Numero</th>
                  <th scope="col" class="hidden px-4 py-3 md:table-cell">Cliente</th>
                  <th scope="col" class="hidden px-4 py-3 lg:table-cell">Causale</th>
                  <th scope="col" class="px-4 py-3">Importo</th>
                  <th scope="col" class="px-4 py-3">Stato</th>
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
                  <td class="px-4 py-3 cifre text-steel-700">{{ riga.importo }}</td>
                  <td class="px-4 py-3">
                    <span class="min-w-[120px]" :class="stileStato(riga.stato).classe">
                      <span aria-hidden="true">{{ stileStato(riga.stato).glifo }}</span>
                      {{ riga.stato }}
                    </span>
                  </td>
                </tr>
                <tr v-if="righeFiltraite.length === 0">
                  <td colspan="7" class="px-4 py-8 text-center text-sm text-steel-600 italic">
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
