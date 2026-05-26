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

## Limiti consapevoli

Questa pipeline non copre ancora:

- deploy frontend
- reverse proxy `Nginx` o `Traefik`
- TLS
- staging dedicato
- doppia istanza web
- rollback DB strutturato
- centralizzazione log
- Sentry

## Prossimo passo coerente

Dopo questa pipeline il passo giusto non e aggiungere altra automazione a caso.

Il passo giusto e:

1. chiudere la matrice secret
2. fare un primo deploy controllato su Aruba
3. poi aggiungere osservabilita production-grade
