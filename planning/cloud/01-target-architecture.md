# Target Architecture Azure

## Obiettivo

Definire la topologia Azure di arrivo, con particolare attenzione a:

- isolamento di rete
- costi fissi bassi nella fase di lancio
- aderenza al codice e ai workflow gia presenti
- mantenibilita da parte di un solo sviluppatore

## Stato attuale rilevato nel repository

Backend:

- `FastAPI` asincrono in [backend/app/main.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/main.py)
- `SQLAlchemy + Alembic`
- autenticazione JWT dual-token
- `Celery` in [backend/app/core/celery_app.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/celery_app.py)
- `Redis` condiviso per cache, rate limiting e broker in [backend/app/core/redis.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/redis.py)
- Docker runtime in [backend/Dockerfile](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/Dockerfile) e [docker-compose.yml](/c:/Users/ivan.lisciotto_webra/Desktop/project/docker-compose.yml)

Frontend:

- Vue 3
- API client con `VITE_API_BASE_URL` in [frontend/src/lib/http.js](/c:/Users/ivan.lisciotto_webra/Desktop/project/frontend/src/lib/http.js)

CI/CD:

- build immagine backend su GHCR in [.github/workflows/publish-backend-image.yml](/c:/Users/ivan.lisciotto_webra/Desktop/project/.github/workflows/publish-backend-image.yml)
- deploy Aruba esistente in [.github/workflows/deploy-backend-aruba.yml](/c:/Users/ivan.lisciotto_webra/Desktop/project/.github/workflows/deploy-backend-aruba.yml)

## Principio architetturale

Il progetto non deve diventare un sistema distribuito complesso solo per "sembrare enterprise".

La scelta corretta e:

- `modular monolith` applicativo
- separazione infrastrutturale tra ingress, compute, queue e database
- servizi gestiti al posto di cluster auto-gestiti
- codice astratto dai provider dove il coupling attuale e troppo forte

## Architettura target

### 1. Frontend

Target consigliato:

- hosting statico Azure dedicato al frontend
- dominio pubblico separato dal backend
- `VITE_API_BASE_URL` puntato ad APIM, non direttamente alle Functions

Pattern:

- browser -> frontend statico
- frontend -> `https://api.<domain>` gestito da APIM

### 2. API Gateway

Servizio:

- `Azure API Management Standard v2`

Ruolo:

- unico ingresso pubblico API
- TLS terminator
- rate limiting gateway-level
- validazione JWT dove utile
- header forwarding coerente
- observability cross-request

Motivi della scelta:

- puo raggiungere backend in VNet
- e produzione-ready
- evita di esporre direttamente le Function App come origin principale

Scelta esplicita da non fare in questa fase:

- non usare `APIM Consumption` come tier principale se il backend deve restare realmente dietro rete privata

### 3. Compute Backend

Servizio:

- `Azure Functions Flex Consumption`

Pattern applicativo:

- una Function App per l'entrypoint HTTP
- una seconda Function App per workload asincroni/consumer, se il carico o la separazione operativa lo richiedono

Motivi:

- costo variabile e basso al lancio
- supporto a VNet integration
- adatto a backend con traffico irregolare

Vincolo importante:

- l'app deve essere adattata a runtime Functions e non puo restare semplicemente un container `uvicorn` se si vuole sfruttare pienamente il modello serverless scelto

### 4. Messaggistica

Servizio:

- `Azure Service Bus`

Uso previsto:

- comandi asincroni
- job lunghi
- eventi applicativi interni
- retry e dead-lettering

Decisione tier:

- `Standard` solo se si accetta endpoint pubblico protetto
- `Premium` se il requisito "tutto privato" per i servizi interni e non negoziabile

Dato il requisito espresso nel progetto, la linea corretta e:

- backlog e codice compatibili con `Premium`
- eventuale partenza temporanea in `Standard` solo come concessione economica, dichiarata e tracciata

### 5. Database

Servizio:

- `Azure Database for PostgreSQL Flexible Server`

Scelta iniziale:

- `private access`
- SKU `Burstable` in fase launch
- niente HA in prima fase se il budget e stretto

Conseguenza:

- il database resta raggiungibile solo da subnet abilitate
- la VNet diventa parte integrante del provisioning

### 6. Cache

Decisione iniziale:

- non introdurre Redis gestito come prerequisito del go-live Azure

Motivo:

- oggi `Redis` e usato per tre responsabilita diverse
- cache KPI
- rate limiting
- broker/result backend Celery

Il refactor corretto e separare le responsabilita:

- queue -> `Service Bus`
- stato job -> database o store dedicato applicativo
- rate limiting -> APIM + fallback applicativo
- cache KPI -> memory cache locale o cache opzionale esterna

## Topologia di rete target

### Pubblico

- `443` su APIM
- `443` su frontend statico

### Privato

- subnet integration per Function Apps
- subnet delegata per PostgreSQL Flexible Server
- private endpoint per Service Bus se tier `Premium`
- Private DNS per risoluzione interna

### Regola di accesso

- nessun database esposto pubblicamente
- nessun broker esposto pubblicamente se si sceglie la variante hardening completa
- backend non usato come origin internet-facing primario

## Flussi applicativi principali

### Flusso autenticazione

1. browser chiama APIM
2. APIM inoltra alla Function HTTP
3. backend autentica contro PostgreSQL
4. access token in memoria client
5. refresh token in cookie `HttpOnly`

### Flusso comando business sincrono

1. browser -> APIM
2. APIM -> Function HTTP
3. Function -> PostgreSQL
4. risposta immediata

### Flusso job asincrono

1. browser richiede generazione report
2. Function HTTP valida e persiste il job
3. Function pubblica un messaggio su Service Bus
4. Function consumer elabora il job
5. stato job aggiornato su database
6. frontend interroga uno status endpoint o usa polling

## Decisioni di design da fissare ora

### Decisione 1

Non portare `Celery` su Azure come dipendenza permanente.

Motivo:

- aggiunge complessita operativa inutile
- conserva un coupling forte a Redis
- peggiora il vantaggio del passaggio a servizi nativi Azure

### Decisione 2

Non usare i result backend effimeri come fonte di verita dello stato job.

Motivo:

- in un ERP gli utenti devono poter ritrovare lo stato di elaborazioni e report
- lo stato deve vivere in persistenza applicativa

### Decisione 3

Tenere separati i confini:

- dominio applicativo
- adapter infrastrutturali
- bootstrap runtime

Motivo:

- serve per supportare locale, test e Azure senza fork logici del dominio

## Rischi architetturali principali

- migrare a Functions senza introdurre un adapter layer e rompere test e struttura attuale
- lasciare `Celery` nel dominio e rendere il backend dipendente da due modelli asincroni contemporaneamente
- usare APIM come semplice proxy senza sfruttarlo per policy, throttling e sicurezza
- dipendere da `Redis` anche quando non serve piu come broker
- fare provisioning manuale e rendere l'ambiente non riproducibile

## Obiettivo di arrivo realistico

La versione Azure iniziale deve essere:

- economicamente leggera
- privata lato database
- privata lato code appena il budget lo consente
- osservabile
- automatizzabile da repository
- reversibile tramite rollout a fasi
