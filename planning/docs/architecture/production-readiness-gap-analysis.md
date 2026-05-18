# Production Readiness Gap Analysis

## Obiettivo

Tradurre lo stato attuale della demo tecnica in una mappa pragmatica di cio che manca per arrivare a un rilascio reale `prod-ready`, mantenendo il progetto gestibile da un unico sviluppatore.

## Executive Summary

L'architettura corrente e una buona base per un ERP SaaS multitenant moderno:

- backend `FastAPI + Pydantic + SQLAlchemy + PostgreSQL`
- migrazioni schema con `Alembic`
- code asincrone con `Celery + Redis`
- cache applicativa e rate limiting con `redis.asyncio`
- frontend `Vue 3 + Pinia + Axios`
- runtime coerente con `Docker Compose`
- pipeline CI minima con GitHub Actions

### Interazione dei moduli attuali

- `Auth` autentica l'utente, emette `JWT`, ruota refresh token persistiti e applica hardening base.
- `RBAC` controlla ruoli, permessi e scoping tenant-aware tramite dependency dichiarative.
- `PostgreSQL` resta la fonte canonica dei dati.
- `Redis` viene usato per:
  - cache KPI tenant-aware
  - rate limiting endpoint ad alta frequenza
  - broker e result backend dei task async
- `Celery` esegue lavori lunghi in processi separati dal web server.
- `Pinia` mantiene in memoria sessione, ruolo e permessi del frontend.
- `Axios` si occupa di allegare l'access token e tentare il refresh automatico da cookie `HttpOnly`.

### Valutazione sintetica

- lo stack e corretto
- l'approccio `modular monolith` e corretto
- la separazione tra web, cache, queue e DB e corretta
- la demo e tecnicamente credibile
- il salto verso produzione non richiede cambiare stack, ma aggiungere disciplina operativa, osservabilita, test, audit business e delivery controllata

## Delta Verso la Produzione

## 1. Audit Logs e Tracciabilita Business

### Stato attuale

Esiste gia audit su:

- login
- refresh
- logout
- operazioni amministrative utenti
- audit globale super admin
- audit locale tenant

### Gap reale

Per un ERP questo non basta. In produzione servono audit forensi sul dominio business:

- chi ha modificato la risorsa
- quale risorsa
- quando
- prima e dopo
- tenant
- request id
- origine tecnica quando disponibile

### Strategia consigliata

Usare audit applicativo esplicito nei service, non solo listener ORM impliciti.

Pattern consigliato:

1. tabella dedicata `audit_events`
2. snapshot `before_json` e `after_json`
3. campi standard:
   - `tenant_id`
   - `actor_user_id`
   - `resource_type`
   - `resource_id`
   - `action`
   - `before_json`
   - `after_json`
   - `metadata_json`
   - `request_id`
   - `created_at`
4. commit unico tra mutazione e audit

### Best practice 2026

- audit semantico nel service
- listener SQLAlchemy solo per metadata tecnici come timestamp o `updated_by`
- introdurre `version` integer sulle entita business sensibili per optimistic locking
- non loggare segreti, password o payload eccessivi

## 2. Strategia CI/CD

### Stato attuale

Esiste CI minima per:

- lint backend
- format check backend
- importability backend
- lint frontend
- build frontend

### Gap reale

Manca una pipeline di delivery completa:

- build immagini versionate
- push su registry
- deploy automatico su Aruba
- rollback
- migration controllate
- healthcheck post-deploy

### Strategia consigliata per un solo sviluppatore

Non introdurre Kubernetes.

Target pragmatico:

- VM Aruba Cloud
- `Docker` / `docker compose`
- reverse proxy `Traefik` o `Nginx`
- GitHub Actions per build e deploy via SSH

### Flusso raccomandato

1. push su `main`
2. GitHub Actions esegue:
   - quality gate
   - build immagini Docker taggate con SHA
   - push su registry
3. job deploy:
   - SSH sulla VM
   - pull nuove immagini
   - run migration come job separato
   - restart controllato web e worker
   - verifica healthcheck

### Nota pratica GHCR

Per la publication da GitHub Actions non serve introdurre subito un PAT custom se il repository usa:

- `GITHUB_TOKEN`
- job permissions corrette
- `Workflow permissions = Read and write` nel repository

Il PAT serve invece lato server Aruba per il pull di immagini private da `GHCR`, tipicamente con scope minimo:

- `read:packages`

### Obiettivo zero-downtime pragmatico

- almeno 2 istanze web dietro proxy
- restart una istanza alla volta
- migration backward-compatible
- worker separati dal web
- niente auto-migration implicita all'avvio del web in produzione

## 3. Gestione Errori e Monitoraggio

### Stato attuale

Esistono:

- healthcheck base
- logging applicativo basilare
- distinzione chiara dei componenti runtime

### Gap reale

Manca osservabilita production-grade:

- error tracking
- log centralizzati
- correlation id
- metriche
- alerting

### Stack minimo raccomandato

- `Sentry` backend e frontend
- log JSON strutturati su stdout
- request id / correlation id propagato
- dashboard minima con:
  - uptime
  - 5xx rate
  - latency
  - queue depth Celery
  - job failures
  - cache hit/miss
  - stato Redis/Postgres

### Best practice 2026

- ogni request deve avere un `request_id`
- ogni errore non gestito deve finire su Sentry
- i log devono essere machine-readable
- worker Celery deve avere heartbeat/health dedicato
- introdurre alert minimi prima del go-live

