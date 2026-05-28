# Coolify Deploy Setup

## Obiettivo

Documentare il deploy completo su VPS Aruba con Coolify: backend FastAPI, frontend Vue, PostgreSQL, Redis, proxy Cloudflare.

## Architettura risultante

```
Browser
  │
  ▼
Cloudflare (WAF + proxy TLS)
  │
  ▼
Aruba VPS — Coolify Caddy (80/443)
  ├── tuo-dominio.com/api/*  ──▶  core_service :8000  (Application, build da Dockerfile)
  └── tuo-dominio.com/*      ──▶  Static Site Vue     (Coolify build da Nixpacks)

Rete interna Docker (Coolify):
  core_service   ──▶  PostgreSQL resource
  celery_worker  ──▶  Redis resource (broker + result backend)
  core_service   ──▶  Redis resource (cache + pubsub)
```

> **Nessun registry esterno**: Coolify builda il backend direttamente dal `Dockerfile` nella repo GitHub — non serve GHCR o Docker Hub.

## Prerequisiti

- VPS Aruba con Coolify già installato e raggiungibile
- Dominio con DNS gestito da Cloudflare
- Repo GitHub con il codice (backend in `backend/`, frontend in `frontend/`)
- Docker e Docker Compose disponibili sulla VPS (Coolify li gestisce)

---

## Step 1 — Risorse database in Coolify

### PostgreSQL

1. Coolify → **New Resource → Database → PostgreSQL**
2. Versione: `16`
3. Nome: `gestionale-db`
4. Al termine: vai su **Connection** → copia **Internal Connection String**

Formato interno:
```
postgresql://postgres:PASSWORD@NOME-SERVIZIO:5432/postgres
```

### Redis

1. Coolify → **New Resource → Database → Redis**
2. Versione: `7`
3. Nome: `gestionale-redis`
4. Al termine: vai su **Connection** → copia **Internal Connection String**

Formato interno:
```
redis://default:PASSWORD@NOME-SERVIZIO:6379
```

Usa questi hostname nei `REDIS_URL`, `CELERY_BROKER_URL` ecc. — i container si vedono per nome servizio sulla rete interna Coolify.

---

## Step 2 — Backend (Application resource × 2)

Crea due Application resource separate: `core_service` e `celery_worker`. Entrambe buildano dallo stesso Dockerfile.

### core_service

1. Coolify → **New Resource → Application**
2. Source: **GitHub** → seleziona la repo, branch `main`
3. Base directory: `backend`
4. Build pack: **Dockerfile**
5. Domain: `tuo-dominio.com` — Port: `8000` — Path: `/api`
6. Pre-deploy command: `/app/.venv/bin/alembic upgrade head`

Il pre-deploy command esegue le migration Alembic automaticamente prima di ogni deploy.

### celery_worker

1. Coolify → **New Resource → Application**
2. Source: stessa repo, branch `main`
3. Base directory: `backend`
4. Build pack: **Dockerfile** (stesso Dockerfile di core_service)
5. Start command override:
   ```
   /app/.venv/bin/celery -A app.core.celery_app:celery_app worker --loglevel=info --concurrency=2
   ```
6. Nessun dominio — non esposto

### Environment variables (identiche per entrambi i servizi)

Vai su **Environment Variables** di ciascuna Application e inserisci:

```
APP_ENV=production
APP_NAME=Gestionale Core Service
APP_VERSION=0.1.0
LOG_LEVEL=INFO
LOG_JSON=true
REQUEST_ID_HEADER_NAME=X-Request-ID
API_V1_PREFIX=/api/v1

DATABASE_URL=postgresql+psycopg://postgres:PASSWORD@NOME-SERVIZIO:5432/postgres

REDIS_URL=redis://default:PASSWORD@NOME-SERVIZIO:6379/0
REDIS_PUBSUB_URL=redis://default:PASSWORD@NOME-SERVIZIO:6379/1
CELERY_BROKER_URL=redis://default:PASSWORD@NOME-SERVIZIO:6379/2
CELERY_RESULT_BACKEND_URL=redis://default:PASSWORD@NOME-SERVIZIO:6379/3

JWT_SECRET_KEY=<genera con: openssl rand -hex 64>
JWT_ALGORITHM=HS256
JWT_ISSUER=Gestionale-core-service
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

FIELD_ENCRYPTION_KEY=<genera con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">

CORS_ALLOWED_ORIGINS=["https://tuo-dominio.com"]
AUTH_ALLOWED_ORIGINS=["https://tuo-dominio.com"]
AUTH_ENFORCE_ORIGIN_CHECK=true

REFRESH_COOKIE_NAME=Gestionale_refresh_token
REFRESH_COOKIE_SECURE=true
REFRESH_COOKIE_SAMESITE=lax
REFRESH_COOKIE_PATH=/api/v1/auth

TRUSTED_PROXY_IPS=["173.245.48.0/20","103.21.244.0/22","103.22.200.0/22","103.31.4.0/22","141.101.64.0/18","108.162.192.0/18","190.93.240.0/20","188.114.96.0/20","197.234.240.0/22","198.41.128.0/17","162.158.0.0/15","104.16.0.0/13","104.24.0.0/14","172.64.0.0/13","131.0.72.0/22"]

LOGIN_RATE_LIMIT_MAX_ATTEMPTS=5
LOGIN_RATE_LIMIT_WINDOW_MINUTES=15
LOGIN_RATE_LIMIT_LOCKOUT_MINUTES=15
LOGIN_RATE_LIMIT_IDENTIFIER_MAX_ATTEMPTS=10
LOGIN_RATE_LIMIT_IP_MAX_ATTEMPTS=30
API_RATE_LIMIT_REQUESTS_PER_MINUTE=100

CELERY_TASK_DEFAULT_QUEUE=default
CELERY_TASK_TRACK_STARTED=true

DASHBOARD_KPI_CACHE_TTL_SECONDS=300
```

