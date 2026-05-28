# Stato Corrente

## Obiettivo della fase

Preparare il nucleo tecnico del nuovo gestionale web Gestionale partendo dal modulo trasversale `Auth & Identity`.

## Stato raggiunto

- definito `Master Plan` architetturale
- definita specifica tecnica del modulo `Auth`
- definito skeleton architetturale del backend FastAPI
- creato backend minimale eseguibile
- introdotta containerizzazione con Docker
- introdotte dipendenze gestite con `uv`
- introdotto `Alembic` con migration iniziale
- creato schema PostgreSQL `security`
- implementato login reale su PostgreSQL con JWT e refresh token persistiti
- verificato smoke test reale del backend containerizzato
- creato frontend minimale `Vue 3` per test del flusso JWT
- introdotti check di qualita leggeri per backend e frontend
- introdotta pipeline CI minima per lint e build
- definita e applicata una prima linea stilistica del gestionale su palette grigio e rosso
- estratti componenti UI condivisi per evitare duplicazione nelle viste frontend

## Messaging Layer (aggiunto 2026-05-26)

Il progetto dispone ora di un bus eventi real-time basato su **SSE + Redis Pub/Sub**.

### Architettura

```
Celery worker / FastAPI route
        │  publish() su Redis Pub/Sub (db 3 per subscriber, db 2 per publisher)
        ▼
Redis Pub/Sub ──► FastAPI SSE endpoint ──► EventSource (Vue frontend)
                  (tenant-scoped)               │
                                         Pinia eventsStore
                                          ├─ notificationsStore (notification.new)
                                          ├─ tasksStore (task.progress/completed/failed)
                                          └─ dashboardStore (kpi.updated)
```

### Funzionalità implementate

**STEP 1 — SSE infrastruttura base**
- `GET /api/v1/events/stream` endpoint SSE autenticato, tenant-scoped
- token accettato da header `Authorization: Bearer` o query param `?token=` (per EventSource browser)
- canali Redis separati per tenant, admin e user
- heartbeat ogni 15 secondi per keepalive
- `EventPublisher` async per route FastAPI, `SyncEventPublisher` per Celery worker

**STEP 2 — Notification Center**
- tabella `core.notifications` (migration `20260526_0007`)
- `NotificationService`: persist + publish atomici
- endpoint `GET /api/v1/notifications`, `PATCH /{id}/read`, `POST /read-all`, `POST /test`
- frontend: `NotificationBell` con badge unread, `NotificationPanel` dropdown, `useNotificationsStore`
- `NotificationBell` integrata nell'header `AppShell` per tutti gli utenti autenticati

**STEP 3 — Task Progress via SSE**
- `report_tasks.py` pubblica `task.progress`, `task.completed`, `task.failed` su Redis ad ogni step
- frontend: `useTasksStore` sostituisce il polling `setInterval(2s)` con listener SSE
- dashboard aggiornata: barra di avanzamento guidata da eventi in tempo reale

**STEP 4 — KPI Live Update**
- `ProductionService.update_production_status` pubblica `kpi.updated` dopo cache invalidation
- frontend: `useDashboardStore` si iscrive a `kpi.updated` e chiama `GET /dashboard/kpis`
- dashboard mostra sezione "KPI Tenant Live" con auto-refresh su evento SSE

### Redis db layout

| db | Uso                                 |
|----|-------------------------------------|
| 0  | Celery broker                       |
| 1  | Celery result backend               |
| 2  | Cache applicativa + EventPublisher  |
| 3  | Subscriber SSE (connessioni dedicate per stream) |

## Stato backend attuale

