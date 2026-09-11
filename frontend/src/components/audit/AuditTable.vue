<script setup>
import { dettaglioEvento, eAllarme, formattaData, infoEvento, utenteEvento } from "../../lib/audit";
import { GRADI } from "../../lib/stato";

defineProps({
  eventi: { type: Array, required: true },
  caricamento: { type: Boolean, default: false },
  errore: { type: String, default: null },
  conTenant: { type: Boolean, default: false },
  filtrato: { type: Boolean, default: false },
});
</script>

<template>
  <p
    v-if="errore"
    role="alert"
    class="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
  >
    {{ errore }}
  </p>

  <div v-else-if="caricamento" class="mt-5 space-y-3" aria-busy="true">
    <div v-for="n in 4" :key="n" class="h-12 animate-pulse rounded-xl bg-steel-100" />
  </div>

  <p
    v-else-if="!eventi.length"
    class="mt-5 rounded-2xl border border-steel-200 bg-steel-50 px-4 py-8 text-center text-sm text-steel-700"
  >
    {{ filtrato ? "Nessun evento in questa categoria." : "Nessun evento registrato." }}
  </p>

  <div v-else class="mt-5 overflow-hidden rounded-2xl border border-steel-200">
    <div class="max-h-[32rem] overflow-auto">
      <table class="min-w-full divide-y divide-steel-200 bg-white text-sm">
        <caption class="sr-only">
          Eventi di audit dal piu' recente: data, utente{{ conTenant ? ", tenant" : "" }}, evento e dettaglio.
        </caption>
        <thead class="sticky top-0 bg-steel-100">
          <tr class="text-left intestazione-tabella">
            <th scope="col" class="hidden px-4 py-3 sm:table-cell">Data e ora</th>
            <th scope="col" class="px-4 py-3">Utente</th>
            <th v-if="conTenant" scope="col" class="hidden px-4 py-3 md:table-cell">Tenant</th>
            <th scope="col" class="px-4 py-3">Evento</th>
            <th scope="col" class="hidden px-4 py-3 lg:table-cell">Dettaglio</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-steel-100">
          <tr v-for="evento in eventi" :key="evento.id" class="transition hover:bg-brand-50/45">
            <td class="hidden whitespace-nowrap px-4 py-3 cifre text-steel-700 sm:table-cell">
              {{ formattaData(evento.created_at) }}
            </td>
            <td class="max-w-[160px] truncate px-4 py-3 font-medium text-steel-900">
              {{ utenteEvento(evento) }}
            </td>
            <td v-if="conTenant" class="hidden max-w-[160px] truncate px-4 py-3 text-steel-700 md:table-cell">
              {{ evento.tenant_name ?? "—" }}
            </td>
            <td class="px-4 py-3 text-steel-700">
              <span v-if="eAllarme(evento.event_type)" :class="GRADI.azione.classe">
                <span aria-hidden="true">{{ GRADI.azione.glifo }}</span>
                {{ infoEvento(evento.event_type).etichetta }}
              </span>
              <template v-else>{{ infoEvento(evento.event_type).etichetta }}</template>
            </td>
            <td
              class="hidden max-w-[240px] truncate px-4 py-3 text-steel-700 lg:table-cell"
              :title="dettaglioEvento(evento)"
            >
              {{ dettaglioEvento(evento) || "—" }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
