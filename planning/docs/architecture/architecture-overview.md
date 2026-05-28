# Architettura e Funzionamento — Gestionale

Documento di riferimento completo per sviluppatori e LLM che devono comprendere l'applicazione senza contesto pregresso. Aggiornato al 2026-05-27.

---

## 1. Panoramica generale

**Gestionale** è una web app enterprise per aziende ceramiche/logistiche, costruita come sostituzione di un applicativo desktop legacy VB/VB.NET.

Approccio: **modular monolith** — un singolo processo backend FastAPI con moduli interni ben separati, nessun micro-servizio prematuro.

### URL produzione

| Servizio  | URL                                           |
|-----------|-----------------------------------------------|
| Frontend  | `https://gestionale.vasquezlisciotto.xyz`     |
| Backend   | `https://api-gestionale.vasquezlisciotto.xyz` |

---

## 2. Stack tecnologico

### Backend

| Componente      | Tecnologia                          |
|-----------------|-------------------------------------|
| Framework       | FastAPI                             |
| Contratti API   | Pydantic v2                         |
| ORM             | SQLAlchemy (async)                  |
| Database        | PostgreSQL                          |
| Migrations      | Alembic                             |
| Task asincroni  | Celery                              |
| Broker/Backend  | Redis (db 0 broker, db 1 result)    |
| Cache / Pub/Sub | Redis (db 2 cache, db 3 subscriber) |
| Dipendenze      | uv + pyproject.toml                 |
| Container       | Docker (Dockerfile per servizio)    |

### Frontend

| Componente      | Tecnologia                          |
|-----------------|-------------------------------------|
| Framework       | Vue 3 (Composition API, script setup) |
| Bundler         | Vite                                |
| Routing         | Vue Router                          |
| State           | Pinia                               |
| UI component    | PrimeVue v4 (unstyled + PT)         |
| Styling         | Tailwind CSS v4                     |
| HTTP client     | Axios (interceptor centralizzato)   |
| Real-time       | EventSource (SSE)                   |
| Runtime prod    | nginx:1.27-alpine                   |

### Infrastruttura produzione

| Layer           | Tecnologia                          |
|-----------------|-------------------------------------|
| VPS             | Aruba                               |
| PaaS            | Coolify (self-hosted)               |
| Reverse proxy   | Traefik (gestito da Coolify)        |
| CDN / WAF       | Cloudflare                          |
| SSL             | Cloudflare Universal SSL + Traefik Let's Encrypt |
| Firewall        | UFW (porta 80/443 solo IP Cloudflare) |

---

## 3. Architettura runtime

```
Browser (Vue 3)
     │ HTTPS
     ▼
Cloudflare (CDN + WAF + SSL offload)
     │ HTTPS → HTTP interno
     ▼
VPS Aruba
└─ Coolify
   ├─ Traefik (reverse proxy — routing via Docker labels)
   │    ├─ gestionale.vasquezlisciotto.xyz → frontend (nginx:80)
   │    └─ api-gestionale.vasquezlisciotto.xyz → core_service (:8000)
   │         └─ /api/v1/events/stream → router SSE (priority=100, no gzip)
   │
   ├─ core_service    FastAPI uvicorn :8000   (Dockerfile.coolify)
   ├─ celery_worker   Celery worker           (Dockerfile.worker)
   ├─ postgres        PostgreSQL              (Coolify Database Resource)
   ├─ redis           Redis                   (Coolify Redis Resource)
   └─ frontend        nginx static            (frontend/Dockerfile)
```

### Flusso di una request HTTP tipica

1. Browser → Cloudflare (WAF, SSL termination, cache CDN)
2. Cloudflare → Traefik su VPS (HTTP con header `CF-*`)
3. Traefik → container di destinazione (header `X-Forwarded-For` da Cloudflare)
4. FastAPI legge `X-Forwarded-For` solo se l'IP diretto è in `trusted_proxies` (fail-fast altrimenti)

---

## 4. Servizi — dettaglio

### 4.1 `core_service` — FastAPI backend

Entrypoint: `app/main.py` — monta tutti i router sotto `/api/v1`.

**Moduli interni:**

| Prefisso route          | Modulo              | Stato    |
|-------------------------|---------------------|----------|
| `/api/v1/auth`          | Auth & Identity     | Reale    |
| `/api/v1/users`         | User management     | Reale    |
| `/api/v1/admin`         | Super admin         | Reale    |
| `/api/v1/tenant`        | Tenant admin config | Reale    |
| `/api/v1/anagrafiche`   | Anagrafiche         | Reale    |
| `/api/v1/notifications` | Notification Center | Reale    |
| `/api/v1/events/stream` | SSE stream          | Reale    |
| `/api/v1/dashboard`     | KPI dashboard       | Reale    |
| `/api/v1/reports`       | Report asincroni    | Demo     |
| `/health/live`          | Health check        | Reale    |
| `/health/ready`         | Ready check         | Reale    |

