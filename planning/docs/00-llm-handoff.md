# LLM Handoff

## Scopo

Questo documento serve come punto di ingresso rapido per un altro LLM o per un altro sviluppatore che debba riprendere il progetto senza contesto pregresso.

## Contesto progetto

- dominio: gestionale enterprise per aziende ceramiche/logistiche
- origine: applicativo desktop legacy in VB/VB.NET
- target: web app moderna
- approccio corrente: **modular monolith**

## Stato reale del progetto

Il progetto ha completato il nucleo tecnico, il **primo modulo business reale** (Anagrafiche) ed e **deployato in produzione** su Coolify (`gestionale.vasquezlisciotto.xyz` / `api-gestionale.vasquezlisciotto.xyz`).

La parte realmente costruita oggi include:

- backend FastAPI reale
- PostgreSQL reale
- autenticazione JWT reale
- refresh token persistiti
- refresh token esposti al browser solo via cookie `HttpOnly`
- audit persistito
- ruoli `admin`, `tenant_admin`, `manager`, `worker`, `user`
- primo scoping tenant reale
- frontend Vue 3 di test e mockup enterprise
- hardening auth backend con throttling multi-scope, trusted proxy espliciti e origin check sugli endpoint cookie-based
- infrastruttura `Celery + Redis` pronta per task lunghi backend
- Redis asincrono condiviso da FastAPI per cache KPI tenant-aware e rate limiting
- **SSE + Redis Pub/Sub** come bus eventi real-time tenant-scoped
- Notification Center persistito (DB + SSE)
- Task Celery con progress events live (no polling)
- KPI dashboard con auto-refresh su evento `kpi.updated`

## Cosa funziona davvero oggi

### Backend

- `login`
- `refresh`
- `logout`
- `me`
- CRUD utenti
- audit globale super admin
- audit locale tenant
- configurazione aziendale tenant-aware
- configurazione SMTP tenant-aware
- numerazioni documentali tenant-aware
- generazione report asincrona demo via `Celery` con progress events SSE
- KPI dashboard cacheati in Redis e invalidati per tenant
- aggiornamenti tenant admin reali invalidano la cache KPI del tenant senza far fallire mutazioni gia committate se Redis non risponde
- `GET /api/v1/events/stream` — SSE stream autenticato (Bearer o `?token=`)
- `GET/PATCH/POST /api/v1/notifications` — Notification Center persistito
- `EventPublisher` (async) e `SyncEventPublisher` (Celery sync) per publish su bus Redis Pub/Sub
- **Anagrafiche** — primo modulo business reale tenant-aware:
  - CRUD clienti, fornitori, agenti con P.IVA, CF, codice SDI, PEC
  - Indirizzi multipli per tipo (legale, operativo, spedizione, fatturazione)
  - Permessi RBAC: `anagrafiche.read/write/delete`
  - Seed demo 6 soggetti realistici (ceramica/logistica)
- **UUID nativo PostgreSQL** su tutte le colonne id/FK (migration 0008)
- **Articoli** — secondo modulo business reale tenant-aware (migration 0012):
  - catalogo articoli + categorie lookup, codice/nome univoci per tenant
  - prezzo/IVA/giacenza in Decimal, optimistic locking via campo `version` (409 su conflitto)
  - eventi SSE `articolo.created/updated/deactivated` + KPI dashboard "Articoli a catalogo"
  - permessi RBAC `articoli.read/write/delete`; categoria validata cross-tenant
- **modalita demo read-only** (`DEMO_READONLY=true`): middleware blocca tutte le scritture business con 403 (`{"demo_readonly": true}`), eccetto `/auth/*`; il frontend legge `GET /api/v1/meta`, mostra un banner persistente e un toast quando una scrittura viene bloccata

### Frontend

- login reale
- access token in memoria
- ripristino sessione via refresh da cookie `HttpOnly`
- route guard dichiarative per ruoli e permessi
- dashboard con KPI reali tenant-aware + KPI mock ERP
- task progress live via SSE (no polling)
- `NotificationBell` nell'header con badge unread e pannello dropdown
- console `Super Admin` statica
- console `Tenant Admin` statica
- **sidebar di navigazione globale** in `AppShell`: Desktop (colonna xl:248px) + mobile drawer via hamburger; voci reali: Dashboard, Anagrafiche, Tenant Admin, Super Admin; voci mockup disabilitate: Bolle, Fatture, Articoli, Spedizioni, Scadenze
- **`AnagraficheView`** (`/anagrafiche`): lista filtrata con `IconField`+`InputText`+`Select` PrimeVue PT, toggle "Solo attivi", reset filtri, righe cliccabili verso la detail, modale create/edit, soft-delete
- **`AnagraficaDetailView`** (`/anagrafiche/:id`): hero card, dati fiscali, SDI/PEC, indirizzi, sidebar riepilogo, bottone back con hover animato

