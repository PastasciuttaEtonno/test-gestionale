# Backend Usage and Maintenance Guide

## Obiettivo

Spiegare come funziona il backend oggi, come avviarlo, come modificarlo correttamente e dove prestare attenzione quando si interviene.

## Stack attivo

- `FastAPI` per routing, dependency injection e OpenAPI
- `Pydantic` per request/response model e documentazione Swagger
- `SQLAlchemy` per ORM e accesso al database
- `Alembic` per migrazioni
- `PostgreSQL` come persistenza primaria
- `uv` per dipendenze e comandi Python
- `Docker Compose` per avvio integrato backend + database
- `Celery` per task asincroni
- `Redis` come broker e result backend
- `redis.asyncio` per cache applicativa e rate limiting
- logging strutturato con `request_id` propagato

## Struttura logica

Il backend e organizzato a layer:

- `api/`: espone endpoint e dependency
- `core/`: contiene configurazione, database, logging e sicurezza tecnica
- `domain/`: contiene enum, costanti ed eccezioni di dominio
- `models/`: contiene i modelli ORM SQLAlchemy
- `repositories/`: contiene l'accesso ai dati
- `schemas/`: contiene gli schemi Pydantic
- `services/`: contiene i casi d'uso applicativi

## Moduli oggi realmente attivi

### Auth

Gestisce:

- login
- refresh token
- logout
- risoluzione utente corrente

Caratteristiche:

- password hashate
- JWT reali
- refresh token persistiti e revocabili
- audit su login, refresh e logout con `ip_address` e `user_agent` reali
- rate limiting persistito su PostgreSQL per il login con scope `pair`, `identifier`, `ip`
- cooldown con risposta `429` quando una soglia viene superata
- controllo `Origin` / `Referer` sugli endpoint auth cookie-based
- validazione fail-fast della postura di sicurezza in staging e produzione

### Users

Gestisce:

- elenco utenti
- dettaglio utente
- creazione utente
- aggiornamento utente
- cambio stato
- cambio ruolo

Caratteristiche:

- persistenza reale su PostgreSQL
- audit delle operazioni amministrative
- scoping tenant per il ruolo `tenant_admin`

### Admin

Gestisce:

- consultazione audit log

### Tenant Admin

Gestisce:

- consultazione audit locale del tenant corrente
- configurazione aziendale del tenant corrente
- configurazione SMTP del tenant corrente
- numerazioni documentali del tenant corrente

Caratteristiche:

- accesso consentito solo a `tenant_admin`
- filtro automatico sugli utenti appartenenti alla stessa organizzazione
- `tenant_id` risolto dal profilo autenticato
- password SMTP cifrata lato backend

### Reports Async

Gestisce:

- accodamento generazione report lunga
- lettura stato task per il frontend

Caratteristiche:

- task inviati a `Celery`
- stato persistito in `Redis`
- worker eseguito in processo separato da FastAPI
- sessioni SQLAlchemy aperte nel worker tramite context manager dedicato

### Dashboard

Gestisce:

- KPI tenant-aware cacheati
- rate limiting per endpoint ad alta frequenza

Caratteristiche:

- cache Redis isolata per tenant
- chiave `tenant:{tenant_id}:dashboard:kpis`
- TTL default `300` secondi
- invalidazione puntuale sulle mutazioni rilevanti
- invalidazione eseguita in best-effort dopo `commit` delle mutazioni su PostgreSQL

## Avvio locale

