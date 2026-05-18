# Frontend Auth Test Client

## Struttura

- `frontend/src/components/layout/AppShell.vue`: shell condivisa applicativa
- `frontend/src/components/ui/`: componenti base riusabili del design system iniziale
- `frontend/src/router/index.js`: definizione rotte e guardie
- `frontend/src/stores/auth.js`: stato sessione in memoria
- `frontend/src/lib/http.js`: istanza `axios` con interceptor request/response
- `frontend/src/services/auth.js`: funzioni API del modulo auth/admin
- `frontend/src/views/LoginView.vue`: login
- `frontend/src/views/DashboardView.vue`: mockup ERP frontend-only per utenti standard
- `frontend/src/views/TenantAdminView.vue`: console `Tenant Admin` frontend-only
- `frontend/src/views/AdminOnlyView.vue`: console `Super Admin` frontend-only

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

- non implementa logica di business
- non esegue chiamate dati dedicate
- usa dati dummy definiti localmente nello `script setup`
- serve solo per validare layout ERP, densita tabellare e ingombri responsive

## Mockup Super Admin

La vista `/admin-only` corrente:

- e dedicata al personale Esseduesoft
- modella tenants, licenze, health e audit globale
- resta completamente statica in questa fase
- non usa ancora dati reali o logica di impersonation effettiva

## Mockup Tenant Admin

La vista `/tenant-admin` corrente:

- modella utenti interni, RBAC, impostazioni globali aziendali, numerazioni e audit locale
- e statica e usa dati dummy nello `script setup`
- e visibile solo al ruolo reale `tenant_admin`
- non e accessibile al `Super Admin`, che mantiene solo la console globale Esseduesoft

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