## 4. Database Migrations in Produzione

### Stato attuale

Le migration Alembic sono gia parte del flusso e oggi vengono eseguite in bootstrap container.

### Gap reale

Questo approccio non va bene a lungo in produzione con clienti reali.

Rischi:

- race condition tra istanze
- startup piu fragili
- deployment poco prevedibili
- lock schema in momenti sbagliati

### Strategia corretta

Separare:

- fase migration
- fase startup applicativa

### Regole operative

- migration piccole
- backward-compatible
- additive-first
- drop e rename solo in release successive
- backfill pesanti fuori dal path di bootstrap

### Pattern consigliato

1. deploy codice compatibile con vecchio e nuovo schema
2. eseguire migration
3. attivare nuova logica
4. rimuovere compatibilita legacy in release successiva

### Per clienti h24

- evitare lock lunghi
- evitare migrazioni distruttive one-shot
- usare finestre controllate solo per cambi eccezionali
- validare sempre su staging

## 5. Internazionalizzazione e Localizzazione

### Stato attuale

La demo e di fatto italiana-first, con contenuti descrittivi e formati ancora non strutturati per multi-locale.

### Gap reale

Un ERP multistabilimento reale richiede:

- lingua UI
- timezone tenant
- timezone utente
- valuta base tenant
- formati data/ora/locali
- formati numerici
- codici valuta ISO

### Strategia consigliata

Backend:

- salvare timestamp in UTC
- salvare importi in decimal
- salvare currency code separato
- introdurre configurazione tenant:
  - `default_locale`
  - `default_timezone`
  - `base_currency`

Frontend:

- formattazione per locale
- chiavi traduzione fin dall'inizio
- override opzionale per utente

### Approccio pragmatico

- non tradurre subito tutto
- preparare prima l'architettura
- localizzare prima date, ore, numeri e valute
- mantenere l'italiano come default iniziale

## 6. Altri Gap Architetturali Critici

### Test automatici reali

Mancano ancora:

- unit test selettivi
- integration test API
- test auth/RBAC/tenant isolation
- smoke test deploy
- test worker/task

### Backup e Disaster Recovery

Servono:

- backup automatici PostgreSQL
- test di restore periodici
- retention policy
- runbook di recovery

### Gestione segreti

Servono:

- secret reali fuori dal repo
- rotazione credenziali
- separazione `dev`, `staging`, `prod`

### Session e auth hardening residuo

Restano raccomandati:

- refresh token family reuse detection
- revoca di famiglia
- absolute session timeout
- password breach screening su cambio/reset
- re-authentication per azioni sensibili future

### Concurrency e consistenza

Per i moduli ERP reali serviranno:

- optimistic locking
- eventuale idempotency key su operazioni sensibili
- policy chiare su retry e duplicate submission

## Roadmap di Rilascio

## Fase 1: Blindatura Demo

Obiettivo: rendere la demo affidabile e tecnicamente difendibile.

Checklist:

- aggiungere test API su auth, refresh, RBAC e tenant isolation
- aggiungere test su cache hit/miss e invalidazione tenant
- aggiungere test su task async e polling
- integrare `Sentry` backend e frontend
- introdurre logging JSON con `request_id`
- introdurre runbook minimi di deploy, rollback e restore
- separare seed demo da assetto runtime reale
- preparare backup e prova restore locale
- introdurre healthcheck distinti per web, worker, Redis e Postgres

## Fase 2: Predisposizione Prod

Obiettivo: rendere il progetto rilasciabile in modo prevedibile.

Checklist:

- pipeline GitHub Actions con build immagini Docker e push registry
- deploy Aruba via SSH automatizzato
- migration Alembic come job separato
- reverse proxy con TLS e healthcheck
- gestione segreti prod fuori dal repository
- staging coerente con la produzione
- tabella audit business unificata
- metriche e alert minimi
- supporto base a locale/timezone/currency per tenant
- eliminazione della auto-migration in startup del web container

## Fase 3: Go-Live su Aruba

Obiettivo: primo rilascio controllato a tenant reali.

Checklist:

- almeno 2 istanze web dietro proxy
- worker Celery separato e monitorato
- backup automatici con restore verificato
- monitor uptime e alert attivi
- procedura rollback documentata e provata
- migration backward-compatible verificate su staging
- TLS e hardening edge corretti
- onboarding di un tenant pilota
- finestra di supporto post-go-live
- incident response minima documentata

## Priorita Consigliata Per Un Solo Sviluppatore

Ordine raccomandato:

1. test automatici reali
2. osservabilita minima
3. pipeline di publication immagini e migration discipline
4. audit business serio
5. primi moduli business reali

## Decisione CTO Pragmatica

Non serve cambiare stack.

Scelte consigliate:

- mantenere `modular monolith`
- mantenere `FastAPI + PostgreSQL`
- mantenere `Celery + Redis`
- mantenere `Vue 3 + Pinia`
- evitare `Kubernetes` in questa fase
- evitare motori policy esterni come `Casbin` finche il modello resta gestibile con ruoli e permessi interni

Il rischio principale non e tecnologico: e operativo.

Il progetto diventa veramente `prod-ready` quando:

- il deploy e ripetibile
- le migration sono disciplinate
- gli errori si vedono subito
- gli audit sono completi
- il restore e provato
- i moduli business iniziano a nascere sopra fondamenta stabili
