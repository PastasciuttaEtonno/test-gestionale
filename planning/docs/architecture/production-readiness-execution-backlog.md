# Production Readiness Execution Backlog

## Obiettivo

Tradurre la gap analysis di produzione in un backlog breve, ordinato e realmente eseguibile da un solo sviluppatore.

## Principi di priorita

L'ordine non segue il fascino tecnico, ma il rischio operativo:

1. rendere il rilascio ripetibile
2. rendere i secret gestibili senza scorciatoie pericolose
3. rendere gli errori visibili subito

## Stato di partenza

Gia presenti:

- quality gate minimo con GitHub Actions
- publication backend su `GHCR`
- migration discipline iniziale con `db_migrator`
- logging strutturato e `request_id`
- health endpoint backend

Ancora assenti:

- deploy Aruba via SSH
- secret discipline reale per ambienti runtime
- osservabilita production-grade con error tracking e monitor worker

## Step 1: Deploy Discipline Aruba

### Priorita

- `P0`

### Motivo

Senza deploy ripetibile, il progetto non e rilasciabile in modo sicuro anche se il codice e corretto.

### Obiettivo

Portare il progetto da "immagine pubblicata" a "rilascio eseguibile in staging/prod con procedura coerente".

### Scope

- workflow GitHub Actions di deploy manuale via `workflow_dispatch`
- connessione SSH alla VM Aruba
- `docker login ghcr.io` sul server
- pull immagine backend per tag esplicito
- esecuzione migration separata
- restart controllato di `core_service` e `celery_worker`
- verifica healthcheck post-deploy

### Deliverable attesi

- workflow `.github/workflows/deploy-backend-aruba.yml`
- checklist secret GitHub necessari
- procedura rollback minima a tag precedente
- documentazione operativa Aruba aggiornata

### Dipendenze

- package backend gia pubblicato su `GHCR`
- accesso SSH Aruba disponibile
- utente o service account GitHub con PAT `read:packages` per il server

### Effort stimato

- `M`

### Criterio di chiusura

- un deploy manuale backend puo essere lanciato da GitHub Actions
- il server esegue pull, migration e restart senza step manuali fuori workflow
- il backend risponde `200` su healthcheck finale

## Step 2: Secrets Management Baseline

### Priorita

- `P0`

### Motivo

Il deploy senza gestione segreti corretta porta rapidamente a configurazioni fragili o insicure.

### Obiettivo

Definire una disciplina minima per secret applicativi e infrastrutturali, distinta per ambiente.

### Scope

- censimento secret correnti:
  - DB
  - JWT
  - SMTP
  - GHCR pull
  - SSH deploy
- tabella sorgente/ownership dei secret
- distinzione `dev`, `staging`, `prod`
- naming coerente dei GitHub Secrets
- regole minime di rotazione
- esclusione completa dei secret runtime dal repository

### Deliverable attesi

- documento operativo con matrice secret
- elenco GitHub Secrets richiesti per deploy Aruba
- aggiornamento `.env.example` solo come schema, non come sorgente di verita prod

### Dipendenze

- definizione del primo workflow deploy Aruba

### Effort stimato

- `S-M`

### Criterio di chiusura

- ogni secret critico ha un owner e un punto di caricamento definito
- il deploy Aruba non dipende da credenziali lasciate in shell history o file locali improvvisati

## Step 3: Observability Production-Grade Minima

### Priorita

- `P1`

### Motivo

Una volta che il deploy esiste, il rischio successivo e non accorgersi di errori, task falliti o degradi.

### Obiettivo

Completare l'osservabilita minima per backend, frontend e worker.

### Scope

- integrazione `Sentry` backend
- integrazione `Sentry` frontend
- healthcheck dedicato worker Celery
- log chiari su task falliti
- base documentale per alert minimi

### Deliverable attesi

- configurazione Sentry backend
- configurazione Sentry frontend
- endpoint o check worker documentato
- runbook minimo di triage errori

### Dipendenze

- secret management baseline disponibile

### Effort stimato

- `M`

### Criterio di chiusura

- un errore backend non gestito arriva a Sentry
- un errore frontend significativo arriva a Sentry
- esiste un modo documentato per capire se il worker e vivo o degradato

## Step volutamente rinviati

Non sono i prossimi tre step, anche se restano importanti:

- test di integrazione completi con DB/Redis reali
- audit business forense
- backup/restore verificato
- reverse proxy e zero-downtime completo
- staging pienamente separato

Questi step vanno dopo aver chiuso la prima disciplina di deploy, secret e osservabilita.

## Ordine raccomandato

1. implementare deploy Aruba manuale via GitHub Actions
2. chiudere la matrice secret e il setup dei secret runtime
3. integrare Sentry e monitor worker

## Regola di esecuzione

Non lavorare in parallelo su tutti e tre.

La sequenza corretta e:

1. chiudere Step 1 con workflow e test deploy
2. rifinire Step 2 sui secret effettivamente richiesti dal deploy
3. solo dopo introdurre Step 3