**Pattern architetturale interno:**

```
Router → Service → Repository → SQLAlchemy (ORM)
                └→ Redis (cache, pub/sub)
                └→ Celery (task dispatch)
```

Regola ferrea: SQL solo nei repository, logica nei service, schemi Pydantic nei router.

**Startup (`start.sh` in Dockerfile.coolify):**
```sh
/app/.venv/bin/alembic upgrade head
exec /app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Le migrazioni girano nel nuovo container ad ogni deploy — non nel pre-deploy di Coolify.

---

### 4.2 `celery_worker` — Task asincroni

Entrypoint: `app/core/celery_app.py`

- Broker: Redis db 0 — Result backend: Redis db 1
- Concorrenza: 2 worker (`--concurrency=2`)
- Pubblica eventi SSE a ogni step del task via `SyncEventPublisher`

**Task implementati:**

| Task                     | Trigger                          | Evento SSE emesso           |
|--------------------------|----------------------------------|-----------------------------|
| `generate_report`        | `POST /api/v1/reports/generate`  | `task.progress`, `task.completed`, `task.failed` |

---

### 4.3 `postgres` — Database

Due schemi logici:

#### Schema `security`

| Tabella           | Contenuto                                      |
|-------------------|------------------------------------------------|
| `roles`           | Ruoli di sistema                               |
| `permissions`     | Permessi granulari                             |
| `role_permissions`| Associazione M2M ruolo-permesso                |
| `users`           | Utenti con `tenant_id`, `role_id`, `is_active` |
| `tenants`         | Aziende clienti                                |
| `refresh_tokens`  | Token persistiti con `family_id`, `revoked_at` |
| `audit_log`       | Ogni evento auth/admin con IP e user agent     |
| `login_protection`| Rate limiting login per `identifier + ip`      |

#### Schema `core`

| Tabella                      | Contenuto                          |
|------------------------------|------------------------------------|
| `tenant_company_settings`    | Ragione sociale, P.IVA, SDI, PEC   |
| `tenant_smtp_settings`       | Config email tenant (password cifrata) |
| `tenant_document_sequences`  | Numerazioni documentali tenant     |
| `notifications`              | Notifiche persistite per utente    |
| `anagrafiche`                | Clienti, fornitori, agenti         |
| `anagrafica_addresses`       | Indirizzi multipli per tipo        |

Tutte le colonne id/FK usano **UUID nativo PostgreSQL** (migration 0008).

**Naming convenzione migrations:**

```
alembic/versions/YYYYMMDD_NNNN_descrizione.py
```

---

### 4.4 `redis` — Cache, Broker, Pub/Sub

| db | Uso                                           |
|----|-----------------------------------------------|
| 0  | Celery broker                                 |
| 1  | Celery result backend                         |
| 2  | Cache applicativa (KPI, rate limiting) + EventPublisher |
| 3  | Subscriber SSE (connessioni dedicate per stream, una per utente connesso) |

---

### 4.5 `frontend` — Vue 3 SPA

Build: `npm run build` → `dist/` → copiato in nginx.

**Struttura stores Pinia:**

| Store                  | Responsabilità                                     |
|------------------------|----------------------------------------------------|
| `useAuthStore`         | Token in memoria, profilo utente, helper ruolo/permessi |
| `useEventsStore`       | EventSource SSE centralizzato, dispatch eventi a tutti i subscriber |
| `useNotificationsStore`| Lista notifiche, badge unread, mark-read           |
| `useTasksStore`        | Progress task Celery via SSE (no polling)          |
| `useDashboardStore`    | KPI da API, auto-refresh su `kpi.updated` SSE      |

**Routing (Vue Router):**

- Guardie dichiarative: `requiresAuth`, `roles`, `permissions` per ogni route
- Direttiva `v-can` disponibile per visibilità elementi UI
- `AppShell` con sidebar globale: colonna fissa 248px su `xl`, drawer off-canvas su mobile

**Viste reali (collegate ad API):**

| Vista                 | Route             | Permesso richiesto   |
|-----------------------|-------------------|----------------------|
| `LoginView`           | `/login`          | —                    |
| `DashboardView`       | `/dashboard`      | `authenticated`      |
| `AnagraficheView`     | `/anagrafiche`    | `anagrafiche.read`   |
| `AnagraficaDetailView`| `/anagrafiche/:id`| `anagrafiche.read`   |
| `AdminOnlyView`       | `/admin`          | `role: admin`        |
| `TenantAdminView`     | `/tenant-admin`   | `role: tenant_admin` |

---

## 5. Bus eventi real-time (SSE + Redis Pub/Sub)

```
Celery worker / FastAPI route
        │  publish() → Redis Pub/Sub (db 2/3)
        ▼
