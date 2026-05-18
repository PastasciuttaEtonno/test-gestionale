# Stato Corrente

## Obiettivo della fase

Preparare il nucleo tecnico del nuovo gestionale web Esseduesoft partendo dal modulo trasversale `Auth & Identity`.

## Stato raggiunto

- definito `Master Plan` architetturale
- definita specifica tecnica del modulo `Auth`
- definito skeleton architetturale del backend FastAPI
- creato backend minimale eseguibile
- introdotta containerizzazione con Docker
- introdotte dipendenze gestite con `uv`
- introdotto `Alembic` con migration iniziale
- creato schema PostgreSQL `security`
- implementato login reale su PostgreSQL con JWT e refresh token persistiti
- verificato smoke test reale del backend containerizzato
- creato frontend minimale `Vue 3` per test del flusso JWT
- introdotti check di qualita leggeri per backend e frontend
- introdotta pipeline CI minima per lint e build
- definita e applicata una prima linea stilistica del gestionale su palette grigio e rosso
- estratti componenti UI condivisi per evitare duplicazione nelle viste frontend

## Stato backend attuale

- `FastAPI` configurato
- `Pydantic` usato per schemi request/response
- `SQLAlchemy` attivo come ORM layer
- `PostgreSQL` attivo via `docker-compose`
- `Alembic` attivo per lo schema `security`
- `Celery + Redis` introdotti per task asincroni backend
- Redis asincrono introdotto anche come cache applicativa e motore di rate limiting
- `AuthService` collegato al DB reale
- `UserService` collegato al DB reale
- `AuditService` collegato al DB reale
- login persistito su DB con password hashate
- refresh token persistiti e ruotati
- audit esteso anche alle operazioni amministrative utenti
- ruolo reale `tenant_admin` introdotto nel dominio sicurezza
- RBAC dichiarativo tenant-aware disponibile con ruoli `admin`, `tenant_admin`, `manager`, `worker`, `user`
- endpoint demo protetti: `GET /api/v1/bom/{bom_id}` e `POST /api/v1/finance/costs`
- introdotto schema `tenants` con collegamento `user.tenant_id`
- gestione utenti resa tenant-aware per il livello 2
- audit locale tenant esposto tramite endpoint dedicato
- configurazione aziendale tenant-aware esposta tramite API dedicate
- cifratura lato backend introdotta per i segreti SMTP del tenant
- protezione login persistita introdotta su `/auth/login`
- cooldown e rate limiting auth attivi su tre scope: `identifier + ip_address`, solo `identifier`, solo `ip_address`
- audit auth con `ip_address` e `user_agent` reali
- hardening produzione introdotto su auth: fail-fast configurazione sensibile, trusted proxy espliciti e controllo `Origin` / `Referer` sugli endpoint cookie-based
- endpoint dashboard KPI tenant-aware protetto con cache Redis e rate limiting
- endpoint demo di mutazione produzione con invalidazione mirata della cache tenant
- update reali tenant admin allineati con invalidazione cache KPI del tenant in best-effort
- osservabilita minima backend introdotta con `request_id`, logging strutturato e health endpoint `live/ready`
- baseline test backend introdotta su `health`, `auth` e RBAC tenant-aware, eseguita anche in CI
- migration discipline iniziale introdotta: `db_migrator` separato da web e worker nel runtime Docker
- publication discipline iniziale introdotta: workflow GitHub Actions per publish backend image su `GHCR`
- setup operativo GHCR chiarito: publish via `GITHUB_TOKEN`, futuro pull Aruba via PAT `read:packages`
- dipendenze frontend aggiornate a versioni recenti e prive di vulnerabilita note da `npm audit`
- immagini Docker principali aggiornate e pin esplicite

## Stato frontend attuale

- `Vue 3` con `script setup`
- `Vite` attivo come dev server
- `Tailwind CSS` attivo per styling rapido
- `Pinia` attiva per lo stato auth condiviso
- `Axios` attivo con interceptor centralizzato
- store auth esteso con helper ruolo/permessi
- `Vue Router` attivo con guardie dichiarative per auth, ruoli e permessi
- login con access token in memoria e refresh token in cookie `HttpOnly`
- direttiva `v-can` disponibile per la visibilita degli elementi UI
- dashboard protetta collegata a `GET /api/v1/auth/me`
- vista `admin-only` collegata a `GET /api/v1/admin/audit-log`
- home gestionale di base resa comune per tutti gli utenti autenticati
- navigazione admin nascosta ai non admin
- area `Super Admin` Esseduesoft trasformata in mockup statico enterprise
- area `Tenant Admin` cliente trasformata in mockup statico enterprise
- console `Super Admin` e `Tenant Admin` separate anche nella navigazione e nelle guardie router
- demo frontend di task report asincrono con polling integrata nella dashboard

## Decisioni attive

- approccio `modular monolith`
- `Auth & Identity` come primo asse trasversale
- documentazione operativa obbligatoria durante ogni evoluzione
- standard OpenAPI elevato per ogni endpoint backend
- convenzione descrittiva del codice in italiano
- frontend minimale come client di test prima dei moduli business
- pin delle immagini e lockfile come regola di stabilita del runtime
- quality gate leggeri preferiti a policy troppo rigide in questa fase

## Documento di handoff

Per ripartire con un altro LLM o con un altro sviluppatore, il punto di ingresso rapido e:

- [00-llm-handoff.md](/c:/Users/ivan.lisciotto_webra/Desktop/project/planning/docs/00-llm-handoff.md)
- [production-readiness-gap-analysis.md](/c:/Users/ivan.lisciotto_webra/Desktop/project/planning/docs/architecture/production-readiness-gap-analysis.md)
