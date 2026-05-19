# Azure Rollout Backlog

## Obiettivo

Tradurre la migrazione Azure in un backlog ordinato, con deliverable chiari e dipendenze realistiche.

## Fase 0 - Decisioni bloccanti

### Priorita

- `P0`

### Task

- confermare `APIM Standard v2`
- confermare `Functions Flex Consumption`
- decidere se `Service Bus` parte subito in `Premium` o temporaneamente in `Standard`
- confermare `PostgreSQL Flexible Server` con `private access`
- decidere hosting frontend

### Exit criteria

- una pagina di ADR o decision log con le 5 scelte fissate

## Fase 1 - Refactor applicativo per portabilita cloud

### Priorita

- `P0`

### Task

- introdurre `job_executions` nel dominio
- estrarre interfacce `JobDispatcher` e `JobStatusStore`
- spostare la business logic report in un handler runtime-agnostic
- adattare `ReportTaskService` al nuovo modello
- introdurre bootstrap `create_app()`
- rendere Redis opzionale
- rivedere readiness per dipendenze opzionali

### File principali impattati

- [backend/app/services/reports/report_task_service.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/services/reports/report_task_service.py)
- [backend/app/tasks/report_tasks.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/tasks/report_tasks.py)
- [backend/app/core/config.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/config.py)
- [backend/app/main.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/main.py)
- [backend/.env.example](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/.env.example)

### Exit criteria

- il backend non dipende piu direttamente da `Celery` nei service applicativi
- lo stato job e leggibile da DB

## Fase 2 - Adapter Azure

### Priorita

- `P0`

### Task

- creare adapter `ServiceBusJobDispatcher`
- creare Function consumer per la queue `reports`
- creare adapter di status store su PostgreSQL
- introdurre telemetry/correlation sui job

### Exit criteria

- un report puo essere accodato senza `Celery`
- il consumer puo elaborare il messaggio e aggiornare stato job

## Fase 3 - Infrastructure as Code

### Priorita

- `P0`

### Task

- creare cartella `infra/bicep`
- modellare VNet, subnet, DNS privato
- modellare PostgreSQL private access
- modellare Service Bus
- modellare Function App e dipendenze
- modellare APIM
- modellare Key Vault e identita

### Exit criteria

- l'intero ambiente `dev` puo essere creato da pipeline

## Fase 4 - CI/CD Azure

### Priorita

- `P0`

### Task

- aggiungere workflow validazione Bicep
- aggiungere workflow deploy infra
- aggiungere workflow deploy backend Azure
- aggiungere workflow smoke tests
- introdurre OIDC GitHub -> Azure

### Exit criteria

- un deploy su `dev` non richiede portale o SSH manuale

## Fase 5 - Hardening sicurezza

### Priorita

- `P1`

### Task

- chiudere accessi pubblici non necessari
- introdurre Key Vault references
- verificare trusted proxies e forwarded headers
- rivedere cookie secure/samesite con domini reali
- configurare throttling APIM
- verificare RBAC Azure per identita gestite

### Exit criteria

- superficie pubblica limitata a frontend e APIM
- servizi dati raggiungibili solo in rete privata

## Fase 6 - Frontend cutover

### Priorita

- `P1`

### Task

- definire `VITE_API_BASE_URL` ambiente-specifica
- testare login, refresh cookie e logout su domini reali
- verificare CORS e origin enforcement
- allineare documentazione deploy frontend

### File principali impattati

- [frontend/src/lib/http.js](/c:/Users/ivan.lisciotto_webra/Desktop/project/frontend/src/lib/http.js)

### Exit criteria

- il frontend parla solo con APIM
- il flusso auth completo funziona in Azure

## Fase 7 - Decommission componenti legacy

### Priorita

- `P1`

### Task

- rimuovere `celery_worker` dal path di produzione
- deprecare `CELERY_BROKER_URL` e `CELERY_RESULT_BACKEND_URL`
- aggiornare `docker-compose.yml` per il nuovo modello locale
- aggiornare documentazione backend e runbook
- archiviare workflow Aruba

### File principali impattati

- [docker-compose.yml](/c:/Users/ivan.lisciotto_webra/Desktop/project/docker-compose.yml)
- [backend/pyproject.toml](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/pyproject.toml)
- [.github/workflows/deploy-backend-aruba.yml](/c:/Users/ivan.lisciotto_webra/Desktop/project/.github/workflows/deploy-backend-aruba.yml)

### Exit criteria

- il percorso standard non dipende piu da `Celery + Redis broker`

## Backlog tecnico puntuale

### Backend

- aggiungere model e migration `job_executions`
- aggiungere repository stato job
- aggiungere schemi response per job status
- aggiungere abstraction layer queue
- aggiungere adapter Azure Service Bus
- aggiungere bootstrap Azure Functions
- rendere opzionale il client Redis
- rivedere healthcheck
- introdurre trace `request_id` -> `job_id`

### Frontend

- parametrizzare meglio `VITE_API_BASE_URL`
- gestire scenario domini distinti frontend/api
- aggiungere smoke test auth end-to-end

### DevOps

- creare `infra/bicep`
- aggiungere workflow deploy Azure
- aggiungere smoke tests post-deploy
- introdurre convenzioni di naming e tagging risorse

### Security

- mappa secret per ambiente
- Key Vault
- managed identity
- APIM policies
- network isolation verificata

## Rischi di rollout

- tentare il passaggio a Azure senza prima decouplare il modello async
- lasciare readiness hard-coupled a Redis
- migrare il deploy senza una strategia chiara per le migration DB
- non testare il flusso cookie su domini veri
- usare APIM come mero reverse proxy e non come boundary di sicurezza

## Sequenza minima consigliata per partire subito

1. aprire branch dedicato `azure-foundation`
2. implementare `job_executions`
3. astrarre `ReportTaskService`
4. introdurre adapter Service Bus
5. creare `infra/bicep/dev`
6. creare pipeline deploy `dev`
7. testare login e report async in Azure
8. solo dopo pianificare il primo ambiente `prod`