Redis Pub/Sub ──► GET /api/v1/events/stream ──► EventSource (browser)
                  (autenticato, tenant-scoped)         │
                                               useEventsStore (Pinia)
                                                ├─ useNotificationsStore
                                                ├─ useTasksStore
                                                └─ useDashboardStore
```

**Autenticazione SSE:** il browser non può inviare header `Authorization` con `EventSource`, quindi il token viene accettato anche come query param `?token=`. L'URL viene costruito in `useEventsStore` usando `VITE_API_BASE_URL` per supportare domini separati (frontend ≠ backend).

**Canali Redis per tenant:**

- `events:tenant:{tenant_id}` — eventi per tutti gli utenti del tenant
- `events:user:{user_id}` — eventi per singolo utente
- `events:admin` — eventi globali super admin

**Heartbeat:** ogni 15 secondi per mantenere la connessione SSE attraverso proxy/firewall.

**Fix Traefik:** il middleware `gzip` di Traefik bufferizza lo stream SSE e blocca gli aggiornamenti. Soluzione: router ad alta priorità (`priority=100`) per il path `/api/v1/events/stream` senza middleware gzip. Vedere `13-coolify-deploy-setup.md` per le label Docker esatte.

---

## 6. Autenticazione e sessione

### Flusso login

```
POST /auth/login
  │ verifica rate limit (login_protection)
  │ verifica Origin/Referer (se abilitato)
  │ controllo credenziali su DB
  ▼
access_token (JWT, in memoria frontend, 15 min)
refresh_token (JWT, cookie HttpOnly SameSite=Lax, 7 giorni)
```

### Flusso refresh

```
POST /auth/refresh
  │ legge refresh_token da cookie HttpOnly
  │ verifica jti in DB (SENZA filtro revoked_at)
  │   ├─ token revocato → revoca intera famiglia + 401
  │   ├─ famiglia scaduta (>14 gg) → revoca + 401
  │   └─ token valido → ruota token, emette nuovo coppia
  ▼
