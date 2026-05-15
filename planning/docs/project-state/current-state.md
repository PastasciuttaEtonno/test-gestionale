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
- `AuthService` collegato al DB reale
- `UserService` collegato al DB reale
- `AuditService` collegato al DB reale
- login persistito su DB con password hashate
- refresh token persistiti e ruotati
- audit esteso anche alle operazioni amministrative utenti
- ruolo reale `tenant_admin` introdotto nel dominio sicurezza
- introdotto schema `tenants` con collegamento `user.tenant_id`
- gestione utenti resa tenant-aware per il livello 2
- audit locale tenant esposto tramite endpoint dedicato
- configurazione aziendale tenant-aware esposta tramite API dedicate
- cifratura lato backend introdotta per i segreti SMTP del tenant
- protezione login persistita introdotta su `/auth/login`
- cooldown basilare e rate limiting attivi per coppia `identifier + ip_address`
- audit auth con `ip_address` e `user_agent` reali
- dipendenze frontend aggiornate a versioni recenti e prive di vulnerabilita note da `npm audit`
- immagini Docker principali aggiornate e pin esplicite

## Stato frontend attuale

- `Vue 3` con `script setup`
- `Vite` attivo come dev server
- `Tailwind CSS` attivo per styling rapido
- `Axios` attivo con interceptor centralizzato
- `Vue Router` attivo con guardie `auth`, `admin` e `tenant_admin`
- login con access token in memoria e refresh token in cookie `HttpOnly`
- dashboard protetta collegata a `GET /api/v1/auth/me`
- vista `admin-only` collegata a `GET /api/v1/admin/audit-log`
- home gestionale di base resa comune per tutti gli utenti autenticati
- navigazione admin nascosta ai non admin
- area `Super Admin` Esseduesoft trasformata in mockup statico enterprise
- area `Tenant Admin` cliente trasformata in mockup statico enterprise
- console `Super Admin` e `Tenant Admin` separate anche nella navigazione e nelle guardie router

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
