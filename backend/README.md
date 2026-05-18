# Backend Skeleton

Questo folder contiene il `core_service` FastAPI del progetto Esseduesoft, con il primo modulo trasversale `Auth & Identity` gia collegato a PostgreSQL.

Stato attuale:

- struttura package pronta
- router v1 registrati
- modelli ORM del dominio sicurezza definiti
- schemi Pydantic definiti
- servizi Auth, Users e Audit collegati a PostgreSQL
- migration Alembic attive
- JWT reali con refresh token persistiti
- containerizzazione con Docker
- Redis asincrono condiviso lato FastAPI
- dipendenze gestite con `uv`
- immagini base Docker pin esplicite
- protezione login persistita con rate limiting e cooldown basilare
- logging strutturato con `request_id` e health endpoint `live/ready`

Non include ancora:

- gestione completa dei permessi granulari lato business
- endpoint avanzati di revoca puntuale della singola sessione
- collegamento al futuro dominio anagrafiche
- suite di test automatizzata completa

## Avvio locale con uv

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --app-dir backend --reload
```

## Check di qualita

```bash
uv sync --group dev
uv run ruff check app alembic
uv run ruff format --check app alembic
uv run python -m compileall app alembic
```

## Avvio con Docker Compose

```bash
docker compose up --build
```

Nel flusso Docker Compose:

- `db_migrator` esegue `alembic upgrade head`
- `core_service` parte solo dopo il completamento positivo delle migration
- `celery_worker` parte solo dopo il completamento positivo delle migration

## Baseline versioni correnti

- runtime Python container: `python:3.12.13-slim-trixie`
- `uv` nel container: `0.11.11`
- database container: `postgres:17.9-alpine3.23`
- dipendenze Python risolte da `uv.lock`

## Smoke test minimo

Endpoint disponibili:

- `GET /health`
- `GET /health/live`
- `GET /health/ready`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/users`
- `GET /api/v1/admin/audit-log`
- `GET /api/v1/dashboard/kpis`
- `PUT /api/v1/production/update`
- `GET /api/v1/tenant-admin/audit-log`
- `GET /api/v1/tenant-admin/company-settings`
- `PUT /api/v1/tenant-admin/company-settings`
- `GET /api/v1/tenant-admin/smtp-settings`
- `PUT /api/v1/tenant-admin/smtp-settings`
- `GET /api/v1/tenant-admin/document-sequences`
- `PUT /api/v1/tenant-admin/document-sequences/{sequence_code}`

Credenziali iniziali seedate:

- `admin / admin123`
- `tenant.admin / tenant123`
- `user / user123`

Comportamento attuale:

- il login genera JWT reali
- il login applica rate limiting per coppia `identifier + ip_address`
- dopo `5` tentativi falliti nella finestra configurata il backend risponde con `429`
- il cooldown di default e `15` minuti ed e configurabile via environment
- il refresh token viene persistito su PostgreSQL
- il refresh token viene esposto al browser solo via cookie `HttpOnly`
- la rotazione del refresh token revoca il token precedente
- il logout revoca tutte le sessioni refresh attive dell'utente
- i KPI dashboard tenant-aware vengono cacheati in Redis per `5` minuti
- l'endpoint dashboard applica rate limiting per utente/IP
- una mutazione di produzione invalida la sola cache KPI del tenant coinvolto
- gli update reali di configurazione tenant invalidano anch'essi la cache KPI del tenant
- un fault Redis in invalidazione cache non annulla una mutazione gia committata su PostgreSQL
- il ruolo `tenant_admin` e disponibile e autenticabile
- il profilo autenticato espone `tenant_id` quando l'utente appartiene a una specifica azienda
- la gestione utenti e tenant-aware: il `tenant_admin` vede e modifica solo utenti del proprio tenant
- l'audit locale tenant e disponibile su `GET /api/v1/tenant-admin/audit-log`
- le impostazioni aziendali tenant-aware sono disponibili per profilo azienda, SMTP e numerazioni
- la password SMTP viene cifrata lato backend e non viene mai restituita nelle API
- il super admin mantiene la vista globale su utenti e audit
- gli eventi auth registrano `ip_address` e `user_agent` reali
- ogni risposta backend espone `X-Request-ID`
- il backend puo emettere log testo o JSON tramite `LOG_JSON`
- il web container non esegue piu migration implicite in bootstrap

Variabili runtime aggiuntive per la protezione auth:

- `LOGIN_RATE_LIMIT_MAX_ATTEMPTS`
- `LOGIN_RATE_LIMIT_WINDOW_MINUTES`
- `LOGIN_RATE_LIMIT_LOCKOUT_MINUTES`
- `CORS_ALLOWED_ORIGINS`
- `REFRESH_COOKIE_NAME`
- `REFRESH_COOKIE_SECURE`
- `REFRESH_COOKIE_SAMESITE`
- `REFRESH_COOKIE_PATH`
- `REDIS_URL`
- `DASHBOARD_KPI_CACHE_TTL_SECONDS`
- `API_RATE_LIMIT_REQUESTS_PER_MINUTE`
