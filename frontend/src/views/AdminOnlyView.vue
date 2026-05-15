<script setup>
import BaseButton from "../components/ui/BaseButton.vue";
import BaseCard from "../components/ui/BaseCard.vue";
import KpiTile from "../components/ui/KpiTile.vue";
import SectionLabel from "../components/ui/SectionLabel.vue";

const indicatoriSuperAdmin = [
  {
    label: "Tenants attivi",
    value: "38",
    note: "Aziende ceramiche e logistiche con servizio abilitato.",
  },
  {
    label: "Canoni in verifica",
    value: "5",
    note: "Tenant con rinnovo o sospensione da valutare.",
  },
  {
    label: "API request/min",
    value: "1.248",
    note: "Tra autenticazione, documenti e consultazione dati.",
  },
  {
    label: "Code Redis",
    value: "12",
    note: "Job pendenti per notifiche, export e processi batch.",
  },
];

const tenants = [
  {
    azienda: "Ceramiche Aurora S.p.A.",
    settore: "Ceramico",
    piano: "Enterprise",
    utenti: "42 / 60",
    db: "38.4 GB",
    scadenza: "30/06/2026",
    stato: "Attiva",
  },
  {
    azienda: "Logistica Tirrena S.r.l.",
    settore: "Logistica",
    piano: "Professional",
    utenti: "18 / 20",
    db: "12.7 GB",
    scadenza: "12/06/2026",
    stato: "Monitorare",
  },
  {
    azienda: "Edilceram Group",
    settore: "Ceramico",
    piano: "Enterprise",
    utenti: "57 / 80",
    db: "54.1 GB",
    scadenza: "08/07/2026",
    stato: "Attiva",
  },
  {
    azienda: "Trasporti Vela S.r.l.",
    settore: "Logistica",
    piano: "Starter",
    utenti: "9 / 10",
    db: "4.3 GB",
    scadenza: "28/05/2026",
    stato: "Bloccabile",
  },
];

const licenze = [
  {
    tenant: "Ceramiche Aurora S.p.A.",
    spazio: "38.4 / 60 GB",
    utenti: "42 / 60",
    scadenza: "30/06/2026",
    canone: "Regolare",
  },
  {
    tenant: "Logistica Tirrena S.r.l.",
    spazio: "12.7 / 15 GB",
    utenti: "18 / 20",
    scadenza: "12/06/2026",
    canone: "Da confermare",
  },
  {
    tenant: "Trasporti Vela S.r.l.",
    spazio: "4.3 / 5 GB",
    utenti: "9 / 10",
    scadenza: "28/05/2026",
    canone: "Scaduto",
  },
];

const health = [
  {
    titolo: "PostgreSQL",
    stato: "Operativo",
    dettaglio: "Replica logica allineata, storage al 68%.",
  },
  {
    titolo: "API Gateway",
    stato: "Operativo",
    dettaglio: "Tempo medio risposta 184 ms sulle ultime 5 min.",
  },
  {
    titolo: "Redis Queue",
    stato: "Da osservare",
    dettaglio: "12 job pendenti, 2 retry su export XML.",
  },
];

const auditGlobale = [
  {
    timestamp: "15/05/2026 14:21",
    operatore: "luca.assistenza",
    tenant: "Logistica Tirrena S.r.l.",
    evento: "Impersonation avviata",
    dettaglio: "Accesso di supporto richiesto per verifica bolla BL-2026-0441.",
  },
  {
    timestamp: "15/05/2026 13:48",
    operatore: "maria.operations",
    tenant: "Ceramiche Aurora S.p.A.",
    evento: "Tenant sospeso",
    dettaglio: "Blocco temporaneo accesso per canone insoluto.",
  },
  {
    timestamp: "15/05/2026 12:07",
    operatore: "admin.platform",
    tenant: "Edilceram Group",
    evento: "Piano aggiornato",
    dettaglio: "Aumento massimo utenti da 60 a 80.",
  },
];
</script>

