<script setup>
import BaseButton from "../components/ui/BaseButton.vue";
import BaseCard from "../components/ui/BaseCard.vue";
import KpiTile from "../components/ui/KpiTile.vue";
import SectionLabel from "../components/ui/SectionLabel.vue";

const indicatoriTenantAdmin = [
  {
    label: "Utenti attivi",
    value: "26",
    note: "Dipendenti abilitati ai moduli aziendali.",
  },
  {
    label: "Ruoli configurati",
    value: "6",
    note: "Template interni tra magazzino, contabilita e back office.",
  },
  {
    label: "Sezionali attivi",
    value: "4",
    note: "Fatture, bolle, note e documenti interni.",
  },
  {
    label: "Eventi audit oggi",
    value: "39",
    note: "Login, export e modifiche a dati sensibili.",
  },
];

const utentiAzienda = [
  {
    nome: "Mario Conti",
    ruolo: "Magazzino",
    permessi: "Bolle lettura/scrittura",
    stato: "Attivo",
  },
  {
    nome: "Laura Neri",
    ruolo: "Amministrazione",
    permessi: "Fatture complete",
    stato: "Attivo",
  },
  {
    nome: "Paolo Serra",
    ruolo: "Commerciale",
    permessi: "Clienti e listini",
    stato: "Invito inviato",
  },
  {
    nome: "Giulia Ferretti",
    ruolo: "Back Office",
    permessi: "Anagrafiche e ordini",
    stato: "Attivo",
  },
];

const impostazioniAzienda = [
  {
    titolo: "Dati anagrafici aziendali",
    dettaglio: "P.IVA, sede legale, PEC, riferimenti amministrativi e recapiti operativi.",
  },
  {
    titolo: "Branding documentale",
    dettaglio: "Logo aziendale da applicare a fatture, bolle e documenti PDF esportati.",
  },
  {
    titolo: "SMTP aziendale",
    dettaglio: "Configurazione server email per invio fatture, notifiche e comunicazioni clienti.",
  },
];

const numerazioni = [
  {
    sezionale: "Fattura Elettronica 2026",
    prefisso: "FE",
    prossimoNumero: "000184",
    reset: "Annuale",
  },
  {
    sezionale: "Bolle Italia",
    prefisso: "BL",
    prossimoNumero: "004441",
    reset: "Continuo",
  },
  {
    sezionale: "Note di credito",
    prefisso: "NC",
    prossimoNumero: "000019",
    reset: "Annuale",
  },
];

const auditLocale = [
  {
    timestamp: "15/05/2026 14:52",
    utente: "Laura Neri",
    evento: "Export dati",
    dettaglio: "Esportazione elenco fatture clienti Q2 in XLSX.",
  },
  {
    timestamp: "15/05/2026 13:17",
    utente: "Mario Conti",
    evento: "Login",
    dettaglio: "Accesso da rete interna magazzino.",
  },
  {
    timestamp: "15/05/2026 12:08",
    utente: "Giulia Ferretti",
    evento: "Utente modificato",
    dettaglio: "Aggiornati permessi ruolo Back Office.",
  },
  {
    timestamp: "15/05/2026 09:41",
    utente: "Laura Neri",
    evento: "Numerazione aggiornata",
    dettaglio: "Confermato prossimo numero FE 2026.",
  },
];
</script>