- `FastAPI` configurato
- `Pydantic` usato per schemi request/response
- `SQLAlchemy` attivo come ORM layer
- `PostgreSQL` attivo via `docker-compose`
- `Alembic` attivo per lo schema `security`
- `Celery + Redis` introdotti per task asincroni backend
- Redis asincrono introdotto anche come cache applicativa e motore di rate limiting
- **SSE + Redis Pub/Sub** introdotti come bus eventi real-time (4 db Redis separati per responsabilita)
- `EventPublisher` (async) e `SyncEventPublisher` (Celery) disponibili per publish su canali tenant/admin/user
- `NotificationService` con persistenza DB + publish SSE atomici
- task Celery pubblicano progress events via `SyncEventPublisher` invece di solo `update_state`
- `ProductionService` pubblica `kpi.updated` dopo invalidazione cache
- `AuthService` collegato al DB reale
- `UserService` collegato al DB reale
- `AuditService` collegato al DB reale
- login persistito su DB con password hashate
- refresh token persistiti e ruotati
- audit esteso anche alle operazioni amministrative utenti
- ruolo reale `tenant_admin` introdotto nel dominio sicurezza
- RBAC dichiarativo tenant-aware disponibile con ruoli `admin`, `tenant_admin`, `manager`, `worker`, `user`
- endpoint demo protetti: `GET /api/v1/bom/{bom_id}` e `POST /api/v1/finance/costs`
- introdotto schema `tenants` con collegamento `user.tenant_id`
- gestione utenti resa tenant-aware per il livello 2
- audit locale tenant esposto tramite endpoint dedicato
- configurazione aziendale tenant-aware esposta tramite API dedicate
- cifratura lato backend introdotta per i segreti SMTP del tenant
- protezione login persistita introdotta su `/auth/login`
- cooldown e rate limiting auth attivi su tre scope: `identifier + ip_address`, solo `identifier`, solo `ip_address`
- audit auth con `ip_address` e `user_agent` reali
- hardening produzione introdotto su auth: fail-fast configurazione sensibile, trusted proxy espliciti e controllo `Origin` / `Referer` sugli endpoint cookie-based
- refresh token family con reuse detection (RFC 9700 §4.13): riusare un refresh ruotato revoca l'intera famiglia, con audit dedicato
- absolute family timeout (`refresh_token_family_max_age_days`, default 14gg): re-login forzato oltre la soglia
- frontend con lock single-flight + `navigator.locks` cross-tab per serializzare i refresh paralleli (no grace period server-side)
- password breach screening via HIBP Pwned Passwords con k-anonymity + cache Redis, fail-open con audit `PASSWORD_BREACH_CHECK_FAILED`
- policy password aggiornata a NIST SP 800-63B: minimo 12 caratteri + blacklist, niente complessita' forzata
- endpoint dashboard KPI tenant-aware protetto con cache Redis e rate limiting
- endpoint demo di mutazione produzione con invalidazione mirata della cache tenant
- update reali tenant admin allineati con invalidazione cache KPI del tenant in best-effort
- osservabilita minima backend introdotta con `request_id`, logging strutturato e health endpoint `live/ready`
- baseline test backend introdotta su `health`, `auth` e RBAC tenant-aware, eseguita anche in CI
- test unit aggiunti su refresh token family (7) e password breach screening + validator NIST (12)
- secondo dominio business reale: **Articoli** (catalogo) + **Categorie articolo**, tenant-aware, con optimistic locking (`version`), prezzi/IVA in Decimal, eventi SSE e KPI "Articoli a catalogo"; 11 test unit
- **modalita demo read-only** (`DEMO_READONLY`): middleware che blocca ogni scrittura business con 403 esplicito, eccetto gli endpoint `/auth/*`; endpoint pubblico `GET /api/v1/meta` espone il flag al frontend
- migration discipline via `start.sh`: alembic upgrade head eseguito nel nuovo container a ogni deploy Coolify
- deploy produzione su Coolify: `core_service`, `celery_worker`, `postgres`, `redis` come risorse separate
- GitHub Actions: quality gate + Coolify deploy webhook (no GHCR, no SSH)
- Traefik SSE fix: router ad alta priorita senza gzip middleware per `/api/v1/events/stream`
- Cloudflare WAF + UFW attivi in produzione
- dipendenze frontend aggiornate a versioni recenti e prive di vulnerabilita note da `npm audit`
- immagini Docker principali aggiornate e pin esplicite
- immagini runtime e build ricontrollate rispetto ai tag ufficiali correnti; aggiornati `uv`, `node`, `postgres` e `redis`, mantenuto `python 3.12.13` e runner CI pin a `ubuntu-24.04`

## Stato frontend attuale