<template>
  <section class="space-y-6">
    <BaseCard :highlight="true">
      <div class="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <SectionLabel>Livello 1</SectionLabel>
          <h2 class="mt-3 text-3xl font-semibold text-steel-900">
            Console Super Admin Esseduesoft
          </h2>
          <p class="mt-3 max-w-4xl text-sm leading-6 text-steel-700">
            Mockup enterprise per il personale Esseduesoft: gestione tenant,
            controllo licenze, osservabilita piattaforma e audit globale in ottica NIS2.
          </p>
        </div>

        <div class="flex flex-wrap gap-3">
          <BaseButton type="button" variant="secondary">Nuovo tenant</BaseButton>
          <BaseButton type="button" variant="secondary">Verifica licenze</BaseButton>
          <BaseButton type="button" variant="secondary">Apri audit globale</BaseButton>
        </div>
      </div>

      <div class="mt-6 grid gap-3 sm:gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KpiTile
          v-for="indicatore in indicatoriSuperAdmin"
          :key="indicatore.label"
          :label="indicatore.label"
          :value="indicatore.value"
          :note="indicatore.note"
        />
      </div>
    </BaseCard>

    <div class="grid gap-4 sm:gap-6 xl:grid-cols-[1.3fr_0.7fr]">
      <BaseCard>
        <div class="flex items-center justify-between gap-4">
          <div>
            <SectionLabel>Gestione tenants</SectionLabel>
            <h3 class="mt-2 text-xl font-semibold text-steel-900">
              Aziende clienti gestite
            </h3>
          </div>
          <BaseButton type="button" variant="secondary">Filtra tenants</BaseButton>
        </div>

        <div class="mt-5 overflow-hidden rounded-2xl border border-steel-200">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-steel-200 bg-white text-sm">
              <thead class="bg-steel-100">
                <tr class="text-left text-[11px] font-semibold uppercase tracking-[0.18em] text-steel-400">
                  <th class="px-4 py-3">Azienda</th>
                  <th class="hidden px-4 py-3 sm:table-cell">Settore</th>
                  <th class="hidden px-4 py-3 sm:table-cell">Piano</th>
                  <th class="hidden px-4 py-3 md:table-cell">Utenti</th>
                  <th class="hidden px-4 py-3 md:table-cell">DB</th>
                  <th class="hidden px-4 py-3 lg:table-cell">Scadenza</th>
                  <th class="px-4 py-3">Stato</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-steel-100">
                <tr
                  v-for="tenant in tenants"
                  :key="tenant.azienda"
                  class="transition hover:bg-brand-50/45"
                >
                  <td class="max-w-[160px] truncate px-4 py-3 font-medium text-steel-900">{{ tenant.azienda }}</td>
                  <td class="hidden px-4 py-3 text-steel-700 sm:table-cell">{{ tenant.settore }}</td>
                  <td class="hidden px-4 py-3 text-steel-700 sm:table-cell">{{ tenant.piano }}</td>
                  <td class="hidden px-4 py-3 text-steel-700 md:table-cell">{{ tenant.utenti }}</td>
                  <td class="hidden px-4 py-3 text-steel-700 md:table-cell">{{ tenant.db }}</td>
                  <td class="hidden px-4 py-3 text-steel-700 lg:table-cell">{{ tenant.scadenza }}</td>
                  <td class="px-4 py-3">
                    <span
                      class="inline-flex min-w-[104px] items-center justify-center rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-brand-700"
                    >
                      {{ tenant.stato }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </BaseCard>

      <div class="space-y-6">
        <BaseCard>
          <SectionLabel>Health e metriche</SectionLabel>
          <div class="mt-5 space-y-4">
            <div
              v-for="entry in health"
              :key="entry.titolo"
              class="rounded-2xl border border-steel-200 bg-steel-50 p-4"
            >
              <div class="flex items-center justify-between gap-4">
                <h3 class="text-sm font-semibold text-steel-900">{{ entry.titolo }}</h3>
                <span class="rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-brand-700">
                  {{ entry.stato }}
                </span>
              </div>
              <p class="mt-3 text-sm leading-6 text-steel-700">{{ entry.dettaglio }}</p>
            </div>
          </div>
        </BaseCard>

        <BaseCard>
          <SectionLabel>Licenze e piani</SectionLabel>
          <div class="mt-5 space-y-4">
            <div
              v-for="licenza in licenze"
              :key="licenza.tenant"
              class="rounded-2xl border border-steel-200 bg-white p-4"
            >
              <h3 class="text-sm font-semibold text-steel-900">{{ licenza.tenant }}</h3>
              <dl class="mt-3 grid gap-3 text-sm text-steel-700">
                <div class="flex items-center justify-between gap-4">
                  <dt>Spazio DB</dt>
                  <dd class="font-medium text-steel-900">{{ licenza.spazio }}</dd>
                </div>
                <div class="flex items-center justify-between gap-4">
                  <dt>Utenti massimi</dt>
                  <dd class="font-medium text-steel-900">{{ licenza.utenti }}</dd>
                </div>
                <div class="flex items-center justify-between gap-4">
                  <dt>Scadenza</dt>
                  <dd class="font-medium text-steel-900">{{ licenza.scadenza }}</dd>
                </div>
                <div class="flex items-center justify-between gap-4">
                  <dt>Canone</dt>
                  <dd class="font-medium text-brand-700">{{ licenza.canone }}</dd>
                </div>
              </dl>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>

    <BaseCard>
      <div class="flex items-center justify-between gap-4">
        <div>
          <SectionLabel>Audit globale NIS2</SectionLabel>
          <h3 class="mt-2 text-xl font-semibold text-steel-900">
            Tracciamento operazioni Esseduesoft
          </h3>
        </div>
        <BaseButton type="button" variant="secondary">Esporta log</BaseButton>
      </div>

      <div class="mt-5 overflow-hidden rounded-2xl border border-steel-200">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-steel-200 bg-white text-sm">
            <thead class="bg-steel-100">
              <tr class="text-left text-[11px] font-semibold uppercase tracking-[0.18em] text-steel-400">
                <th class="hidden px-4 py-3 sm:table-cell">Timestamp</th>
                <th class="px-4 py-3">Operatore</th>
                <th class="hidden px-4 py-3 md:table-cell">Tenant</th>
                <th class="px-4 py-3">Evento</th>
                <th class="hidden px-4 py-3 lg:table-cell">Dettaglio</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-steel-100">
              <tr
                v-for="entry in auditGlobale"
                :key="`${entry.timestamp}-${entry.operatore}`"
                class="transition hover:bg-brand-50/45"
              >
                <td class="hidden px-4 py-3 text-steel-700 sm:table-cell">{{ entry.timestamp }}</td>
                <td class="px-4 py-3 font-medium text-steel-900">{{ entry.operatore }}</td>
                <td class="hidden max-w-[140px] truncate px-4 py-3 text-steel-700 md:table-cell">{{ entry.tenant }}</td>
                <td class="px-4 py-3 text-steel-700">{{ entry.evento }}</td>
                <td class="hidden max-w-[180px] truncate px-4 py-3 text-steel-700 lg:table-cell">{{ entry.dettaglio }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </BaseCard>
  </section>
</template>