> **Attenzione**: sostituisci `PASSWORD` e `NOME-SERVIZIO` con i valori reali copiati dalla Connection String di PostgreSQL e Redis in Coolify.

### Deploy webhook

1. Nel pannello di `core_service` → **Deploy Webhook**
2. Copia l'URL
3. Mettilo come secret GitHub: `COOLIFY_DEPLOY_WEBHOOK`

> Il webhook triggera il deploy di `core_service` (che include le migration nel pre-deploy command). `celery_worker` si può configurare con auto-deploy su push GitHub direttamente dal pannello Coolify.

---

## Step 3 — Frontend (Static Site resource)

### Creazione

1. Coolify → **New Resource → Static Site**
2. Source: **GitHub** → stessa repo
3. Branch: `main`

### Configurazione

| Campo | Valore |
|---|---|
| Base directory | `frontend` |
| Build command | `npm run build` |
| Publish directory | `dist` |
| Build pack | **Nixpacks** |
| Domain | `tuo-dominio.com` |
| SPA mode / Fallback to index.html | **Abilitato** |

Il SPA mode è obbligatorio: senza di esso navigare direttamente su `/anagrafiche/123` restituisce 404.

### Environment variables build time

```
NODE_ENV=production
```

`VITE_API_BASE_URL` **non serve**: il client HTTP usa il default `/api/v1` (path relativo) che funziona sullo stesso dominio.

> Le variabili `VITE_*` vengono embeddate da Vite a build time. Cambiarle in Coolify richiede un rebuild, non solo un restart.

### Routing `/api`: e' compito di Traefik, NON di nginx

In produzione e' il reverse proxy (Traefik su Coolify) a instradare `tuo-dominio.com/api/*` verso `core_service` — vedi l'architettura in cima a questo documento. Il frontend serve **solo** la SPA.

