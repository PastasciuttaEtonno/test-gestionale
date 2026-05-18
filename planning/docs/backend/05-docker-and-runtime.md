# Docker and Runtime

## Obiettivo

Usare Docker non come formalita, ma come ambiente minimo ripetibile per:

- avvio backend
- avvio PostgreSQL
- smoke test API
- futura integrazione con migrazioni e worker

## File attivi

- [docker-compose.yml](/c:/Users/ivan.lisciotto_webra/Desktop/project/docker-compose.yml)
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
- tool `uv` copiato da: `ghcr.io/astral-sh/uv:0.11.11`
- database: `postgres:17.9-alpine3.23`
- redis: `redis:8.2.1-alpine3.22`

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

## Step successivo

Portare la stessa disciplina nel deploy reale Aruba con job GitHub Actions separato per:

- migration
- rollout web
- rollout worker