- `Vue 3` con `script setup`
- `Vite` attivo come dev server
- `Tailwind CSS v4` attivo (CSS-first via `@tailwindcss/vite`)
- `Pinia` attiva per lo stato auth condiviso
- `Axios` attivo con interceptor centralizzato
- store auth esteso con helper ruolo/permessi
- `Vue Router` attivo con guardie dichiarative per auth, ruoli e permessi
- `PrimeVue v4` integrato in modalita `unstyled: true` con Pass-Through Tailwind
- login enterprise con toggle password nativo e copy istituzionale Gestionale
- login con access token in memoria e refresh token in cookie `HttpOnly`
- direttiva `v-can` disponibile per la visibilita degli elementi UI
- dashboard protetta collegata a `GET /api/v1/auth/me`
- vista `admin-only` collegata a `GET /api/v1/admin/audit-log`
- home gestionale di base resa comune per tutti gli utenti autenticati
- navigazione admin nascosta ai non admin
- area `Super Admin` Gestionale trasformata in mockup statico enterprise
- area `Tenant Admin` cliente trasformata in mockup statico enterprise
- console `Super Admin` e `Tenant Admin` separate anche nella navigazione e nelle guardie router
- demo frontend di task report asincrono con **SSE real-time** integrata nella dashboard (polling rimosso)
- `NotificationBell` con badge unread nell'header AppShell per tutti gli utenti autenticati
- `NotificationPanel` dropdown con lista notifiche, mark-read e mark-all-read
- `useDashboardStore` con KPI reali da API e auto-refresh via evento SSE `kpi.updated`
- `useEventsStore` come bus SSE centralizzato (EventSource browser con reconnect automatico)
- `useTasksStore` per tracking task Celery via SSE senza polling
- `useNotificationsStore` con caricamento iniziale + aggiornamento live via SSE

- workflow `.github/workflows/checks.yml` attivo come quality gate minimo
- workflow `.github/workflows/deploy-backend-aruba.yml` attivo: quality + Coolify deploy webhook
- deploy produzione via Coolify webhook al push su `main` (nessun GHCR, nessun SSH)
- `docker-compose.aruba.yml` mantenuto come riferimento locale ma non usato in produzione Coolify
- frontend completamente responsive mobile-first (375px → 1280px+)
- **sidebar di navigazione globale** in `AppShell` (refactoring da DashboardView): colonna fissa `248px` su desktop `xl`, drawer off-canvas su mobile via hamburger, overlay scrim, chiusura automatica al cambio route
- voci reali: Dashboard, Anagrafiche, Tenant Admin (role), Super Admin (role); voci mockup disabilitate: Bolle, Fatture, Articoli, Spedizioni, Scadenze
- stato drawer condiviso tramite composable `useSidebar.js` (module-level reactive)
- tabelle con column hiding responsive in tutte le view
- griglia KPI con `grid-cols-1 → md:grid-cols-2 → xl:grid-cols-4`
- filtri reali nella DashboardView: `InputText` con `IconField` + due `Select` (tipo/stato) con `computed righeFiltraite`
- `Tag` PrimeVue con PT status-aware in DashboardView, AdminOnlyView e TenantAdminView
- `ProgressBar` PrimeVue per utilizzo risorse DB e utenti in AdminOnlyView
- `Avatar` e `Tooltip` PrimeVue in AppShell
- `AppShell` aggiornata con header mobile (burger + brand center + logout compatto) e desktop invariato
- **`AnagraficheView`**: lista anagrafiche reale con filtri (IconField+InputText+Select con PT completo, toggle "Solo attivi" nativo, reset filtri), righe cliccabili verso detail, modale create/edit (`Dialog` PrimeVue PT), soft-delete
- **`AnagraficaDetailView`**: view dettaglio singola anagrafica — hero, dati fiscali, SDI/PEC, indirizzi, sidebar riepilogo, bottone back con hover + micro-animazione freccia
- route `/anagrafiche/:id` con `props: true` e guardia `anagrafiche.read` nel router
- `Dialog` PrimeVue introdotto (unstyled + PT) per i form modali Anagrafiche

## Deployment produzione (aggiunto 2026-05-27)

Il progetto e **deployato e funzionante in produzione** su VPS Aruba con **Coolify** come self-hosted PaaS.

### URL produzione

| Servizio  | URL                                        |
|-----------|--------------------------------------------|
| Frontend  | `https://gestionale.vasquezlisciotto.xyz`  |
| Backend   | `https://api-gestionale.vasquezlisciotto.xyz` |

### Architettura runtime Coolify

```
Cloudflare (CDN + WAF + SSL)
        │
        ▼
VPS Aruba (UFW: 80/443 solo da IP Cloudflare)
        │
     Coolify
        ├─ Traefik (reverse proxy interno, gestisce TLS e routing)
        ├─ core_service   (FastAPI, Dockerfile.coolify, porta 8000)
        ├─ celery_worker  (Celery, Dockerfile.worker)
        ├─ postgres       (Database Resource Coolify)
        ├─ redis          (Redis Resource Coolify)
        └─ frontend       (Nginx Alpine, frontend/Dockerfile)
```

### Proxy: Traefik (non Caddy)

Coolify usa **Traefik** come proxy interno. Le Caddy label in `docker-compose.aruba.yml` sono irrilevanti per Coolify.

