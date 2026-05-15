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
- dipendenze gestite con `uv`
- immagini base Docker pin esplicite

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

## Baseline versioni correnti

- runtime Python container: `python:3.12.13-slim-trixie`
- `uv` nel container: `0.11.11`
- database container: `postgres:17.9-alpine3.23`
- dipendenze Python risolte da `uv.lock`

## Smoke test minimo

Endpoint disponibili:

- `GET /health`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/users`
- `GET /api/v1/admin/audit-log`
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
- il refresh token viene persistito su PostgreSQL
- la rotazione del refresh token revoca il token precedente
- il logout revoca tutte le sessioni refresh attive dell'utente
- il ruolo `tenant_admin` e disponibile e autenticabile
- il profilo autenticato espone `tenant_id` quando l'utente appartiene a una specifica azienda
- la gestione utenti e tenant-aware: il `tenant_admin` vede e modifica solo utenti del proprio tenant
- l'audit locale tenant e disponibile su `GET /api/v1/tenant-admin/audit-log`
- le impostazioni aziendali tenant-aware sono disponibili per profilo azienda, SMTP e numerazioni
- la password SMTP viene cifrata lato backend e non viene mai restituita nelle API
- il super admin mantiene la vista globale su utenti e audit
