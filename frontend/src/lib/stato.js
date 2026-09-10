/**
 * Scala di stato unica dell'applicazione.
 *
 * Nel gestionale il colore dice una cosa sola: a che punto e' il documento.
 * Il rosso brand resta il segno di penna, quindi marca gli stati che
 * richiedono un intervento, non tutti gli stati indistintamente.
 *
 * Ogni grado porta anche un glifo di forma diversa, cosi' lo stato resta
 * leggibile in bianco e nero e per chi non distingue i rossi.
 */

export const GRADI = {
  attesa: { classe: "tag-stato tag-stato-attesa", glifo: "○" },
  corso: { classe: "tag-stato tag-stato-corso", glifo: "◐" },
  chiuso: { classe: "tag-stato tag-stato-chiuso", glifo: "●" },
  azione: { classe: "tag-stato tag-stato-azione", glifo: "▲" },
};

// Ogni stato che l'applicazione sa mostrare, normalizzato a minuscolo.
// Aggiungere qui i nuovi stati: le viste non ridefiniscono la palette.
const MAPPA = {
  // Nulla da fare adesso.
  bozza: "attesa",
  annullata: "attesa",
  disattivato: "attesa",
  // Pratica avviata, in corso.
  aperta: "corso",
  confermata: "corso",
  "in lavorazione": "corso",
  // Conclusa.
  emessa: "chiuso",
  attivo: "chiuso",
  configurato: "chiuso",
  // Richiede un intervento dell'operatore.
  "da inviare": "azione",
  "da chiudere": "azione",
  incompleta: "azione",
  "non configurato": "azione",
};

export function gradoStato(stato) {
  return MAPPA[String(stato ?? "").trim().toLowerCase()] ?? "attesa";
}

export function stileStato(stato) {
  return GRADI[gradoStato(stato)];
}
