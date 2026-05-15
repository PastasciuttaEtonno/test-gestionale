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
- rate limiting persistito su PostgreSQL per il login
- cooldown basilare con risposta `429` quando la soglia viene superata

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
```

Approccio scelto:

- lint leggero ma utile con `ruff`
- check di formattazione non distruttivo
- verifica minima di importabilita Python

### Con Docker

```bash
docker compose up --build
```

In questo flusso il container backend esegue automaticamente:

1. migration Alembic
2. avvio Uvicorn

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
- [backend/app/services/users/user_service.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/services/users/user_service.py)
- [backend/app/services/audit/audit_service.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/services/audit/audit_service.py)

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
- distinguere sempre tra audit globale Esseduesoft e audit locale tenant
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
- non restituire segreti tenant in chiaro dalle API

### OpenAPI

Swagger deve restare pulito.

Prestare attenzione a:

- esempi coerenti con il comportamento reale
- descrizioni aggiornate
- status code corretti

### Docker

Oggi il container esegue `Alembic` in avvio.

Prestare attenzione a:

- tempi di bootstrap
- comportamento in ambienti condivisi
- eventuale necessità futura di separare migration e runtime

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

- chiave di controllo: `identifier + ip_address`
- soglia di default: `5` tentativi falliti
- finestra di default: `15` minuti
- lockout di default: `15` minuti

Variabili runtime:

- `LOGIN_RATE_LIMIT_MAX_ATTEMPTS`
- `LOGIN_RATE_LIMIT_WINDOW_MINUTES`
- `LOGIN_RATE_LIMIT_LOCKOUT_MINUTES`

Regole operative:

- usare `429` per i tentativi bloccati
- non esporre dettagli che aiutino enumeration o brute force
- mantenere il reset dello stato su login riuscito

## Checklist minima prima di chiudere una modifica

- import e compilazione Python ok
- endpoint avviabili
- documentazione Swagger coerente
- migrazioni allineate
- lint e format check backend ok
- documentazione aggiornata
- nessun messaggio descrittivo rimasto obsoleto
