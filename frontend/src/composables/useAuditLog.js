import { computed, onMounted, ref } from "vue";

import { esportaAuditCsv, infoEvento } from "../lib/audit";

export const LIMITE_AUDIT = 200;

/**
 * Stato condiviso dalle due console admin: carica gli ultimi eventi con la
 * funzione di servizio ricevuta, li filtra per categoria e li esporta in CSV.
 */
export function useAuditLog(recupera, { prefissoFile, conTenant = false }) {
  const eventi = ref([]);
  const caricamento = ref(true);
  const errore = ref(null);
  const filtroCategoria = ref(null);

  const eventiFiltrati = computed(() =>
    filtroCategoria.value
      ? eventi.value.filter((e) => infoEvento(e.event_type).categoria === filtroCategoria.value)
      : eventi.value,
  );

  const eventiOggi = computed(() => {
    const oggi = new Date().toDateString();
    return eventi.value.filter((e) => new Date(e.created_at).toDateString() === oggi).length;
  });

  async function carica() {
    caricamento.value = true;
    errore.value = null;
    try {
      const res = await recupera({ limit: LIMITE_AUDIT });
      eventi.value = res.items;
    } catch {
      eventi.value = [];
      errore.value = "Impossibile caricare l'audit log.";
    } finally {
      caricamento.value = false;
    }
  }

  function esporta() {
    const data = new Date().toISOString().slice(0, 10);
    esportaAuditCsv(`${prefissoFile}-${data}.csv`, eventiFiltrati.value, { conTenant });
  }

  onMounted(carica);

  return { eventi, eventiFiltrati, eventiOggi, caricamento, errore, filtroCategoria, esporta };
}