nuovo access_token in risposta JSON
nuovo refresh_token in cookie HttpOnly
```

**Reuse detection (RFC 9700 §4.13):** presentare un refresh già ruotato revoca l'intera famiglia. Il frontend usa `navigator.locks` cross-tab per serializzare i refresh paralleli ed evitare race condition.

### Token storage

| Token         | Storage                            | Visibile a JS | Durata    |
|---------------|------------------------------------|---------------|-----------|
| access_token  | Memoria Pinia (non persistito)     | Sì            | 15 min    |
| refresh_token | Cookie `HttpOnly SameSite=Lax`     | No            | 7 giorni  |

**Absolute family timeout:** una famiglia di refresh token non può vivere oltre 14 giorni indipendentemente da quante rotazioni avvengano.

---

## 7. Autorizzazione (RBAC tenant-aware)

### Ruoli

| Ruolo         | Perimetro        | Descrizione                                    |
|---------------|------------------|------------------------------------------------|
| `admin`       | Globale          | Super admin Gestionale — vede tutti i tenant   |
| `tenant_admin`| Proprio tenant   | Amministratore del tenant, no perimetro global |
| `manager`     | Proprio tenant   | Può ricevere permessi di scrittura mirati       |
| `worker`      | Proprio tenant   | Permessi operativi di lettura                  |
| `user`        | Proprio tenant   | Ruolo operativo base                           |

### Pattern di autorizzazione — regola decisionale

| Risorsa                                           | Pattern                      | Esempio                             |
|---------------------------------------------------|------------------------------|-------------------------------------|
| Risorse business/dominio (anagrafiche, bolle...)  | `RequirePermission`          | `anagrafiche.read`, `bom.write`     |
| Risorse identità/sicurezza (utenti, audit, config)| Role guard + service scoping | `admin` vede tutti, `tenant_admin` solo il proprio tenant |

**Regola critica:** il `tenant_id` non va mai fidato dal frontend. Va sempre derivato dal profilo autenticato lato backend.

**`admin` ha `tenant_id = None`** — i service tenant-aware devono gestire questo caso senza richiesta esplicita.

### Permessi granulari attivi

| Permesso               | Descrizione                          |
|------------------------|--------------------------------------|
| `users.read`           | Lettura utenti                       |
| `users.write`          | Creazione/modifica utenti            |
| `audit.read`           | Lettura audit log                    |
| `anagrafiche.read`     | Lettura anagrafiche                  |
| `anagrafiche.write`    | Creazione/modifica anagrafiche       |
| `anagrafiche.delete`   | Soft-delete anagrafiche              |
| `bom.read`             | Demo — distinta base                 |
| `finance.costs.write`  | Demo — costi                         |

---

## 8. Sicurezza — features implementate

### Auth hardening

| Feature                              | Dettaglio                                                    |
|--------------------------------------|--------------------------------------------------------------|
| Password hashing                     | bcrypt via passlib                                           |
| JWT reali                            | HS256, secret configurabile, fail-fast su placeholder        |
| Refresh token persistiti e revocabili| Tabella `security.refresh_tokens`, revoca fisica per famiglia|
| Reuse detection                      | RFC 9700 §4.13 — revoca intera famiglia su riuso             |
| Absolute family timeout              | 14 giorni max indipendentemente dalla rotazione              |
| Cookie HttpOnly                      | Refresh token non leggibile da JavaScript                    |
| Rate limiting login                  | Tre scope: `identifier+ip`, solo `identifier`, solo `ip`     |
| Cooldown 429                         | Risposta standard al superamento soglia                      |
| Origin/Referer check                 | Configurabile, fail-fast se disabilitato in produzione        |
| Trusted proxy espliciti              | `X-Forwarded-For` considerato solo da proxy in whitelist     |
| Fail-fast configurazione insicura    | Startup fallisce in staging/prod se JWT secret è placeholder o cookie non sicuri |

### Dati sensibili

| Feature                              | Dettaglio                                                    |
|--------------------------------------|--------------------------------------------------------------|
| SMTP password cifrata                | Cifratura simmetrica lato backend, mai esposta in chiaro via API |
| Audit log reale                      | Ogni evento auth/admin con `ip_address`, `user_agent`, timestamp |
| Audit eventi                         | LOGIN, LOGOUT, REFRESH, REUSE_DETECTED, FAMILY_REVOKED, FAMILY_TIMEOUT, CREATE_USER, UPDATE_USER, etc. |

### Infrastruttura produzione

| Feature                              | Dettaglio                                                    |
|--------------------------------------|--------------------------------------------------------------|
| Cloudflare WAF                       | 3 regole custom: IP admin, login threat score, bot score     |
| UFW firewall                         | Porte 80/443 aperte solo a IP Cloudflare; SSH solo IP fidati |
| Cloudflare Universal SSL             | Copre `*.vasquezlisciotto.xyz` (primo livello)               |
| HTTPS forzato                        | Traefik gestisce redirect e certificati interni              |
| Cloudflare WAF regola 1              | Block: non-admin IP su `/api/v1/admin/**`                    |
| Cloudflare WAF regola 2              | Challenge: threat score > 10 su `/auth/login`                |
| Cloudflare WAF regola 3              | Block: bot score < 20 su endpoint sensibili                  |

### API design

| Feature                              | Dettaglio                                                    |
|--------------------------------------|--------------------------------------------------------------|
| OpenAPI curata endpoint per endpoint | `Field(description=...)`, `examples`, docstring in italiano  |
| Tenant scoping server-side           | `tenant_id` mai fidato dal frontend, derivato dal profilo JWT|
| Soft delete                          | Anagrafiche: `is_active=False`, non cancellazione fisica     |
| Request ID                           | Logging strutturato con `request_id` su ogni richiesta       |

---

## 9. Database migrations (Alembic)

Convenzione naming: `YYYYMMDD_NNNN_descrizione.py`

| Migration                    | Contenuto principale                                  |
|------------------------------|-------------------------------------------------------|
| `0001`                       | Schema security base, ruoli, permessi, utenti         |
| `0002`                       | Tenant e tenant_id su users                           |
| `0003`                       | Login protection (rate limiting)                      |
| `0004`                       | Schema core, company/smtp/sequences                   |
| `0005`                       | Ruoli manager/worker, permessi demo                   |
| `0006`                       | Notifications                                         |
| `0007`                       | Anagrafiche + addresses                               |
| `0008`                       | UUID nativo su tutte le colonne id/FK                 |
| `0011`                       | Refresh token family (family_id, parent_token_identifier, family_created_at) |

Ogni evoluzione schema deve passare da una nuova migration. Le migration non contengono logica di business.

---

## 10. CI/CD

### Workflow GitHub Actions

| Workflow                           | Trigger                          | Job                                   |
|------------------------------------|----------------------------------|---------------------------------------|
| `checks.yml`                       | Push su qualsiasi branch         | lint, format, compileall, pytest, npm build |
| `deploy-backend-aruba.yml`         | Push su `main` (`backend/**`) o manuale | quality + Coolify deploy webhook |

**Nessun registry Docker esterno.** Coolify builda direttamente dalla sorgente GitHub con i Dockerfile del repo.

Secret GitHub necessari:

| Secret                    | Uso                                      |
|---------------------------|------------------------------------------|
| `COOLIFY_DEPLOY_WEBHOOK`  | Trigger rebuild Coolify core_service     |

### Watch Paths Coolify

| Servizio         | Watch path      | Ricostruisce se cambia     |
|------------------|-----------------|----------------------------|
| `core_service`   | `backend/**`    | qualsiasi file backend     |
| `celery_worker`  | `backend/**`    | qualsiasi file backend     |
| `frontend`       | `frontend/**`   | qualsiasi file frontend    |

---

## 11. File chiave del repository

```
backend/
├── Dockerfile            # bare metal / locale
├── Dockerfile.coolify    # Coolify core_service (start.sh: alembic + uvicorn)
├── Dockerfile.worker     # Coolify celery_worker
├── start.sh              # alembic upgrade head + uvicorn (usato da Dockerfile.coolify)
├── app/
│   ├── main.py           # FastAPI app factory, router mount
│   ├── core/
│   │   ├── config.py     # Settings Pydantic con fail-fast
│   │   ├── celery_app.py # Celery instance
│   │   ├── redis.py      # Redis async client pool
│   │   └── events.py     # EventPublisher + SyncEventPublisher
│   ├── auth/             # Auth & Identity (login, refresh, RBAC, audit)
│   ├── users/            # User management tenant-aware
│   ├── anagrafiche/      # Primo modulo business (CRUD + indirizzi)
│   ├── notifications/    # Notification Center persistito
│   └── tasks/            # Task Celery (report, progress events)
└── alembic/versions/     # Migrations versionate

frontend/
├── Dockerfile            # Multi-stage: node build + nginx alpine
├── nginx.conf            # SPA routing (try_files → index.html)
└── src/
    ├── stores/
    │   ├── auth.js        # Token in memoria, profilo, helper ruoli
    │   ├── events.js      # EventSource SSE centralizzato
    │   ├── notifications.js
    │   ├── tasks.js
    │   └── dashboard.js
    └── views/
        ├── LoginView.vue
        ├── DashboardView.vue
        ├── AnagraficheView.vue
        ├── AnagraficaDetailView.vue
        ├── AdminOnlyView.vue
        └── TenantAdminView.vue
```

---

## 12. Cosa non esiste ancora

| Funzionalità               | Note                                                     |
|----------------------------|----------------------------------------------------------|
| Gestione indirizzi in UI   | API pronte, non ancora esposto nel frontend              |
| Bolle reali                | —                                                        |
| Fatture reali              | —                                                        |
| Spedizioni reali           | —                                                        |
| Reporting reale            | Task demo funzionante, contenuto non reale               |
| MFA / TOTP                 | Non implementato                                         |
| Impersonation              | Non implementato                                         |
| Rate limiting distribuito su Redis | Oggi su PostgreSQL, non distribuito            |
| Password breach screening  | HIBP k-anonymity non implementato                        |
| Upload logo aziendale      | —                                                        |
| Test SMTP reale            | —                                                        |

---

## 13. Credenziali demo

| Utente         | Password    | Ruolo         | Tenant              |
|----------------|-------------|---------------|---------------------|
| `admin`        | `admin123`  | `admin`       | — (super admin)     |
| `tenant.admin` | `tenant123` | `tenant_admin`| Ceramica Demo S.r.l.|
| `user`         | `user123`   | `user`        | Ceramica Demo S.r.l.|

---

## 14. Documenti di approfondimento

| Doc                                                           | Contenuto                              |
|---------------------------------------------------------------|----------------------------------------|
| `planning/docs/backend/03-auth-module.md`                     | Specifiche complete auth e refresh family |
| `planning/docs/backend/10-backend-usage-and-maintenance-guide.md` | Guida manutenzione backend + RBAC decisionale |
| `planning/docs/backend/11-tenant-admin-configuration.md`      | Config tenant, SMTP, numerazioni       |
| `planning/docs/backend/13-coolify-deploy-setup.md`            | Setup completo produzione Coolify      |
| `planning/docs/project-state/current-state.md`                | Stato dettagliato di ogni layer        |
| `planning/docs/architecture/production-readiness-gap-analysis.md` | Gap rispetto a produzione matura  |