## Cosa e solo mockup

Queste viste esistono ma **non sono ancora collegate a business logic reale**:

- dashboard ERP standard-user
- console `Super Admin`
- gran parte della console `Tenant Admin`

Il frontend oggi e soprattutto:

- client di test auth
- shell UI
- base visiva per i moduli futuri

## Cosa non esiste ancora

- gestione indirizzi anagrafiche da frontend (CRUD indirizzi disponibile da API, non ancora esposto in UI)
- bolle reali
- fatture reali
- spedizioni reali
- reporting reale
- api gateway reale
- upload reale del logo aziendale
- test SMTP reale
- impersonation reale Gestionale

## Deployment produzione

Il progetto e **live in produzione** su VPS Aruba con **Coolify** come PaaS.

| Servizio  | URL                                           |
|-----------|-----------------------------------------------|
| Frontend  | `https://gestionale.vasquezlisciotto.xyz`     |
| Backend   | `https://api-gestionale.vasquezlisciotto.xyz` |

- **Proxy**: Traefik (gestito da Coolify) — NON Caddy
- **SSL**: Cloudflare Universal SSL (free) + Traefik Let's Encrypt interno
- **CDN/WAF**: Cloudflare con 3 regole WAF custom + UFW che blocca tutto tranne IP Cloudflare
- **Build**: Coolify builda direttamente da Dockerfile (no GHCR, no registry esterno)
- **Deploy CI**: push su `main` → `checks.yml` quality gate → Coolify webhook trigger
- **Migrazioni**: `start.sh` esegue `alembic upgrade head` nel container nuovo a ogni deploy

### Dockerfiles

| File                         | Servizio Coolify   |
|------------------------------|--------------------|
| `backend/Dockerfile.coolify` | `core_service`     |
| `backend/Dockerfile.worker`  | `celery_worker`    |
| `frontend/Dockerfile`        | `frontend`         |
| `backend/Dockerfile`         | locale/bare-metal  |

### Fix SSE critico (Traefik)

Traefik applica `gzip` di default — bufferizza l'SSE e blocca i real-time update. Il servizio `core_service` ha un router Traefik ad alta priorita (`priority=100`) per `/api/v1/events/stream` **senza** middleware gzip. Vedere `planning/docs/backend/13-coolify-deploy-setup.md` per le label esatte.

## Architettura corrente

### Backend

- framework: `FastAPI`
- contratti: `Pydantic`
- ORM: `SQLAlchemy`
- DB: `PostgreSQL`
- migrations: `Alembic` (auto-run via `start.sh` a ogni deploy)
- queue worker: `Celery`
- broker/result backend: `Redis`
- dipendenze: `uv`
- containerizzazione: `Docker` (build Coolify) + `docker-compose.aruba.yml` (locale)

### Frontend

- framework: `Vue 3`
- bundler: `Vite`
- state management: `Pinia` per la sessione auth
- styling: `Tailwind CSS`
- HTTP client: `Axios`
- routing: `Vue Router`
- runtime: `nginx:1.27-alpine` con `nginx.conf` custom per il **solo SPA routing**; il routing `/api` e' di Traefik in produzione (Coolify) e di `nginx.local.conf` in locale (docker-compose). Vedi "Due ambienti, due reverse proxy" in `13-coolify-deploy-setup.md`.

## Schemi database attivi

### `security`

- `roles`
- `permissions`
- `users`
- `tenants`
- `role_permissions`
- `refresh_tokens`
- `audit_log`

### `core`

- `tenant_company_settings`
- `tenant_smtp_settings`
- `tenant_document_sequences`

## Regole di ruolo attuali

### `admin`

- e il super admin Gestionale
- vede audit globale
- vede tutti gli utenti
- non usa la console tenant

### `tenant_admin`

- appartiene a un solo tenant
- vede solo utenti del proprio tenant
- vede solo audit locale del proprio tenant
- gestisce configurazione aziendale del proprio tenant
- non accede al perimetro globale Gestionale

### `manager`

- appartiene a un solo tenant
- puo ricevere permessi di scrittura mirati come `finance.costs.write`

