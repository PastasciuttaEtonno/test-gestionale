# Gestionale 

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

## Deploy su Coolify

Il percorso di produzione attuale. `docker-compose.coolify.yml` descrive l'intero stack — SPA, API, worker Celery, PostgreSQL, Redis — e Coolify builda direttamente dal repo: non serve un registry esterno.

### Architettura

| Dominio | Servizio | Porta |
|---|---|---|
| `gestionale.vasquezlisciotto.xyz` | `client` (SPA Vue su nginx) | 80 |
| `api-gestionale.vasquezlisciotto.xyz` | `core_service` (FastAPI) | 8000 |

Traefik instrada per host. `db_service` e `redis_service` non pubblicano porte: restano raggiungibili solo sulla rete interna del progetto.

> Il trattino in `api-gestionale` non è estetico: Cloudflare Universal SSL copre solo i sottodomini di primo livello, quindi `api.gestionale.*` resterebbe senza certificato.

Poiché i due host condividono il dominio registrabile, per il browser sono same-site: il cookie di refresh viaggia da `gestionale.*` verso `api-gestionale.*` con `SameSite=lax`, senza bisogno di `none`.

### Variabili richieste

Da impostare nel pannello Coolify. Senza `POSTGRES_PASSWORD` il container PostgreSQL non parte e `core_service` resta unhealthy a catena.

| Variabile | Come generarla |
|---|---|
| `POSTGRES_USER` / `POSTGRES_DB` | a scelta (es. `app` / `gestionale`) |
| `POSTGRES_PASSWORD` | `openssl rand -hex 32` |
| `JWT_SECRET_KEY` | `openssl rand -hex 64` |
| `FIELD_ENCRYPTION_KEY` | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `DEMO_READONLY` | opzionale, default `true` |

Le variabili non elencate usano i default di `app/core/config.py`, che puntano già agli hostname interni corretti.

### Procedura

1. Record A per **entrambi** i sottodomini verso l'IP della VPS
2. Cloudflare in **DNS only** (nuvola grigia) per il primo deploy
3. Coolify → **New Resource → Docker Compose**, repo GitHub, branch `main`, compose file `docker-compose.coolify.yml`
4. Imposta le variabili e assegna i due domini ai servizi `client` e `core_service`
5. Deploy, poi verifica che entrambi i certificati siano stati emessi
6. Riattiva il proxy Cloudflare, imposta **SSL/TLS → Full (strict)**, infine limita 80/443 agli IP Cloudflare

> Il passo 2 non è un dettaglio: Traefik ottiene il certificato con challenge HTTP-01, che richiede la porta 80 raggiungibile **da Let's Encrypt**. Con il proxy Cloudflare già attivo e il firewall chiuso sugli IP Cloudflare l'emissione fallisce, e `Full (strict)` risponde 526.

Migrazioni e primo utente sono automatici: `backend/start.sh` esegue `alembic upgrade head` a ogni avvio, e le migrazioni seminano l'utente amministratore. **Cambia la password al primo accesso**: è in chiaro in `backend/alembic/versions/20260515_0001_create_security_schema.py` e il repository è pubblico.

> [`planning/docs/backend/13-coolify-deploy-setup.md`](planning/docs/backend/13-coolify-deploy-setup.md) documenta un assetto alternativo, con risorse Coolify separate per database, backend e frontend, più le regole WAF di Cloudflare.

---

## Deploy produzione (Aruba, altri providers)

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

## Hosting attuale e futuro

Il progetto è pensato per partire in modalità demo locale e crescere verso ambienti di produzione più robusti.

- Locale/demo: `docker compose up --build` con i file di esempio `.env` e `backend/.env` fornisce un ambiente di test rapido e riproducibile.
- Aruba o altri provider: usa container prebuilt e un file `backend.env` separato per tenere i segreti fuori dal repository.
- Evoluzioni future: la stessa architettura containerizzata può essere spostata su servizi cloud gestiti, come container registry, managed Kubernetes, servizi di database e cache gestite.
- Hosting non limitato a VPS private: l’obiettivo è supportare anche deployment su cloud provider con servizi gestiti, evitando di dipendere esclusivamente da VPS tradizionali.
- Coolify: `docker-compose.coolify.yml` builda tutto lo stack dal repo, con i segreti gestiti dal pannello e i database sulla rete interna.
- Workflow CI/CD: il repository include GitHub Actions in `.github/workflows/` per build, test e deploy.

---

## Documentazione interna

- [Stato corrente](planning/docs/project-state/current-state.md)
- [Frontend overview](planning/docs/frontend/00-frontend-overview.md)
- [Guida utilizzo frontend](planning/docs/frontend/02-frontend-usage-and-maintenance-guide.md)
