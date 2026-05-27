# Aruba Deploy Setup

## Obiettivo

Preparare un deploy backend minimamente disciplinato su Aruba partendo dall'immagine pubblicata su `GHCR`, senza buildare il backend direttamente sul server.

## File coinvolti

- [.github/workflows/deploy-backend-aruba.yml](/c:/Users/ivan.lisciotto_webra/Desktop/project/.github/workflows/deploy-backend-aruba.yml)
- [docker-compose.aruba.yml](/c:/Users/ivan.lisciotto_webra/Desktop/project/docker-compose.aruba.yml)
- [planning/docs/backend/05-docker-and-runtime.md](/c:/Users/ivan.lisciotto_webra/Desktop/project/planning/docs/backend/05-docker-and-runtime.md)

## Modello operativo scelto

Questo deploy:

- usa immagine backend gia pubblicata su `GHCR`
- non ricompila il backend sulla VM Aruba
- carica sul server:
  - `docker-compose.aruba.yml`
  - `backend.env` generato da GitHub Secret
  - script remoto di deploy
- esegue migration e rollout via SSH

## Ambito del workflow

Il workflow prepara il deploy del solo backend:

- `db_migrator`
- `core_service`
- `celery_worker`

Non gestisce:

- frontend
- reverse proxy
- TLS
- provisioning della VM
- database e Redis come servizi Docker locali

Per questa pipeline il backend deve poter raggiungere `PostgreSQL` e `Redis` tramite le URL presenti nel file env di produzione.

## GitHub Secrets richiesti

Questa e la lista esatta dei secret richiesti dal workflow:

- `ARUBA_SSH_HOST`
- `ARUBA_SSH_PORT`
- `ARUBA_SSH_USER`
- `ARUBA_SSH_PRIVATE_KEY`
- `ARUBA_SSH_KNOWN_HOSTS`
- `ARUBA_BACKEND_ENV_FILE`
- `GHCR_PULL_USERNAME`
- `GHCR_PULL_TOKEN`

## Significato dei secret

### `ARUBA_SSH_HOST`

Host o IP pubblico della VM Aruba.

### `ARUBA_SSH_PORT`

Porta SSH della VM, di norma `22`.

### `ARUBA_SSH_USER`

Utente SSH autorizzato al deploy.

### `ARUBA_SSH_PRIVATE_KEY`

Chiave privata usata da GitHub Actions per collegarsi alla VM.

### `ARUBA_SSH_KNOWN_HOSTS`

Host key trusted della VM Aruba.

Formato consigliato:

- output di `ssh-keyscan -H <host>`

Questo evita di affidarsi a `ssh-keyscan` runtime dentro la pipeline.

### `ARUBA_BACKEND_ENV_FILE`

Contenuto completo del file `backend.env` che verra scritto sul server durante il deploy.

Deve contenere valori di produzione reali, ad esempio:

- `APP_ENV=production`
- `DATABASE_URL=...`
- `REDIS_URL=...`
- `CELERY_BROKER_URL=...`
- `CELERY_RESULT_BACKEND_URL=...`
- `JWT_SECRET_KEY=...`
- `FIELD_ENCRYPTION_KEY=...`
- `CORS_ALLOWED_ORIGINS=[...]`
- `AUTH_ALLOWED_ORIGINS=[...]`
- `REFRESH_COOKIE_SECURE=true`
- `AUTH_ENFORCE_ORIGIN_CHECK=true`

### `GHCR_PULL_USERNAME`

Username GitHub usato dal server per fare `docker login ghcr.io`.

### `GHCR_PULL_TOKEN`

`Personal Access Token (classic)` con almeno:

- `read:packages`

## GitHub Variables opzionali

Se non valorizzate, il workflow usa default sensati.

- `ARUBA_DEPLOY_PATH`
  - default: `/opt/Gestionale/backend`
- `ARUBA_BACKEND_PORT`
  - default: `8000`
- `ARUBA_COMPOSE_PROJECT_NAME`
  - default: `Gestionale-backend`

## Prerequisiti sulla VM Aruba

Prima di usare il workflow, la VM deve avere:

- Docker installato
- Docker Compose plugin disponibile
- `curl` disponibile
- l'utente SSH autorizzato a eseguire `docker`
- connettivita verso:
  - `ghcr.io`
  - PostgreSQL target
  - Redis target

## Come funziona il deploy

Il workflow:

1. calcola il nome immagine `ghcr.io/<owner>/<repo>-backend`
2. prepara SSH e asset temporanei
3. carica sul server:
   - `docker-compose.aruba.yml`
   - `backend.env` codificato
   - token GHCR temporaneo
   - script remoto
4. esegue `docker login ghcr.io`
5. fa pull di:
   - `db_migrator`
   - `core_service`
   - `celery_worker`