**Fix critico SSE**: Traefik applica il middleware `gzip` di default, che bufferizza l'SSE stream e blocca gli update in tempo reale. La soluzione e aggiungere al servizio `core_service` in Coolify queste label:

```
traefik.http.routers.sse-stream.rule=Host(`api-gestionale.vasquezlisciotto.xyz`) && PathPrefix(`/api/v1/events/stream`)
traefik.http.routers.sse-stream.priority=100
traefik.http.routers.sse-stream.entrypoints=https
traefik.http.routers.sse-stream.tls=true
traefik.http.routers.sse-stream.tls.certresolver=letsencrypt
traefik.http.routers.sse-stream.service=<nome-servizio-generato-da-coolify>
```
(nessun `middlewares=gzip` su questo router — priorita 100 batte il router di default)

### Dockerfile separati

| File                      | Uso                                      |
|---------------------------|------------------------------------------|
| `backend/Dockerfile`      | Bare metal / locale (uvicorn diretto)    |
| `backend/Dockerfile.coolify` | Coolify core_service (esegue `start.sh`: alembic + uvicorn) |
| `backend/Dockerfile.worker`  | Coolify celery_worker                 |
| `frontend/Dockerfile`     | Multi-stage: node build + nginx alpine   |

`start.sh` esegue `alembic upgrade head` poi `uvicorn` **nello stesso container** — indispensabile perche il pre-deploy command di Coolify gira nel container vecchio, non in quello nuovo.

### Nginx frontend: split locale / produzione

`frontend/nginx.conf` (incluso nell'immagine Docker) serve **solo la SPA** e deve restare tale: in produzione e' il reverse proxy (Traefik su Coolify) a instradare `/api` e `/health` verso `core_service`. Un `proxy_pass http://core_service:8000` con hostname letterale farebbe **fallire l'avvio di nginx** se quel nome non risolve nella rete di produzione.

Per lo sviluppo locale (docker-compose, nessun Traefik) il proxy `/api` serve: viene fornito da `frontend/nginx.local.conf`, montato come volume **solo** dal `docker-compose.yml` su `/etc/nginx/conf.d/default.conf`. Coolify ignora il `docker-compose.yml`, quindi la produzione non vede mai questa configurazione.

> Nota: `docker-compose.yml` mappa la porta frontend come `5173:80` (nginx ascolta sulla 80 dentro il container).

### GitHub Actions

- `checks.yml`: quality gate (lint, format, compileall, pytest) su ogni push
- `deploy-backend-aruba.yml`: quality + deploy webhook Coolify al push su `main` che tocca `backend/**`
- **Non si usa piu GHCR**: build avviene direttamente in Coolify dalla sorgente

Secret GitHub Actions necessario:

| Secret                    | Valore                             |
|---------------------------|------------------------------------|
| `COOLIFY_DEPLOY_WEBHOOK`  | URL webhook da Coolify core_service|

### Sicurezza produzione

- **Cloudflare WAF** con 3 regole custom:
  1. Block: IP non admin su `/api/v1/admin/**`
  2. Challenge: login threat score > 10
  3. Block: bot score < 20 su endpoint sensibili
- **UFW**: porte 80/443 aperte solo a IP Cloudflare, SSH solo da IP fidati
- **Cloudflare Universal SSL** (free): copre `*.vasquezlisciotto.xyz` — NON copre sottodomini di secondo livello (es. `api.gestionale.*` → usare `api-gestionale.*`)

### Watch Paths Coolify

- `core_service` / `celery_worker`: watch path `backend/**`
- `frontend`: watch path `frontend/**`

## Stato delivery e runtime operativo

- approccio `modular monolith`
- `Auth & Identity` come primo asse trasversale
- documentazione operativa obbligatoria durante ogni evoluzione
- standard OpenAPI elevato per ogni endpoint backend
- convenzione descrittiva del codice in italiano
- frontend minimale come client di test prima dei moduli business
- pin delle immagini e lockfile come regola di stabilita del runtime
- quality gate leggeri preferiti a policy troppo rigide in questa fase

## Documento di handoff

Per ripartire con un altro LLM o con un altro sviluppatore, il punto di ingresso rapido e:

- [00-llm-handoff.md](/c:/Users/ivan.lisciotto_webra/Desktop/project/planning/docs/00-llm-handoff.md)
- [production-readiness-gap-analysis.md](/c:/Users/ivan.lisciotto_webra/Desktop/project/planning/docs/architecture/production-readiness-gap-analysis.md)
- [production-readiness-execution-backlog.md](/c:/Users/ivan.lisciotto_webra/Desktop/project/planning/docs/architecture/production-readiness-execution-backlog.md)
