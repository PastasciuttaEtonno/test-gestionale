# Frontend Auth Test Client

## Struttura

- `frontend/src/components/layout/AppShell.vue`: shell condivisa — header responsive, burger, Avatar PrimeVue, Tooltip
- `frontend/src/components/ui/`: componenti base riusabili del design system
- `frontend/src/composables/useSidebar.js`: stato reattivo module-level del drawer mobile
- `frontend/src/router/index.js`: definizione rotte e guardie
- `frontend/src/stores/auth.js`: stato sessione in memoria
- `frontend/src/lib/http.js`: istanza `axios` con interceptor request/response
- `frontend/src/services/auth.js`: funzioni API del modulo auth/admin
- `frontend/src/views/LoginView.vue`: login enterprise, toggle password nativo
- `frontend/src/views/DashboardView.vue`: mockup ERP con filtri reali (InputText + Select)
- `frontend/src/views/TenantAdminView.vue`: console `Tenant Admin` con Tag status-aware
- `frontend/src/views/AdminOnlyView.vue`: console `Super Admin` con ProgressBar e Tag

## Flusso di autenticazione

1. Il form login invia `identifier` e `password` a `POST /api/v1/auth/login`.
2. Il backend restituisce `access_token`, `token_type` e `user`, e imposta il `refresh_token` in cookie `HttpOnly`.
3. Il frontend mantiene solo `access_token` e `user` in memoria.
4. Ogni richiesta API protetta allega il bearer token con un interceptor Axios.
5. All'avvio dell'app il client tenta `POST /api/v1/auth/refresh` per ripristinare la sessione dal cookie.
6. In caso di `401`, il client tenta una sola volta `POST /api/v1/auth/refresh`.
7. Se il refresh fallisce, la sessione locale viene rimossa e l'utente deve rieseguire il login.

## Rotte

- `/login`: accesso guest only
- `/dashboard`: accesso autenticato, scaffold statico standard-user
- `/tenant-admin`: accesso autenticato con metadato `requiredRoles: ['tenant_admin']`
- `/admin-only`: accesso autenticato con metadato `requiredRoles: ['admin']`
- `/:pathMatch(.*)*`: pagina `404 Not Found` per URL non riconosciuti

## Visibilita ruoli

- l'utente senza `requiredRoles` validi viene reindirizzato fuori dalla rotta
- la shell legge ruolo e permessi dallo store `Pinia`, non da controlli hardcoded sparsi nelle viste
- la home gestionale di base resta identica tra utente operativo e admin

## Mockup standard-user

La vista `/dashboard` corrente:

- usa dati dummy definiti localmente nello `script setup`
- include filtri funzionanti: testo libero (cliente o numero documento), tipo (Fattura/Bolla), stato
- filtro realizzato con `computed righeFiltraite` — no fetch API
- riga vuota con messaggio se nessun risultato corrisponde
- tabella con column hiding responsive (`hidden md:table-cell` ecc.)
- stato documento mostrato con `Tag` PrimeVue

## Mockup Super Admin

La vista `/admin-only` corrente:

- dedicata al personale Gestionale
- modella tenants, licenze, health e audit globale con dati dummy
- status critici ("Bloccabile", "Scaduto", "Da osservare") mostrati con `Tag` rossa solida
- utilizzo risorse DB e utenti mostrato con `ProgressBar` PrimeVue nelle card licenze
- non usa ancora dati reali o logica di impersonation effettiva

## Mockup Tenant Admin

La vista `/tenant-admin` corrente:

- modella utenti interni, RBAC, impostazioni globali aziendali, numerazioni e audit locale
- stato utenti mostrato con `Tag` PrimeVue ("Invito inviato" riceve stile accent)
- visibile solo al ruolo reale `tenant_admin`
- non accessibile al `Super Admin`

## Responsive

Il frontend è mobile-first (375px → desktop):

- sidebar off-canvas su `< xl`, statica su `≥ xl`
- stato drawer condiviso tramite `useSidebar.js` (module-level reactive — no Pinia)
- overlay scrim con `<Transition name="fade">` al click chiude il drawer
- tabelle con column hiding (`hidden {breakpoint}:table-cell`) — no `overflow-x-auto` come unica strategia
- griglia KPI: `grid-cols-1 → md:grid-cols-2 → xl:grid-cols-4`
- padding header e card ridotto su mobile, standard da `sm+`

Spec complete: `planning/docs/responsive/00-responsive-guidelines.md`

## PrimeVue v4 — componenti attivi

PrimeVue è usato con `unstyled: true`. Ogni componente è stilizzato tramite PT (Pass-Through) con classi Tailwind del progetto. Il preset ufficiale `primevue/passthrough/tailwind` **non viene usato** (è per Tailwind v3).

| Componente | Dove usato |
|---|---|
| `Tooltip` | AppShell (burger, logout) — configurato globalmente in `main.js` |
| `Avatar` | AppShell — iniziale username con `bg-brand-500` |
| `IconField` + `InputIcon` + `InputText` | DashboardView — campo ricerca documenti |
| `Select` | DashboardView — filtri tipo e stato con `show-clear` |
| `Tag` | DashboardView, AdminOnlyView, TenantAdminView — badge stato |
| `ProgressBar` | AdminOnlyView — utilizzo DB e utenti per licenza |

## Limiti intenzionali della fase

- nessun form business
- nessuna gestione multi-tab sofisticata
- nessuna UI per revoca sessioni
- `Pinia` usata solo per sessione auth e permessi correnti
- l'autorizzazione reale resta del backend: il router blocca UX, non sostituisce il controllo server-side

## Regola di evoluzione UI

Quando una nuova vista richiede un pattern ripetibile:

1. creare o aggiornare un componente in `src/components/ui/`
2. evitare classi duplicate sparse nelle viste
3. mantenere i token cromatici coerenti con `planning/style`
4. per PrimeVue: PT inline se usato in un solo punto; estrarre in `src/plugins/primevue-pt.js` se ≥ 2 viste
