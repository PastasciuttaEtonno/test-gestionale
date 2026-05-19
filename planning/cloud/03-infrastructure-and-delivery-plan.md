# Infrastructure And Delivery Plan

## Obiettivo

Descrivere come creare e governare l'infrastruttura Azure senza dipendere da operazioni manuali di portale come sorgente di verita.

## Regola operativa

La console Azure serve per:

- verificare
- osservare
- fare incident response

La creazione e la configurazione devono vivere in codice.

## Scelta IaC

Scelta consigliata:

- `Bicep` come baseline Azure-native

Struttura suggerita nel repository:

- `infra/bicep/modules/`
- `infra/bicep/envs/dev/`
- `infra/bicep/envs/staging/`
- `infra/bicep/envs/prod/`

Motivo:

- integrazione naturale con Azure
- curva piu breve di Terraform per un solo sviluppatore se il target e principalmente Azure

## Risorse da provisionare

## 1. Resource groups

Separazione minima:

- `rg-esseduesoft-shared-<env>`
- `rg-esseduesoft-app-<env>`
- `rg-esseduesoft-data-<env>`

## 2. Networking

Componenti:

- VNet
- subnet per Function integration
- subnet delegata PostgreSQL
- subnet private endpoints
- Private DNS zones

Oggetti da codificare:

- address spaces
- subnet delegation
- NSG di base
- private DNS link

## 3. Compute

Componenti:

- Function App HTTP
- eventuale Function App worker
- storage account richiesto da Functions
- Application Insights
- Log Analytics Workspace

## 4. Integration

Componenti:

- Service Bus namespace
- queue `reports`
- eventuali queue future per email, export, sync
- dead-letter policy

## 5. API Layer

Componenti:

- APIM instance
- API import o definizione
- named values
- policy XML o template policy
- backend definitions

## 6. Data

Componenti:

- PostgreSQL Flexible Server
- database
- private DNS zone
- backup retention
- server parameters se necessari

## 7. Secrets

Componenti:

- Key Vault
- managed identities
- role assignment

## 8. Frontend

Componenti minimi:

- hosting statico
- custom domain
- TLS

Se non si vuole gestire anche questo nella prima iterazione, va comunque documentato come modulo IaC separato.

## Naming convention

Standard minimo:

- `esd-<env>-<service>-<region>`

Esempi:

- `esd-dev-apim-italynorth`
- `esd-dev-fn-http-italynorth`
- `esd-dev-sb-italynorth`
- `esd-dev-psql-italynorth`

## Environment strategy

Per la fase iniziale:

- `dev`
- `prod`

Solo dopo il primo go-live:

- introdurre `staging` separato se il budget lo consente

## Delivery pipeline target

## 1. CI

Mantenere l'attuale pipeline controlli e aggiungere:

- test backend
- build artefatti Functions
- validazione Bicep
- lint Bicep

## 2. Image strategy

Avete oggi una pipeline container-oriented.

Decisione da prendere per Azure:

- se si va davvero su `Functions Flex Consumption`, il path principale non deve dipendere dal deploy di un container `uvicorn`

Quindi la pipeline va evoluta da:

- publish backend image

a:

- package backend function app
- deploy function app code
- opzionalmente mantenere image build solo per locale o fallback container runtime

## 3. CD Azure

Nuovi workflow suggeriti:

- `.github/workflows/validate-azure-infra.yml`
- `.github/workflows/deploy-azure-infra.yml`
- `.github/workflows/deploy-backend-azure.yml`
- `.github/workflows/deploy-frontend-azure.yml`

## 4. Secret management

GitHub Secrets minimi:

- credenziali federate o service principal per deploy Azure
- subscription id
- tenant id
- environment specific variables non sensibili via repo vars

Target corretto:

- `OIDC` GitHub Actions verso Azure
- evitare secret statici lunghi dove possibile

## 5. Configuration delivery

Le app settings delle Functions non devono essere configurate a mano una per una da portale.

Devono essere:

- dichiarate in Bicep quando non sensibili
- valorizzate via Key Vault reference quando sensibili

## Strategia APIM

## Import API

Opzioni:

- import da OpenAPI generato
- definizione API in file versionati

Scelta pragmatica:

- generare OpenAPI dal backend
- versionare il file
- importarlo o sincronizzarlo da pipeline

## Policy minime APIM

- enforcement HTTPS
- header forwarding
- correlation id pass-through
- rate limit by key
- eventuale JWT validation
- response header hardening

## Strategia DB migrations

Le migration Alembic non devono dipendere dal bootstrap del web.

Pattern consigliato:

- job pipeline dedicato
- step esplicito pre-deploy o deploy-time controllato

Fasi:

1. deploy infrastruttura se serve
2. applicare migrations
3. deployare runtime HTTP
4. deployare consumer
5. eseguire smoke tests

## Smoke tests post-deploy

Minimi:

- `GET /health`
- `GET /health/ready`
- login
- endpoint business autorizzato
- enqueue report
- lettura status job

## Runbook essenziali da produrre dopo la prima implementazione

- deploy standard
- rollback applicativo
- rotate secret
- disable public exposure in incident
- verifica code bloccate
- verifica DLQ
- verifica connessione DB privata

## Modifiche richieste ai workflow esistenti

### Workflow da superare

[.github/workflows/deploy-backend-aruba.yml](/c:/Users/ivan.lisciotto_webra/Desktop/project/.github/workflows/deploy-backend-aruba.yml)

Motivo:

- e orientato a SSH su host singolo
- presuppone Docker Compose remoto
- presuppone `celery_worker`

### Workflow da evolvere

[.github/workflows/publish-backend-image.yml](/c:/Users/ivan.lisciotto_webra/Desktop/project/.github/workflows/publish-backend-image.yml)

Motivo:

- puo restare utile nel breve come fallback
- ma il percorso Azure serverless deve avere una pipeline propria

## Deliverable infrastrutturali attesi

- modulo Bicep networking
- modulo Bicep Functions
- modulo Bicep Service Bus
- modulo Bicep PostgreSQL
- modulo Bicep APIM
- pipeline validazione IaC
- pipeline deploy IaC
- pipeline deploy app backend
- pipeline smoke test post-deploy
