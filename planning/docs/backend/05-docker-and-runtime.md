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
- `db_service` PostgreSQL pronto
- healthcheck configurato
- migration Alembic eseguita in avvio container
- smoke test reale gia validato
- immagini base pin esplicite per ridurre drift del runtime

## Immagini correnti

- backend runtime: `python:3.12.13-slim-trixie`
- tool `uv` copiato da: `ghcr.io/astral-sh/uv:0.11.11`
- database: `postgres:17.9-alpine3.23`

## Step successivo

valutare se mantenere `Alembic` in auto-run all'avvio oppure separarlo in un job esplicito di deploy.