### `worker`

- appartiene a un solo tenant
- ha permessi operativi di lettura come `bom.read`

### `user`

- ruolo operativo base
- nessuna funzione amministrativa

## Contratti e tenant scoping

Regola critica:

- il `tenant_id` **non** deve essere trattato come dato affidabile proveniente dal frontend
- il `tenant_id` va derivato dal profilo autenticato corrente
- per risorse tenant-aware usare `RequirePermission` e, se serve, risolvere il tenant dal record DB prima di concedere accesso

Questo e gia vero nei service tenant-aware implementati.

## Sicurezza attuale

- password utenti hashate
- JWT reali
- refresh token persistiti e revocabili
- refresh token non leggibili da JavaScript nel frontend
- refresh token family con reuse detection (RFC 9700 §4.13): riuso di un token ruotato revoca l'intera famiglia
- absolute family timeout configurabile (default 14 giorni)
- frontend con lock single-flight + `navigator.locks` cross-tab per i refresh paralleli (no grace period server-side, standard Auth0/Okta)
- password breach screening HIBP (k-anonymity) con cache Redis, policy fail-open
- policy password NIST SP 800-63B: minimo 12 caratteri + blacklist, niente complessita' forzata
- audit log reale (incluso `refresh_reuse_detected`, `refresh_family_revoked`, `refresh_family_timeout`, `password_breach_rejected`, `password_breach_check_failed`)
- password SMTP cifrata lato backend
- OpenAPI curata endpoint per endpoint
- commenti, docstring e messaggi descrittivi in italiano
- controllo `Origin` / `Referer` su `login` e `refresh` quando abilitato
- fail-fast configurazione insicura in staging e produzione

## Convenzioni operative da rispettare

- SQL nei repository, non nei router
- logica applicativa nei service
- schemi API Pydantic espliciti
- `Field(description=...)` e `examples` sugli schemi
- docstring endpoint in italiano
- aggiornare `planning/docs` a ogni modifica sostanziale
- usare Alembic per ogni evoluzione schema

## Credenziali demo correnti

- `admin / admin123`
- `tenant.admin / tenant123`
- `user / user123`

Tenant demo:

- `Ceramica Demo S.r.l.`

## File da leggere per primi

Ordine consigliato:

1. [planning/struttura.md](planning/struttura.md)
2. [planning/docs/project-state/current-state.md](planning/docs/project-state/current-state.md)
3. [planning/docs/backend/13-coolify-deploy-setup.md](planning/docs/backend/13-coolify-deploy-setup.md) ← setup produzione Coolify attuale
4. [planning/docs/architecture/production-readiness-gap-analysis.md](planning/docs/architecture/production-readiness-gap-analysis.md)
5. [planning/docs/architecture/production-readiness-execution-backlog.md](planning/docs/architecture/production-readiness-execution-backlog.md)
6. [planning/docs/backend/10-backend-usage-and-maintenance-guide.md](planning/docs/backend/10-backend-usage-and-maintenance-guide.md)
7. [planning/docs/backend/11-tenant-admin-configuration.md](planning/docs/backend/11-tenant-admin-configuration.md)
8. [planning/docs/frontend/02-frontend-usage-and-maintenance-guide.md](planning/docs/frontend/02-frontend-usage-and-maintenance-guide.md)

## Prossimi step coerenti

Asse sicurezza (in corso): refresh family reuse detection e password breach screening sono **fatti**. Restano:

1. MFA opzionale TOTP per `admin` e `tenant_admin` (con backup codes)
2. impersonation controllata super-admin → tenant per assistenza, con audit forte
3. endpoint self-service di cambio/reset password (riusa lo screening HIBP gia' integrato)

Altre direzioni:

4. collegare le console frontend `Super Admin` / `Tenant Admin` alle API reali
5. estendere lo scoping tenant ai primi domini business (Articoli come ponte verso Bolle/Fatture)
6. audit business unificato con `before_json`/`after_json` sui domini reali
7. sostituire il task demo report con un caso reale come PDF massivo o invio mail bulk

## Rischi o limiti da tenere presenti

- il frontend puo dare l'impressione di essere piu avanzato del backend: molte viste sono ancora mockup
- il tenant scoping e reale, ma solo su alcuni moduli
- il documento `auth-module-spec.md` e una specifica viva: va tenuto allineato a ogni salto architetturale
- non esiste ancora una strategia completa di migrazione del dominio legacy verso i moduli business