6. esegue migration Alembic, salvo input esplicito che le salta
7. aggiorna `core_service` e `celery_worker`
8. verifica `GET /health/ready`

## Strategia di rollout minima

La strategia corrente e volutamente semplice:

- deploy manuale via `workflow_dispatch`
- migration prima del restart del runtime
- restart controllato di:
  - `core_service`
  - `celery_worker`
- healthcheck finale backend

Questa non e ancora una strategia zero-downtime.

E una strategia minima ma ragionevole per un primo staging o una prima produzione piccola gestita da un solo sviluppatore.

## Rollback corto

Il rollback previsto e deliberatamente corto:

1. recuperare il tag precedente pubblicato su `GHCR`
   - tipicamente `sha-<commit>`
2. rilanciare manualmente `Deploy Backend Aruba`
3. impostare `image_tag` al tag precedente
4. rieseguire il deploy

Se il rollback non richiede schema precedente:

- si puo anche valutare `skip_migrations=true`

Se invece la release ha introdotto una migration non backward-compatible:

- il rollback non e piu corto
- serve procedura esplicita di downgrade o fix forward

Per questo motivo la disciplina migration deve restare additive-first.

## Reverse proxy — Caddy

Il reverse proxy scelto per Aruba e **Caddy v2**, non Nginx.

Motivazioni:

- TLS automatico con Let's Encrypt senza configurazione aggiuntiva
- `flush_interval -1` necessario per SSE (`GET /api/v1/events/stream`) — Caddy supporta questo nativamente
- setup piu semplice per un singolo sviluppatore rispetto a Nginx + Certbot

### Installazione su Debian/Ubuntu

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy
```

### Caddyfile

Il file `Caddyfile` e nel repository alla radice del progetto.

Posizionarlo sul server:

```bash
sudo cp Caddyfile /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

Sostituire `tuo-dominio.com` nel file con il dominio reale puntato alla VPS prima del deploy.

### Struttura Caddyfile

```
tuo-dominio.com {
    handle /api/* {
        reverse_proxy 127.0.0.1:8000 {
            flush_interval -1   # richiesto per SSE
        }
    }
    handle /health* {
        reverse_proxy 127.0.0.1:8000
    }
    handle {
        root * /var/www/gestionale
        try_files {path} /index.html
        file_server
    }
    header {
        Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        Referrer-Policy "strict-origin-when-cross-origin"
        -Server
    }
}
```

Il frontend compilato va in `/var/www/gestionale` (output di `npm run build`).

### Verifica TLS

```bash
curl -I https://tuo-dominio.com/health/live
```

Caddy ottiene il certificato Let's Encrypt al primo avvio se il dominio e raggiungibile dall'esterno sulla porta 80/443.

## Checklist sicurezza — fix implementati

Questi fix sono gia presenti nel codice. Verificare che siano attivi sul server:

### Docker

- [x] Porta backend bind su `127.0.0.1:8000` — non esposta a internet direttamente (`docker-compose.aruba.yml`)
- [x] Network bridge interna `backend` per comunicazione inter-container
- [x] `celery_worker` con `--concurrency=2` esplicito

### Backend FastAPI

- [x] OpenAPI (`/docs`, `/redoc`, `/openapi.json`) disabilitati in `staging` e `production`
- [x] CORS con `allow_origins` da `settings.cors_allowed_origins`, metodi e header espliciti
- [x] `/health/ready` non espone dettagli di eccezione — risponde `{"status": "error"}` senza stack trace

### GitHub Actions workflow

- [x] `chmod 600 backend.env` dopo il decode base64 sul server

### File env di produzione

Verificare che `ARUBA_BACKEND_ENV_FILE` contenga:

- `APP_ENV=production`
- `JWT_SECRET_KEY` reale (non placeholder)
- `REFRESH_COOKIE_SECURE=true`
- `AUTH_ENFORCE_ORIGIN_CHECK=true`
- `AUTH_ALLOWED_ORIGINS` esplicito
- `CORS_ALLOWED_ORIGINS` esplicito con il dominio reale
- `TRUSTED_PROXY_IPS` con l'IP di Caddy se Caddy gira sullo stesso host (normalmente `127.0.0.1`)

## Limiti consapevoli

Questa pipeline non copre ancora:

- deploy frontend (build e copia manuale in `/var/www/gestionale`)
- staging dedicato
- doppia istanza web
- rollback DB strutturato
- centralizzazione log
- Sentry

## Prossimo passo coerente

Dopo questa pipeline il passo giusto non e aggiungere altra automazione a caso.

Il passo giusto e:

1. chiudere la matrice secret
2. sostituire `tuo-dominio.com` nel `Caddyfile` con il dominio reale
3. fare un primo deploy controllato su Aruba
4. poi aggiungere osservabilita production-grade
