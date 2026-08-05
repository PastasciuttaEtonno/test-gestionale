# Security Audit — Gestionale (10/06/2026)

Audit generale su backend FastAPI, frontend Vue 3 e configurazioni di deploy. Basato su revisione diretta del codice (`backend/app`, `frontend/src`, docker-compose, Caddyfile, nginx) e sulla documentazione in `planning/` e `graphify-out/`.

## Giudizio complessivo

La postura di sicurezza è **sopra la media** per un progetto a questo stadio: auth ben progettata (rotazione refresh token con reuse detection e family timeout RFC 9700, cookie HttpOnly path-scoped, origin check enforced in produzione, Argon2, password ≥12 caratteri con breach check HIBP, lockout multi-scope), RBAC tenant-aware applicato in modo coerente, audit persistito, docs OpenAPI disabilitate in produzione, validatori di posture in `config.py`. Nessun uso di SQL raw pericoloso, nessun `v-html` nel frontend, access token solo in memoria.

I problemi trovati sono soprattutto di **gestione segreti e configurazione di deploy**, non di logica applicativa.

---

## Finding

### ALTO

**A1 — Segreti di produzione reali in `backend/.env` nella working tree**
Il file contiene `APP_ENV=production` con password PostgreSQL e Redis reali, `JWT_SECRET_KEY` e `FIELD_ENCRYPTION_KEY` di produzione. È correttamente in `.gitignore` (non committato), ma vive nella cartella di progetto: ogni backup, sync o condivisione della cartella espone le credenziali prod. Inoltre la `DATABASE_URL` usa l'utente **superuser `postgres`** (violazione least privilege).
*Rimedio:* ruotare tutte le credenziali, rimuovere il file dal progetto, gestire i segreti solo in Coolify; creare un utente DB applicativo con privilegi minimi.

**A2 — `FIELD_ENCRYPTION_KEY` con default Fernet hardcodato in `app/core/config.py`**
`field_encryption_key: str = Field(default="5hS0d52C...")` è una chiave reale e pubblica nel repo, usata da `FieldEncryptionService` (cifratura SMTP/settings tenant). A differenza del JWT secret, `validate_security_posture()` **non blocca** il default in staging/produzione: un deploy senza override cifrerebbe dati con una chiave nota a chiunque legga il repo.
*Rimedio:* aggiungere il check in `validate_security_posture`, rimuovere il default reale (usare un placeholder non valido), verificare che la prod usi una chiave dedicata (lo fa già) e pianificare la rotazione.

### MEDIO

**M1 — Access token in query string per SSE (`?token=`)**
`get_sse_user` accetta il token via URL e `frontend/src/stores/events.js` lo usa. L'URL completo finisce nei log access di Caddy/Traefik/nginx e di eventuali proxy intermedi. Mitigato dal TTL di 15 minuti, ma resta un token spendibile nei log.
*Rimedio:* ticket monouso a vita breve emesso da un endpoint autenticato, oppure cookie dedicato per lo stream; in alternativa, assicurarsi che i log dei proxy troncino la query string.

**M2 — Estrazione IP client da `X-Forwarded-For` fragile (rate limit e audit aggirabili)**
`build_security_request_context` prende il **primo** valore di XFF se il peer diretto è in `TRUSTED_PROXY_IPS`. Due problemi: (1) il primo hop di XFF è controllato dal client (Cloudflare appende, non sostituisce) → spoofing dell'IP nel lockout per-IP e nell'audit; (2) in produzione Coolify il peer diretto di uvicorn è Traefik sulla rete Docker interna, non un IP Cloudflare → la condizione non scatta mai e tutti i client risultano con lo stesso IP interno, degradando il lockout per-IP a lockout globale.
*Rimedio:* fidarsi solo del valore più a destra non-trusted della catena, o usare `CF-Connecting-IP`, e includere l'IP del reverse proxy interno tra i trusted.

**M3 — Security header assenti nel percorso di produzione effettivo**
HSTS, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` esistono **solo nel Caddyfile** (percorso Aruba). La produzione attuale (Coolify/Traefik + nginx del container frontend) non li imposta: `frontend/nginx.conf` non ha alcun header di sicurezza e il backend non ha middleware dedicato. Manca una **Content-Security-Policy** ovunque.
*Rimedio:* aggiungere gli header in `nginx.conf` (o via label Traefik) e definire una CSP almeno in modalità report-only.

**M4 — Rate limiting API applicato a un solo endpoint**
`rate_limit_dependency` è usato solo in `dashboard/routes.py`; `API_RATE_LIMIT_REQUESTS_PER_MINUTE` non protegge il resto delle API (il login ha la sua protezione dedicata, che è buona). Endpoint costosi (liste, SSE, report) restano senza limite.
*Rimedio:* applicare la dependency a livello di router o di endpoint sensibili.

### BASSO

**B1 — Artifact di test committati nel repo**: `auth-cookie.txt`, `login-headers.txt`, `logout-headers.txt`, `refresh-headers.txt`, `refresh-missing-headers.txt` sono tracciati in git. Oggi non contengono segreti, ma normalizzano il commit di output curl che potrebbero contenerne. Rimuoverli e aggiungere un pattern a `.gitignore`.

**B2 — docker-compose di sviluppo espone Postgres (`app/app`) e Redis senza password sulle porte host 5432/6379**. Accettabile in locale, ma da non riutilizzare su macchine raggiungibili in rete; valutare il bind su `127.0.0.1`.

**B3 — Messaggi `detail` delle eccezioni propagati nei 401** (`detail=str(exc)` in `get_current_user`): oggi i messaggi sono generici e sicuri, ma il pattern rischia di esporre dettagli interni se le eccezioni evolvono. Preferire messaggi statici.

---

## Punti di forza confermati

Rotazione refresh token con reuse detection e revoca di famiglia + absolute family timeout; cookie refresh HttpOnly, Secure, path-scoped su `/api/v1/auth`; origin/referer check obbligatorio in produzione (validato a startup); Argon2 via pwdlib; password policy 12+ caratteri con controllo breach (HIBP, k-anonymity presumibile); lockout login multi-scope (coppia identificativo+IP, identificativo, IP); RBAC granulare con verifica tenant della risorsa target (`RequirePermission`) e scoping coerente nei service (`current_user.tenant_id` passato ovunque nei moduli business); tenant admin non può assegnare ruolo admin né creare utenti fuori dal proprio tenant; UUID nativi (no ID enumerabili); PyJWT con issuer/algoritmo espliciti; docs/OpenAPI spente in produzione; CORS con origin esplicite; nessun `v-html`/localStorage per i token nel frontend; optimistic locking sui moduli business.

## Priorità suggerite

1. A1 — rotazione credenziali e rimozione `.env` dal progetto (subito)
2. A2 — validatore produzione per `FIELD_ENCRYPTION_KEY` (una riga, subito)
3. M3 — security header + CSP nel percorso Coolify
4. M2 — fix estrazione IP dietro Traefik/Cloudflare
5. M1, M4, B1–B3 a seguire

*Audit statico del codice: non sostituisce un penetration test sull'ambiente live.*
