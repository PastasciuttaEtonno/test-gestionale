# Code Adaptation Plan

## Obiettivo

Tradurre la migrazione Azure in modifiche concrete al codice esistente, evitando di legare il dominio direttamente a `Celery`, `Redis` o a bootstrap specifici di container locali.

## Principio guida

L'applicazione deve poter girare in tre modalita:

- locale `Docker Compose`
- test/CI
- Azure

Questo richiede di separare:

- core domain e servizi applicativi
- adapter infrastrutturali
- runtime entrypoints

## Delta principali sul backend

## 1. Sostituire il coupling diretto a Celery nei servizi applicativi

### Stato attuale

Il servizio [backend/app/services/reports/report_task_service.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/services/reports/report_task_service.py) chiama direttamente:

- `genera_report_massivo_task.delay(...)`
- `AsyncResult(...)`

Questo lega il dominio applicativo a:

- Celery
- broker Redis
- result backend Redis

### Refactor richiesto

Introdurre un contratto applicativo, per esempio:

- `app/services/jobs/job_dispatcher.py`
- `app/services/jobs/job_status_store.py`

Interfacce suggerite:

```python
class JobDispatcher(Protocol):
    async def dispatch_report_generation(self, *, tenant_id: str, requested_by_user_id: str) -> str: ...

class JobStatusStore(Protocol):
    async def create_job(...): ...
    async def mark_running(...): ...
    async def mark_succeeded(...): ...
    async def mark_failed(...): ...
    async def get_job(...): ...
```

Il service `ReportTaskService` deve dipendere da questi contratti, non da Celery.

### Risultato atteso

- backend piu portabile
- Azure Service Bus integrabile come adapter
- test piu semplici con fake dispatcher

## 2. Introdurre una persistenza esplicita dello stato job

### Stato attuale

Lo stato del job asincrono vive di fatto nel result backend Celery.

### Refactor richiesto

Creare una tabella applicativa, ad esempio:

- `job_executions`

Campi minimi:

- `id`
- `tenant_id`
- `job_type`
- `status`
- `progress`
- `requested_by_user_id`
- `payload_json`
- `result_json`
- `error_message`
- `created_at`
- `started_at`
- `completed_at`

File da toccare:

- nuova migration Alembic in `backend/alembic/versions`
- nuovi model/repository/schema/service sotto `backend/app/models`, `repositories`, `schemas`, `services`

### Risultato atteso

- endpoint status indipendente dal broker
- polling frontend piu stabile
- audit e debugging migliori

## 3. Rimpiazzare il task Celery con un command handler riusabile

### Stato attuale

[backend/app/tasks/report_tasks.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/tasks/report_tasks.py) contiene sia:

- logica di orchestrazione stato
- logica del task runtime

### Refactor richiesto

Estrarre la logica business in un modulo puro, ad esempio:

- `backend/app/services/reports/report_generation_handler.py`

Responsabilita:

- validazione input
- caricamento tenant
- esecuzione step
- aggiornamento stato job

Poi creare due adapter:

- adapter locale/Celery temporaneo
- adapter Azure Functions + Service Bus

### Risultato atteso

- una sola logica di business
- nessun fork tra ambiente locale e cloud

## 4. Separare rate limiting e cache dal bootstrap Redis obbligatorio

### Stato attuale

[backend/app/main.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/main.py) fallisce il bootstrap se `Redis` non risponde:

- `await redis_client.ping()`

La readiness stessa dipende da Redis.

### Problema

In Azure, dopo la rimozione di `Celery + Redis broker`, forzare Redis come dipendenza hard del web puo essere uno spreco o un single point inutile.

### Refactor richiesto

Introdurre un livello di configurazione per capacita opzionali:

- `cache_backend = memory | redis | disabled`
- `rate_limit_backend = memory | redis | disabled`

File da rivedere:

- [backend/app/core/config.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/config.py)
- [backend/app/core/redis.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/redis.py)
- [backend/app/main.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/main.py)
- moduli `cache` e `rate_limit`

### Risultato atteso

- Redis non piu obbligatorio
- fallback degradato ma controllato
- readiness coerente con i servizi realmente necessari

