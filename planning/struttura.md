# Progetto di Migrazione: Da Legacy Monolith a Modular Web Architecture

**Target Stack:** Python (`FastAPI + Pydantic + SQLAlchemy`) | Vue.js 3 | Docker | PostgreSQL

## 1. Visione dell'Architettura

L'obiettivo e trasformare il gestionale desktop legacy (VB6/VB.NET) in una Web App moderna.  
Il target finale puo evolvere verso microservizi, ma la scelta architetturale corrente e un **Modular Monolith containerizzato**.

Questa decisione e coerente con:

- team ridotto
- esigenza di mantenere complessita operativa bassa
- necessita di introdurre domini separati senza frammentare subito il runtime

Domini attesi:

- `Auth & Identity`
- `Anagrafiche`
- `Documentale`
- `Fiscale`
- `Amministrazione tenant`

## 2. Stack Tecnologico

| Layer | Tecnologia | Motivazione |
| --- | --- | --- |
| **Frontend** | **Vue.js 3 (Vite)** | Buona ergonomia per UI gestionali dense, form complessi e navigazione enterprise. |
| **Backend** | **Python (FastAPI + Pydantic + SQLAlchemy)** | FastAPI per routing/OpenAPI, Pydantic per contratti API, SQLAlchemy per ORM e persistenza strutturata. |
| **Database** | **PostgreSQL** | ACID, JSONB, viste/materialized views, solidita per dominio gestionale. |
| **Container** | **Docker & Compose** | Ambiente ripetibile tra sviluppo, test e bootstrap locale. |
| **Cache/Broker** | **Redis** | Previsto per code e processi asincroni futuri; non ancora implementato. |

## 3. Infrastruttura Corrente

Servizi attualmente previsti nello stack:

1. `client`: frontend Vue.js
2. `core_service`: backend FastAPI
3. `db_service`: PostgreSQL

Servizi previsti ma non ancora implementati realmente:

1. `api_gateway`
2. `worker_service`
3. `redis`

## 4. Backend

Il backend segue una struttura a layer:

- `app/api/`
- `app/core/`
- `app/domain/`
- `app/models/`
- `app/repositories/`
- `app/schemas/`
- `app/services/`

Principi attivi:

- logica HTTP nei router
- logica applicativa nei service
- accesso dati nei repository
- modelli ORM separati dagli schemi Pydantic
- documentazione OpenAPI trattata come contratto

## 5. Primo Asse Trasversale: Auth & Identity

Il primo modulo implementato e `Auth & Identity`, interno al `core_service`.

Responsabilita attuali:

- login
- refresh token
- logout
- profilo utente corrente
- ruoli applicativi
- audit sicurezza
- utenti applicativi
- tenant scoping di livello base

Ruoli attualmente reali:

- `admin`: super admin Gestionale
- `tenant_admin`: amministratore dell'azienda cliente
- `user`: utente operativo standard

Note attuali:

- `admin` ha visione globale
- `tenant_admin` opera solo sul proprio tenant
- `user` ha accesso operativo non amministrativo

Documenti di riferimento:

- [auth-module-spec.md](c:/Users/ivan.lisciotto_webra/Desktop/project/planning/auth-module-spec.md)
- [11-tenant-admin-configuration.md](c:/Users/ivan.lisciotto_webra/Desktop/project/planning/docs/backend/11-tenant-admin-configuration.md)

## 6. Tenant e Multi-Tenancy

Il progetto non e ancora multi-tenant completo, ma il backend ha gia introdotto una base reale:

- schema `security.tenants`
- collegamento `security.users.tenant_id`
- utenti tenant-scoped
- audit locale tenant
- configurazione aziendale tenant-aware

Attualmente lo scoping tenant e applicato a:

- gestione utenti del tenant
- audit locale del tenant
- configurazione aziendale del tenant
- configurazione SMTP del tenant
- numerazioni documentali del tenant
- **anagrafiche** (primo dominio business tenant-aware)
- **articoli e categorie articolo** (secondo dominio business tenant-aware, con codice/nome univoci per tenant e validazione cross-tenant della categoria)
- **bolle / DDT** (terzo dominio, primo documento composito: testata + righe con snapshot, ciclo bozza/emessa/annullata, numerazione progressiva per tenant)

Non e ancora applicato a:

- fatture
- spedizioni

## 7. Frontend

Il frontend e oggi un client Vue 3 minimale ma funzionante per:

- test del flusso JWT
- shell gestionale di base
- mockup `Super Admin`
- mockup `Tenant Admin`

Stato attuale:

- login reale collegato al backend
- persistenza locale sessione
- guardie router per `admin` e `tenant_admin`
- dashboard ERP standard-user statica
- console `Super Admin` statica
- console `Tenant Admin` statica

Le console amministrative frontend non sono ancora tutte collegate ai dati reali backend.

## 8. Sicurezza e Compliance

Regole attive:

- password hashate
- JWT reali
- refresh token persistiti e revocabili
- audit log persistito
- segreti SMTP tenant cifrati lato backend
- documentazione OpenAPI obbligatoria e curata
- convenzione descrittiva del codice in italiano

Vincoli ancora aperti:

- acquisizione reale di `ip_address` e `user_agent`
- MFA eventuale
- rate limiting sugli endpoint auth
- gestione completa impersonation per assistenza Gestionale

## 9. Stato della Migrazione

La migrazione non e ancora nel dominio business.

Stato reale raggiunto:

- nucleo tecnico del backend costruito
- autenticazione reale pronta
- ruoli globali e tenant introdotti
- prime API tenant-aware reali implementate
- frontend di test e mockup enterprise disponibili

Modulo business ancora non implementato:

- `Anagrafiche`
- `Bolle`
- `Fatture`
- `Spedizioni`

## 10. Regole di Evoluzione

Ogni evoluzione deve rispettare queste regole:

- niente SQL diretto nei router
- ogni endpoint con OpenAPI curato
- ogni modifica strutturale passa da Alembic
- ogni feature nuova aggiorna `planning/docs`
- i ruoli e il tenant scope si applicano lato backend, non solo nel frontend
- i mockup frontend non devono essere confusi con funzionalita business gia operative

## 11. Documento di Handoff

Per riprendere rapidamente il progetto con un altro LLM o con un altro sviluppatore, il documento principale da leggere per primo e:

- [00-llm-handoff.md](c:/Users/ivan.lisciotto_webra/Desktop/project/planning/docs/00-llm-handoff.md)
