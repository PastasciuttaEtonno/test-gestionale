/**
 * Lettura dell'audit log nelle console admin: etichette degli eventi,
 * dettaglio ricavato dal payload ed export CSV.
 *
 * La categoria "sicurezza" raccoglie i segnali di un possibile attacco: sono
 * gli unici eventi che chiedono un intervento, quindi gli unici marcati in rosso.
 */

const EVENTI = {
  login_success: { etichetta: "Accesso", categoria: "accessi" },
  login_failed: { etichetta: "Accesso fallito", categoria: "accessi" },
  logout: { etichetta: "Uscita", categoria: "accessi" },
  token_refresh: { etichetta: "Sessione rinnovata", categoria: "accessi" },
  refresh_family_timeout: { etichetta: "Sessione scaduta", categoria: "accessi" },
  login_rate_limited: { etichetta: "Accessi bloccati per troppi tentativi", categoria: "sicurezza" },
  login_cooldown_active: { etichetta: "Accesso durante il blocco", categoria: "sicurezza" },
  access_denied: { etichetta: "Accesso negato", categoria: "sicurezza" },
  refresh_reuse_detected: { etichetta: "Riuso di un token revocato", categoria: "sicurezza" },
  refresh_family_revoked: { etichetta: "Sessioni revocate", categoria: "sicurezza" },
  password_breach_rejected: { etichetta: "Password compromessa rifiutata", categoria: "sicurezza" },
  password_breach_check_failed: { etichetta: "Controllo password non riuscito", categoria: "utenti" },
  user_created: { etichetta: "Utente creato", categoria: "utenti" },
  user_updated: { etichetta: "Utente modificato", categoria: "utenti" },
  user_status_changed: { etichetta: "Stato utente cambiato", categoria: "utenti" },
  user_role_changed: { etichetta: "Ruolo utente cambiato", categoria: "utenti" },
  production_order_updated: { etichetta: "Ordine di produzione aggiornato", categoria: "operazioni" },
};

export const CATEGORIE_EVENTO = [
  { label: "Accessi e sessioni", value: "accessi" },
  { label: "Sicurezza", value: "sicurezza" },
  { label: "Gestione utenti", value: "utenti" },
  { label: "Operazioni", value: "operazioni" },
];

const RUOLI = { admin: "Super Admin", tenant_admin: "Tenant Admin", user: "Utente" };

const fmtData = new Intl.DateTimeFormat("it-IT", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

export function infoEvento(eventType) {
  return EVENTI[eventType] ?? { etichetta: eventType, categoria: "operazioni" };
}

export function eAllarme(eventType) {
  return infoEvento(eventType).categoria === "sicurezza";
}

export function formattaData(iso) {
  return fmtData.format(new Date(iso));
}

// Per i login falliti su username inesistenti l'autore e' solo quanto digitato.
export function utenteEvento(evento) {
  return evento.username ?? evento.payload_json?.identificativo ?? "—";
}

function ruolo(codice) {
  return RUOLI[codice] ?? codice;
}

export function dettaglioEvento(evento) {
  const p = evento.payload_json ?? {};
  switch (evento.event_type) {
    case "user_created":
      return `Creato ${p.username_creato} (${ruolo(p.ruolo)})`;
    case "user_updated":
      return `Aggiornati i dati di ${p.username_target}`;
    case "user_status_changed":
      return `${p.username_target} ${p.stato_nuovo ? "riattivato" : "disattivato"}`;
    case "user_role_changed":
      return `${p.username_target}: da ${ruolo(p.ruolo_precedente)} a ${ruolo(p.ruolo_nuovo)}`;
    case "login_failed":
      return p.tentativi_falliti ? `Tentativo fallito n. ${p.tentativi_falliti}` : "";
    case "login_rate_limited":
      return p.bloccato_fino ? `Bloccato fino al ${formattaData(p.bloccato_fino)}` : "";
    case "refresh_family_revoked":
      return p.token_revocati ? `${p.token_revocati} token revocati` : "";
    case "password_breach_rejected":
      return `Password presente in ${p.breach_count} violazioni note`;
    case "production_order_updated":
      return `Ordine ${p.order_code}: ${p.status}`;
    default:
      return p.motivo ?? "";
  }
}

function cellaCsv(valore) {
  let testo = String(valore ?? "");
  // Excel esegue come formula una cella che inizia con = + - @, e l'identificativo
  // di un login fallito lo sceglie chiunque apra la pagina di accesso.
  if (/^[=+\-@\t\r]/.test(testo)) testo = `'${testo}`;
  return /[";\r\n]/.test(testo) ? `"${testo.replace(/"/g, '""')}"` : testo;
}

function scaricaCsv(nomeFile, intestazioni, righe) {
  // Separatore ";" come si aspetta Excel in italiano. Il BOM serve perche'
  // senza Excel legge il file come ANSI e rovina le lettere accentate.
  const corpo = [intestazioni, ...righe].map((r) => r.map(cellaCsv).join(";")).join("\r\n");
  const bom = String.fromCharCode(0xfeff);
  const url = URL.createObjectURL(new Blob([bom, corpo], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = nomeFile;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

export function esportaAuditCsv(nomeFile, eventi, { conTenant = false } = {}) {
  const intestazioni = [
    "Data e ora",
    "Utente",
    ...(conTenant ? ["Tenant"] : []),
    "Evento",
    "Dettaglio",
    "Codice evento",
    "Indirizzo IP",
  ];
  const righe = eventi.map((e) => [
    formattaData(e.created_at),
    utenteEvento(e),
    ...(conTenant ? [e.tenant_name ?? ""] : []),
    infoEvento(e.event_type).etichetta,
    dettaglioEvento(e),
    e.event_type,
    e.ip_address ?? "",
  ]);
  scaricaCsv(nomeFile, intestazioni, righe);
}