## 5. Preparare una modalita di bootstrap per Azure Functions

### Stato attuale

L'entrypoint e `uvicorn app.main:app` nel Dockerfile:

- [backend/Dockerfile](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/Dockerfile)

### Refactor richiesto

Separare:

- factory dell'app FastAPI
- bootstrap locale
- bootstrap Functions

Pattern consigliato:

- creare `create_app()` in `backend/app/main.py` o nuovo modulo `app/bootstrap/web.py`
- aggiungere entrypoint Azure Functions che monti FastAPI tramite adapter compatibile

Output atteso:

- un runtime locale continua a funzionare
- un runtime Azure Functions puo riusare la stessa app

## 6. Rendere la configurazione cloud-native

### Stato attuale

[backend/.env.example](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/.env.example) e ancora centrato su:

- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND_URL`
- `REDIS_URL`

### Refactor richiesto

Aggiungere variabili nuove e deprecare le vecchie:

- `QUEUE_BACKEND=local|service_bus`
- `JOB_STATUS_BACKEND=database`
- `SERVICE_BUS_NAMESPACE_FQDN`
- `SERVICE_BUS_QUEUE_REPORTS`
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_STORAGE_ACCOUNT_URL` se servono artefatti o blob
- `APIM_EXPECTED_HEADER_*` solo se necessario per trust esplicito

Separare chiaramente:

- env locale
- env CI
- env Azure

## 7. Allineare il frontend al gateway

### Stato attuale

[frontend/src/lib/http.js](/c:/Users/ivan.lisciotto_webra/Desktop/project/frontend/src/lib/http.js) punta a:

- `VITE_API_BASE_URL || "/api/v1"`

### Refactor richiesto

Formalizzare gli environment frontend:

- locale: `/api/v1`
- staging/prod Azure: `https://api.<domain>/api/v1`

Task:

- introdurre file `.env` per ambiente nel frontend
- aggiornare documentazione deploy frontend
- verificare cookie policy cross-site se frontend e API stanno su sottodomini diversi

## 8. Gestire correttamente proxy, host e schema

### Stato attuale

L'app usa `request.client.host`, ma non emerge ancora una strategia completa per:

- `X-Forwarded-For`
- `X-Forwarded-Proto`
- host canonicale dietro APIM

### Refactor richiesto

Definire trusted proxy e header policy in:

- configurazione
- middleware
- logging
- security checks origin/cookie

Questo e importante per:

- audit affidabile
- cookie secure
- redirect corretti
- rate limiting per IP

## 9. Observability applicativa

### Refactor richiesto

Aggiungere:

- correlation tra `request_id` HTTP e `job_id`
- log strutturati coerenti per enqueue, consume, fail, complete
- telemetry hook per Azure Monitor / Application Insights

File da estendere:

- [backend/app/core/logging.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/logging.py)
- [backend/app/main.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/main.py)
- nuovi moduli job

## 10. Test da introdurre o aggiornare

### Nuovi test backend

- unit test su dispatcher fake
- unit test su job status store
- test integrazione endpoint report senza Celery reale
- test fallback senza Redis
- test configurazione Azure-specifica

File di riferimento per stile test esistente:

- [backend/tests/test_auth_routes.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/tests/test_auth_routes.py)
- [backend/tests/test_health.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/tests/test_health.py)

## Sequenza di refactor consigliata

1. introdurre tabella `job_executions`
2. introdurre interfacce `JobDispatcher` e `JobStatusStore`
3. spostare la business logic del report in un handler puro
4. fare adattare `ReportTaskService` ai nuovi contratti
5. mantenere per poco un adapter Celery di compatibilita
6. introdurre adapter Service Bus
7. rendere Redis opzionale
8. aggiungere bootstrap Azure Functions
9. eliminare definitivamente il coupling a Celery dove non serve piu

## Deliverable di codice attesi

- nuovo modulo job runtime-agnostic
- nuova persistenza stato job
- nuova config Azure-oriented
- nuovo bootstrap Functions
- revisione health/readiness
- rimozione progressiva di `Celery` dal path principale