### Con `uv`

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --app-dir backend --reload
```

## Check di qualita

Eseguire sempre questi controlli prima di considerare chiusa una modifica backend:

```bash
uv sync --group dev
uv run ruff check app alembic
uv run ruff format --check app alembic
uv run python -m compileall app alembic
uv run python -m pytest
```

Approccio scelto:

- lint leggero ma utile con `ruff`
- check di formattazione non distruttivo
- verifica minima di importabilita Python
- baseline test backend veloce senza dipendere da PostgreSQL o Redis reali

### Con Docker

```bash
docker compose up --build
```

In questo flusso:

1. `db_migrator` esegue `alembic upgrade head`
2. `core_service` parte solo dopo migration riuscita
3. `celery_worker` parte solo dopo migration riuscita

## Credenziali iniziali

Utenti seedati dalla migration iniziale:

- `admin / admin123`
- `tenant.admin / tenant123`
- `user / user123`

Questi utenti esistono nello schema `security.users`.

## Dove si trova cosa

### Configurazione runtime

- [backend/app/core/config.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/config.py)
- [backend/.env.example](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/.env.example)
- [backend/app/core/logging.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/logging.py)
- [backend/app/core/request_id.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/request_id.py)
- [backend/app/core/redis.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/redis.py)
- [backend/app/core/cache.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/cache.py)
- [backend/app/core/rate_limit.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/rate_limit.py)

### Database e sessione

- [backend/app/core/db.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/db.py)

### Migrazioni

- [backend/alembic](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/alembic)
- [backend/alembic/versions/20260515_0001_create_security_schema.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/alembic/versions/20260515_0001_create_security_schema.py)
- [backend/alembic/versions/20260515_0003_add_tenants_and_user_scoping.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/alembic/versions/20260515_0003_add_tenants_and_user_scoping.py)
- [backend/alembic/versions/20260515_0005_add_login_protection.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/alembic/versions/20260515_0005_add_login_protection.py)

### Sicurezza tecnica

- [backend/app/core/security/hashing.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/security/hashing.py)
- [backend/app/core/security/jwt.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/security/jwt.py)
- [backend/app/core/security/field_encryption.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/security/field_encryption.py)
- [backend/app/core/security/request_context.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/security/request_context.py)

### Servizi applicativi

- [backend/app/services/auth/auth_service.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/services/auth/auth_service.py)
- [backend/app/services/auth/login_protection_service.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/services/auth/login_protection_service.py)
- [backend/app/services/dashboard/dashboard_service.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/services/dashboard/dashboard_service.py)
- [backend/app/services/production/production_service.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/services/production/production_service.py)
- [backend/app/services/reports/report_task_service.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/services/reports/report_task_service.py)
- [backend/app/services/users/user_service.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/services/users/user_service.py)
- [backend/app/services/audit/audit_service.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/services/audit/audit_service.py)

### Coda asincrona

- [backend/app/core/celery_app.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/celery_app.py)
- [backend/app/tasks/report_tasks.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/tasks/report_tasks.py)

## Come aggiungere o modificare endpoint

Regole obbligatorie:

- aggiungere o aggiornare lo schema Pydantic
- documentare ogni campo con `Field(description=...)`
- aggiungere `examples`
- usare `response_model`
- definire `status_code`
- definire `responses={...}`
- scrivere docstring endpoint in italiano
- mantenere type hints coerenti

Ordine corretto:

1. schema request/response
2. service applicativo
3. repository se serve persistenza
4. route FastAPI
5. aggiornamento documentazione in `planning/docs`

## Come evolvere il database

Regola:

mai modificare lo schema manualmente.

Flusso corretto:

1. modificare modelli SQLAlchemy
2. creare nuova migration Alembic
3. revisionare la migration
4. applicarla localmente
5. verificare impatto su Docker e documentazione

## Dove prestare attenzione

### Audit

Ogni operazione sensibile deve lasciare traccia.

Prestare attenzione a:

- chi e l'attore
- qual e la risorsa target
- quali dati minimi servono nel `payload_json`
- evitare di loggare segreti o password
- distinguere sempre tra audit globale Gestionale e audit locale tenant
- acquisire sempre `ip_address` e `user_agent` quando il contesto request e disponibile

### JWT e secret

La secret JWT deve essere robusta e mai lasciata a valori deboli in ambienti reali.

Prestare attenzione a:

- lunghezza della secret
- coerenza `issuer`
- durata access token
- durata refresh token
- soglie di `LOGIN_RATE_LIMIT_*`
- messaggi di errore neutri durante i fallimenti di login
- `REFRESH_COOKIE_SECURE=true` in staging e produzione
- `AUTH_ENFORCE_ORIGIN_CHECK=true` in staging e produzione
- `TRUSTED_PROXY_IPS` valorizzato correttamente dietro reverse proxy, altrimenti `X-Forwarded-For` viene ignorato

### Repository vs Service

Il repository non deve contenere logica applicativa.
Il service non deve fare SQL diretto.

### Tenant scoping

Lo scoping tenant deve restare centralizzato nei service.

Prestare attenzione a:

- non demandare il filtro tenant al frontend
- non esporre query utenti globali al ruolo `tenant_admin`
- mantenere `tenant_id` nullo per i super admin globali
- evitare che il `tenant_admin` possa assegnare il ruolo `admin`
- per gli endpoint tenant-aware preferire `RequirePermission(resource, action, ...)` rispetto a check manuali sul ruolo
- il `tenant_id` inviato dal client va trattato come input da validare o cross-checkare, non come fonte di verita
- non restituire segreti tenant in chiaro dalle API

### OpenAPI

Swagger deve restare pulito.

Prestare attenzione a:

- esempi coerenti con il comportamento reale
- descrizioni aggiornate
- status code corretti

### Docker

Oggi il runtime locale separa `db_migrator` da `core_service`.

Prestare attenzione a:

- tempi di bootstrap
- comportamento in ambienti condivisi
- distinzione netta tra migration job e web runtime
- il check container del web deve puntare a `/health/ready`, non a una liveness cieca

### Osservabilita minima

Regole operative:

- propagare sempre `X-Request-ID` verso il client
- includere il `request_id` in tutti i log applicativi
- usare `LOG_JSON=true` in staging/produzione se i log vengono raccolti da sistemi esterni
- distinguere tra:
  - `/health/live`: processo vivo
  - `/health/ready`: web pronto con DB e Redis raggiungibili

### Celery e worker

Regole operative:

- creare l'istanza `Celery` fuori da `main.py`
- non importare l'app FastAPI dentro il worker
- non riusare sessioni database del web server
- aprire sempre una nuova `SessionLocal` dentro task o service usati dal task
- aggiornare lo stato task con `update_state(...)` se il frontend deve mostrare progressi

### Redis cache e rate limiting

Regole operative:

- inizializzare il client Redis asincrono nel `lifespan` FastAPI
- salvare il client in `app.state.redis`
- usare chiavi esplicite e tenant-aware per la cache condivisa
- invalidare la chiave del solo tenant impattato dopo ogni mutazione business rilevante
- non usare la cache come fonte di verita: il dato canonico resta PostgreSQL
- se Redis fallisce in invalidazione dopo un commit DB, non riportare falso rollback applicativo al client
- applicare rate limiting come dependency riusabile, non con logica duplicata nei router

## Come aggiornare il backend in futuro

Quando fai una modifica:

1. aggiorna il codice
2. aggiorna gli schemi OpenAPI
3. aggiorna la documentazione tecnica in `planning/docs`
4. aggiorna `uv.lock` se cambiano dipendenze
5. verifica `uv run ...`
6. verifica `docker compose up --build`

## Protezione login

Il backend applica una protezione basilare del login:

- chiavi di controllo: `identifier + ip_address`, solo `identifier`, solo `ip_address`
- soglia di default: `5` tentativi falliti
- soglia di default per identificativo: `10` tentativi falliti
- soglia di default per IP: `30` tentativi falliti
- finestra di default: `15` minuti
- lockout di default: `15` minuti

Variabili runtime:

- `LOGIN_RATE_LIMIT_MAX_ATTEMPTS`
- `LOGIN_RATE_LIMIT_IDENTIFIER_MAX_ATTEMPTS`
- `LOGIN_RATE_LIMIT_IP_MAX_ATTEMPTS`
- `LOGIN_RATE_LIMIT_WINDOW_MINUTES`
- `LOGIN_RATE_LIMIT_LOCKOUT_MINUTES`
- `AUTH_ALLOWED_ORIGINS`
- `AUTH_ENFORCE_ORIGIN_CHECK`
- `TRUSTED_PROXY_IPS`

Regole operative:

- usare `429` per i tentativi bloccati
- non esporre dettagli che aiutino enumeration o brute force
- mantenere il reset dello stato su login riuscito
- usare `401` generico per credenziali errate o account inattivo
- fidarsi di `X-Forwarded-For` solo dietro proxy esplicitamente noto
- non avviare ambienti staging/produzione con secret JWT placeholder o cookie refresh insicuri

## Hardening produzione

Impostazioni minime richieste in ambienti non development:

- `APP_ENV=staging` o `APP_ENV=production`
- `JWT_SECRET_KEY` reale, non placeholder
- `REFRESH_COOKIE_SECURE=true`
- `AUTH_ENFORCE_ORIGIN_CHECK=true`
- `AUTH_ALLOWED_ORIGINS` esplicito
- `TRUSTED_PROXY_IPS` esplicito se e presente un reverse proxy

Residui ancora non implementati ma raccomandati:

- reuse detection e revoca di famiglia per refresh token
- absolute session timeout indipendente dalla sola rotazione del refresh token
- password breach screening su cambio/reset password
- re-authentication per azioni sensibili future

## Endpoint task asincroni

Endpoint demo attivi:

- `POST /api/v1/reports/generate`
- `GET /api/v1/tasks/{task_id}/status`

Flusso:

1. il client invia `tenant_id`
2. FastAPI valida accesso e tenant
3. il backend restituisce `202 Accepted` con `task_id`
4. il frontend effettua polling leggero
5. il worker aggiorna `progress`, `message` e `result_url`

## RBAC dichiarativo tenant-aware

- il backend dispone gia di catalogo `roles`, `permissions`, `role_permissions`
- per questa fase ERP e preferibile una matrice ruoli/permessi interna rispetto a Casbin: meno moving parts, seed piu semplici, audit piu leggibile
- Casbin ha senso solo quando emergeranno policy dinamiche per reparto, documento o record-level rule molto variabili
- usare `RequirePermission("resource", "action")` come dependency standard
- quando la risorsa e tenant-scoped:
- usare `tenant_field_name` se il `tenant_id` e nella request
- usare `resource_id_param_name` + `tenant_resolver` se il tenant va ricavato dal database
- il controllo tenant deve avvenire prima dell'accesso ai dati applicativi per ridurre il rischio di IDOR

## Endpoint cache e rate limiting

Endpoint demo attivi:

- `GET /api/v1/dashboard/kpis`
- `PUT /api/v1/production/update`

Flusso cache:

1. il backend costruisce la chiave `tenant:{tenant_id}:dashboard:kpis`
2. se Redis contiene gia il payload, il backend risponde dal cache layer
3. se Redis non contiene il payload, il backend legge PostgreSQL
4. il risultato viene serializzato in JSON con TTL di `300` secondi
5. una mutazione di produzione invalida la sola chiave del tenant toccato
6. gli update `company-settings`, `smtp-settings` e `document-sequences` invalidano la stessa chiave KPI del tenant

## Checklist minima prima di chiudere una modifica

- import e compilazione Python ok
- endpoint avviabili
- documentazione Swagger coerente
- migrazioni allineate
- lint e format check backend ok
- documentazione aggiornata
- nessun messaggio descrittivo rimasto obsoleto
