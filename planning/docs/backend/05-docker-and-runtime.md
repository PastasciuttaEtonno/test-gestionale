# Docker and Runtime

## Obiettivo

Usare Docker non come formalita, ma come ambiente minimo ripetibile per:

- avvio backend
- avvio PostgreSQL
- smoke test API
- futura integrazione con migrazioni e worker

## File attivi

- [docker-compose.yml](/c:/Users/ivan.lisciotto_webra/Desktop/project/docker-compose.yml)
- [docker-compose.aruba.yml](/c:/Users/ivan.lisciotto_webra/Desktop/project/docker-compose.aruba.yml)
- [backend/Dockerfile](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/Dockerfile)
- [backend/.env.example](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/.env.example)

## Stato corrente

- `core_service` containerizzato
- `db_migrator` separato come job esplicito di migration
- `celery_worker` containerizzato
- `db_service` PostgreSQL pronto
- `redis_service` pronto come broker e result backend
- `redis_service` usato anche da FastAPI per cache e rate limiting
- healthcheck configurato
- healthcheck `core_service` basato su `/health/ready`
- migration Alembic eseguita da servizio dedicato prima di web e worker
- smoke test reale gia validato
- immagini base pin esplicite per ridurre drift del runtime

## Immagini correnti

- backend runtime: `python:3.12.13-slim-trixie`
- tool `uv` copiato da: `ghcr.io/astral-sh/uv:0.11.14`
- database: `postgres:17.10-alpine3.23`
- redis: `redis:8.2.6-alpine3.22`

## Verifica aggiornamento immagini

Le immagini principali usate in runtime, build e pipeline sono state ricontrollate rispetto ai tag ufficiali correnti.

Esito sintetico:

- `python:3.12.13-slim-trixie`
  - gia allineata alla patch corrente della linea `3.12`
- `ghcr.io/astral-sh/uv`
  - aggiornata da `0.11.11` a `0.11.14`
- `postgres`
  - aggiornato da `17.9-alpine3.23` a `17.10-alpine3.23`
- `redis`
  - aggiornato da `8.2.1-alpine3.22` a `8.2.6-alpine3.22`
- `node`
  - aggiornato in `frontend/Dockerfile` da `24.14.1-alpine3.23` a `24.15.0-alpine3.23`

Per le GitHub Actions runner e stato anche eliminato il riferimento flottante `ubuntu-latest` in favore di `ubuntu-24.04`, cosi da ridurre drift e sorprese tra run successive.

## Disciplina corrente

Nel runtime locale containerizzato:

- `db_migrator` esegue le migration e termina
- `core_service` non parte se le migration falliscono
- `celery_worker` non parte se le migration falliscono
- il web container non modifica lo schema da solo

## Publication corrente

La pubblicazione immagini oggi copre il backend:

- registry scelto: `GHCR`
- naming immagine: `ghcr.io/<owner-lowercase>/<repo-lowercase>-backend`
- tag pubblicati:
  - `sha-<commit>`
  - `main`
  - `latest`

La pipeline di publication:

- non esegue il deploy su Aruba
- parte solo dopo il successo del workflow `Checks` su `main`
- costruisce l'immagine partendo dal `backend/Dockerfile`

## Setup Registry e Aruba

### Publication da GitHub Actions

Il workflow `.github/workflows/publish-backend-image.yml` usa gia il token effimero del job:

- login registry con `github.actor`
- password `secrets.GITHUB_TOKEN`
- permessi richiesti al job:
  - `contents: read`
  - `packages: write`

Prerequisito repository:

- `Settings > Actions > General > Workflow permissions`
- valore richiesto: `Read and write permissions`

Questo e sufficiente per pubblicare su `GHCR` senza PAT aggiuntivi.

### Pull futuro da Aruba

Sul server Aruba la situazione e diversa: il server non gira dentro GitHub Actions e quindi non puo usare `GITHUB_TOKEN`.

Per il pull privato da `GHCR` servira:

- un utente GitHub o service account leggibile dal server
- un `Personal Access Token (classic)` con almeno:
  - `read:packages`

Comando tipico lato server:

```bash
docker login ghcr.io -u <github-username> -p <pat-read-packages>
```

Poi:

```bash
docker pull ghcr.io/<owner>/<repo>-backend:sha-<commit>
```

### Gestione corretta dei secret

Non mettere il PAT Aruba:

- nel repository
- in `.env.example`
- hardcodato in script shell versionati

Strategia consigliata:

- secret memorizzato nella piattaforma CI per il deploy
- oppure secret installato direttamente sulla VM Aruba
- rotazione periodica del PAT

### Nota operativa

Se il package GHCR resta privato, il deploy Aruba fallira finche il server non ha eseguito con successo `docker login ghcr.io`.

## Step successivo

Portare la stessa disciplina nel deploy reale Aruba con job GitHub Actions separato per:

- migration
- rollout web
- rollout worker

Questo step e ora preparato tramite:

- [planning/docs/backend/12-aruba-deploy-setup.md](/c:/Users/ivan.lisciotto_webra/Desktop/project/planning/docs/backend/12-aruba-deploy-setup.md)