<template>
  <section class="space-y-6">
    <BaseCard :highlight="true">
      <div class="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <SectionLabel>Livello 2</SectionLabel>
          <h2 class="mt-3 text-3xl font-semibold text-steel-900">
            Console Tenant Admin
          </h2>
          <p class="mt-3 max-w-4xl text-sm leading-6 text-steel-700">
            Mockup statico del responsabile IT aziendale: gestione utenti interni,
            impostazioni globali della propria azienda, numerazioni documentali e audit locale.
          </p>
        </div>

        <div class="flex flex-wrap gap-3">
          <BaseButton type="button" variant="secondary">Invita utente</BaseButton>
          <BaseButton type="button" variant="secondary">Configura SMTP</BaseButton>
          <BaseButton type="button" variant="secondary">Esporta audit</BaseButton>
        </div>
      </div>

      <div class="mt-8 grid gap-4 md:grid-cols-2 2xl:grid-cols-4">
        <KpiTile
          v-for="indicatore in indicatoriTenantAdmin"
          :key="indicatore.label"
          :label="indicatore.label"
          :value="indicatore.value"
          :note="indicatore.note"
        />
      </div>
    </BaseCard>

    <div class="grid gap-6 2xl:grid-cols-[1.15fr_0.85fr]">
      <BaseCard>
        <div class="flex items-center justify-between gap-4">
          <div>
            <SectionLabel>Utenti e RBAC</SectionLabel>
            <h3 class="mt-2 text-xl font-semibold text-steel-900">
              Permessi e dipendenti aziendali
            </h3>
          </div>
          <BaseButton type="button" variant="secondary">Nuovo ruolo</BaseButton>
        </div>

        <div class="mt-5 overflow-hidden rounded-2xl border border-steel-200">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-steel-200 bg-white text-sm">
              <thead class="bg-steel-100">
                <tr class="text-left text-[11px] font-semibold uppercase tracking-[0.18em] text-steel-400">
                  <th class="px-4 py-3">Utente</th>
                  <th class="px-4 py-3">Ruolo</th>
                  <th class="px-4 py-3">Permessi</th>
                  <th class="px-4 py-3">Stato</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-steel-100">
                <tr
                  v-for="utente in utentiAzienda"
                  :key="utente.nome"
                  class="transition hover:bg-brand-50/45"
                >
                  <td class="px-4 py-3 font-medium text-steel-900">{{ utente.nome }}</td>
                  <td class="px-4 py-3 text-steel-700">{{ utente.ruolo }}</td>
                  <td class="px-4 py-3 text-steel-700">{{ utente.permessi }}</td>
                  <td class="px-4 py-3">
                    <span
                      class="inline-flex min-w-[112px] items-center justify-center rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-brand-700"
                    >
                      {{ utente.stato }}
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
          <SectionLabel>Impostazioni globali</SectionLabel>
          <div class="mt-5 space-y-4">
            <div
              v-for="entry in impostazioniAzienda"
              :key="entry.titolo"
              class="rounded-2xl border border-steel-200 bg-steel-50 p-4"
            >
              <h3 class="text-sm font-semibold text-steel-900">{{ entry.titolo }}</h3>
              <p class="mt-3 text-sm leading-6 text-steel-700">{{ entry.dettaglio }}</p>
            </div>
          </div>
        </BaseCard>

        <BaseCard>
          <SectionLabel>Numerazioni e sezionali</SectionLabel>
          <div class="mt-5 space-y-4">
            <div
              v-for="entry in numerazioni"
              :key="entry.sezionale"
              class="rounded-2xl border border-steel-200 bg-white p-4"
            >
              <h3 class="text-sm font-semibold text-steel-900">{{ entry.sezionale }}</h3>
              <dl class="mt-3 grid gap-3 text-sm text-steel-700">
                <div class="flex items-center justify-between gap-4">
                  <dt>Prefisso</dt>
                  <dd class="font-medium text-steel-900">{{ entry.prefisso }}</dd>
                </div>
                <div class="flex items-center justify-between gap-4">
                  <dt>Prossimo numero</dt>
                  <dd class="font-medium text-steel-900">{{ entry.prossimoNumero }}</dd>
                </div>
                <div class="flex items-center justify-between gap-4">
                  <dt>Reset</dt>
                  <dd class="font-medium text-steel-900">{{ entry.reset }}</dd>
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
          <SectionLabel>Audit locale</SectionLabel>
          <h3 class="mt-2 text-xl font-semibold text-steel-900">
            Eventi dipendenti e azioni sensibili
          </h3>
        </div>
        <BaseButton type="button" variant="secondary">Filtra eventi</BaseButton>
      </div>

      <div class="mt-5 overflow-hidden rounded-2xl border border-steel-200">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-steel-200 bg-white text-sm">
            <thead class="bg-steel-100">
              <tr class="text-left text-[11px] font-semibold uppercase tracking-[0.18em] text-steel-400">
                <th class="px-4 py-3">Timestamp</th>
                <th class="px-4 py-3">Utente</th>
                <th class="px-4 py-3">Evento</th>
                <th class="px-4 py-3">Dettaglio</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-steel-100">
              <tr
                v-for="entry in auditLocale"
                :key="`${entry.timestamp}-${entry.utente}`"
                class="transition hover:bg-brand-50/45"
              >
                <td class="px-4 py-3 text-steel-700">{{ entry.timestamp }}</td>
                <td class="px-4 py-3 font-medium text-steel-900">{{ entry.utente }}</td>
                <td class="px-4 py-3 text-steel-700">{{ entry.evento }}</td>
                <td class="px-4 py-3 text-steel-700">{{ entry.dettaglio }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </BaseCard>
  </section>
</template>
