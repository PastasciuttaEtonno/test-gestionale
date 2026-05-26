# Gestionale Gestionale

Stack: FastAPI · PostgreSQL · Redis · Celery · Vue 3 · Vite · Tailwind CSS v4 · PrimeVue v4

---

## Avvio locale (sviluppo)

Copia i file di configurazione di esempio prima del primo avvio:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### Avviare tutti i servizi

```bash
docker compose up --build
```

| Servizio | URL |
|---|---|
| Frontend (Vue) | http://localhost:5173 |
| Backend (FastAPI) | http://localhost:8000 |
| Docs API (Swagger) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

> Le migrazioni Alembic vengono eseguite automaticamente da `db_migrator` prima che il backend parta.

### Avviare solo il backend (senza frontend)

```bash
docker compose up --build core_service celery_worker db_service redis_service
```

### Ricostruire le immagini senza usare la cache

```bash
docker compose build --no-cache
docker compose up
```

### Fermare e rimuovere i container

```bash
docker compose down
```

### Fermare, rimuovere i container e cancellare i volumi (reset DB)

```bash
docker compose down -v
```

### Vedere i log in tempo reale

```bash
# tutti i servizi
docker compose logs -f

# solo backend
docker compose logs -f core_service

# solo worker Celery
docker compose logs -f celery_worker
```

### Eseguire un comando nel container backend

```bash
docker compose exec core_service /app/.venv/bin/python -c "print('ok')"
```

---

## Deploy produzione (Aruba)

Il file `docker-compose.aruba.yml` usa immagini pre-built da GHCR e richiede un file `backend.env` nella stessa cartella sul server.

```bash
# prima esecuzione — scarica le immagini e avvia
BACKEND_IMAGE_REPOSITORY=ghcr.io/<owner>/<repo>-backend \
BACKEND_IMAGE_TAG=latest \
docker compose -f docker-compose.aruba.yml up -d

# aggiornare a una nuova immagine
BACKEND_IMAGE_TAG=sha-<commit> \
docker compose -f docker-compose.aruba.yml pull && \
docker compose -f docker-compose.aruba.yml up -d

# fermare
docker compose -f docker-compose.aruba.yml down
```

---

## Documentazione interna

- [Stato corrente](planning/docs/project-state/current-state.md)
- [Frontend overview](planning/docs/frontend/00-frontend-overview.md)
- [Guida utilizzo frontend](planning/docs/frontend/02-frontend-usage-and-maintenance-guide.md)