Per questo `frontend/nginx.conf` (usato dall'immagine Docker) deve restare **pristino**, senza blocchi `location /api { proxy_pass http://core_service:8000; }`:

- con un hostname **letterale**, nginx risolve l'upstream all'avvio e va in `[emerg] host not found in upstream` se `core_service` non risolve nella rete di produzione → container in crash loop, sito down
- il proxy `/api` serve **solo in locale** (docker-compose, dove non c'e' Traefik): e' fornito da `frontend/nginx.local.conf`, montato come volume unicamente dal `docker-compose.yml`. Coolify ignora il `docker-compose.yml`, quindi non vede mai quel config.

> ATTENZIONE: non spostare i blocchi `/api` dentro `frontend/nginx.conf`. Romperebbe il deploy.

### Due ambienti, due reverse proxy

Il routing `/api` ha **due modalita' complementari**, una per ambiente:

| Ambiente | Reverse proxy `/api` | Frontend |
|---|---|---|
| **Locale** (docker-compose) | nginx del container client, via `frontend/nginx.local.conf` montato come volume | SPA servita da nginx |
| **Produzione** (Coolify) | Traefik, gestito da Coolify (routing path `/api` → core_service) | SPA servita da Coolify |

Sono due strade per testare/servire la stessa app: in locale non c'e' Traefik, quindi nginx fa da proxy; in produzione ci pensa Traefik e `frontend/nginx.conf` resta pristino (solo SPA). Per questo i blocchi `/api` vivono **solo** in `nginx.local.conf`.

---

## Step 4 — GitHub Actions

### Secret da aggiungere

| Secret | Valore |
|---|---|
| `COOLIFY_DEPLOY_WEBHOOK` | URL webhook copiato dallo Step 2 |

### Secret da rimuovere (non più necessari)

- `ARUBA_SSH_HOST`
- `ARUBA_SSH_PORT`
- `ARUBA_SSH_USER`
- `ARUBA_SSH_PRIVATE_KEY`
- `ARUBA_SSH_KNOWN_HOSTS`
- `ARUBA_BACKEND_ENV_FILE`
- `GHCR_PULL_USERNAME`
- `GHCR_PULL_TOKEN`

### Flusso deploy backend

Il workflow `.github/workflows/deploy-backend-aruba.yml`:

1. Si attiva su push a `main` che tocca `backend/**` (o manualmente)
2. Esegue check di qualità: lint, format, importability, tests
3. Se i check passano: chiama il webhook Coolify
4. Coolify fa il pull del codice da GitHub, builda il Dockerfile sulla VPS e rideploya

Nessun build di immagine in CI, nessun registry esterno — il build avviene direttamente su Coolify.

---

## Step 5 — Cloudflare

### SSL mode

Cloudflare → **SSL/TLS → Full (strict)**

Coolify gestisce il proprio certificato TLS. Senza `Full strict` il traffico Cloudflare→VPS viaggia in HTTP.

### Firewall VPS — blocca accesso diretto

Solo gli IP Cloudflare possono raggiungere le porte 80/443, altrimenti chiunque conosca l'IP della VPS bypassa Cloudflare.

```bash
sudo ufw delete allow 80/tcp
sudo ufw delete allow 443/tcp

for ip in \
  173.245.48.0/20 103.21.244.0/22 103.22.200.0/22 103.31.4.0/22 \
  141.101.64.0/18 108.162.192.0/18 190.93.240.0/20 188.114.96.0/20 \
  197.234.240.0/22 198.41.128.0/17 162.158.0.0/15 104.16.0.0/13 \
  104.24.0.0/14 172.64.0.0/13 131.0.72.0/22; do
  sudo ufw allow from $ip to any port 80,443 proto tcp
done

sudo ufw reload
```

### WAF Custom Rules (free tier — 5 regole)

Cloudflare → **Security → WAF → Custom Rules**

**Regola 1 — Blocca accesso admin da IP sconosciuti**
```
(http.request.uri.path contains "/api/v1/admin" and not ip.src in {TUO_IP/32})
→ Block
```

**Regola 2 — Blocca login da client ad alto threat score**
```
(http.request.uri.path eq "/api/v1/auth/login" and cf.threat_score gt 10)
→ Block
```

**Regola 3 — Blocca bot su endpoint API**
```
(http.request.uri.path contains "/api" and cf.client.bot)
→ Block
```

### Impostazioni aggiuntive (tutte gratis)

| Impostazione | Valore | Dove |
|---|---|---|
| Bot Fight Mode | On | Security → Bots |
| Security Level | Medium | Security → Settings |
| Browser Integrity Check | On | Security → Settings |
| Always Use HTTPS | On | SSL/TLS → Edge Certs |
| HSTS | Enable (max-age 31536000) | SSL/TLS → Edge Certs |

---

## Generare i secret

Dalla repo locale (richiede Git Bash o terminale Unix):

```bash
# JWT_SECRET_KEY
openssl rand -hex 64

# FIELD_ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

> **Importante**: salva questi valori in un password manager prima di inserirli in Coolify. Se perdi `FIELD_ENCRYPTION_KEY` dopo il primo deploy, i campi cifrati nel database (es. password SMTP) diventano illeggibili e non recuperabili.

---

## Checklist deploy — prima volta

- [ ] PostgreSQL resource creato in Coolify, Internal URL copiata
- [ ] Redis resource creato in Coolify, Internal URL copiata
- [ ] `JWT_SECRET_KEY` generata e salvata nel password manager
- [ ] `FIELD_ENCRYPTION_KEY` generata e salvata nel password manager
- [ ] Application `core_service` creata, env vars inserite, dominio `/api` configurato, pre-deploy command impostato
- [ ] Application `celery_worker` creata, env vars inserite, start command override impostato
- [ ] Deploy webhook di `core_service` copiato e aggiunto come `COOLIFY_DEPLOY_WEBHOOK` in GitHub Secrets
- [ ] Static Site creato, SPA mode abilitato, dominio root configurato
- [ ] Cloudflare SSL mode impostato su `Full (strict)`
- [ ] Firewall VPS aggiornato — solo IP Cloudflare su 80/443
- [ ] WAF rules create in Cloudflare
- [ ] `TUO_IP` sostituito con il tuo IP reale nella WAF Rule 1
- [ ] `tuo-dominio.com` sostituito con il dominio reale in tutto il file env

## Rollback

1. Identifica il tag SHA dell'immagine precedente su GHCR (es. `sha-abc1234`)
2. In Coolify → Docker Compose resource → **Environment Variables** → aggiorna `BACKEND_IMAGE_TAG`
3. Redeploy manuale dal pannello

Se la release ha introdotto una migration non backward-compatible il rollback richiede un downgrade manuale del DB — preferire sempre migration additive.
