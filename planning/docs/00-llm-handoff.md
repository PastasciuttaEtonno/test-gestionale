# LLM Handoff

## Scopo

Questo documento serve come punto di ingresso rapido per un altro LLM o per un altro sviluppatore che debba riprendere il progetto senza contesto pregresso.

## Contesto progetto

- azienda: **Esseduesoft S.r.l.**
- dominio: gestionale enterprise per aziende ceramiche/logistiche
- origine: applicativo desktop legacy in VB/VB.NET
- target: web app moderna
- approccio corrente: **modular monolith**

## Stato reale del progetto

Il progetto **non** e ancora nel dominio business principale.  
La parte realmente costruita oggi e il nucleo tecnico della piattaforma:

- backend FastAPI reale
- PostgreSQL reale
- autenticazione JWT reale
- refresh token persistiti
- audit persistito
- ruoli `admin`, `tenant_admin`, `user`
- primo scoping tenant reale
- frontend Vue 3 di test e mockup enterprise

## Cosa funziona davvero oggi

### Backend

- `login`
- `refresh`
- `logout`
- `me`
- CRUD utenti
- audit globale super admin
- audit locale tenant
- configurazione aziendale tenant-aware
- configurazione SMTP tenant-aware
- numerazioni documentali tenant-aware

### Frontend

- login reale
- persistenza sessione in `localStorage`
- route guard per `admin` e `tenant_admin`
- dashboard standard-user statica
- console `Super Admin` statica
- console `Tenant Admin` statica

## Cosa e solo mockup

Queste viste esistono ma **non sono ancora collegate a business logic reale**:

- dashboard ERP standard-user
- console `Super Admin`
- gran parte della console `Tenant Admin`

Il frontend oggi e soprattutto:

- client di test auth
- shell UI
- base visiva per i moduli futuri

## Cosa non esiste ancora

- anagrafiche reali
- bolle reali
- fatture reali
- spedizioni reali
- reporting reale
- worker async reale
- redis reale
- api gateway reale
- upload reale del logo aziendale
- test SMTP reale
- impersonation reale Esseduesoft

## Architettura corrente

### Backend

- framework: `FastAPI`
- contratti: `Pydantic`
- ORM: `SQLAlchemy`
- DB: `PostgreSQL`
- migrations: `Alembic`
- dipendenze: `uv`
- containerizzazione: `Docker Compose`

### Frontend

- framework: `Vue 3`
- bundler: `Vite`
- styling: `Tailwind CSS`
- HTTP client: `Axios`
- routing: `Vue Router`

## Schemi database attivi

### `security`

- `roles`
- `permissions`
- `users`
- `tenants`
- `role_permissions`
- `refresh_tokens`
- `audit_log`

### `core`

- `tenant_company_settings`
- `tenant_smtp_settings`
- `tenant_document_sequences`

## Regole di ruolo attuali

### `admin`

- e il super admin Esseduesoft
- vede audit globale
- vede tutti gli utenti
- non usa la console tenant

### `tenant_admin`

- appartiene a un solo tenant
- vede solo utenti del proprio tenant
- vede solo audit locale del proprio tenant
- gestisce configurazione aziendale del proprio tenant
- non accede al perimetro globale Esseduesoft

### `user`

- ruolo operativo base
- nessuna funzione amministrativa

## Contratti e tenant scoping

Regola critica:

- il `tenant_id` **non** deve essere trattato come dato affidabile proveniente dal frontend
- il `tenant_id` va derivato dal profilo autenticato corrente

Questo e gia vero nei service tenant-aware implementati.

## Sicurezza attuale

- password utenti hashate
- JWT reali
- refresh token persistiti e revocabili
- audit log reale
- password SMTP cifrata lato backend
- OpenAPI curata endpoint per endpoint
- commenti, docstring e messaggi descrittivi in italiano

## Convenzioni operative da rispettare

- SQL nei repository, non nei router
- logica applicativa nei service
- schemi API Pydantic espliciti
- `Field(description=...)` e `examples` sugli schemi
- docstring endpoint in italiano
- aggiornare `planning/docs` a ogni modifica sostanziale
- usare Alembic per ogni evoluzione schema

## Credenziali demo correnti

- `admin / admin123`
- `tenant.admin / tenant123`
- `user / user123`

Tenant demo:

- `Ceramica Demo S.r.l.`

## File da leggere per primi

Ordine consigliato:

1. [planning/struttura.md](c:/Users/ivan.lisciotto_webra/Desktop/project/planning/struttura.md)
2. [planning/docs/project-state/current-state.md](c:/Users/ivan.lisciotto_webra/Desktop/project/planning/docs/project-state/current-state.md)
3. [planning/docs/backend/10-backend-usage-and-maintenance-guide.md](c:/Users/ivan.lisciotto_webra/Desktop/project/planning/docs/backend/10-backend-usage-and-maintenance-guide.md)
4. [planning/docs/backend/11-tenant-admin-configuration.md](c:/Users/ivan.lisciotto_webra/Desktop/project/planning/docs/backend/11-tenant-admin-configuration.md)
5. [planning/docs/frontend/02-frontend-usage-and-maintenance-guide.md](c:/Users/ivan.lisciotto_webra/Desktop/project/planning/docs/frontend/02-frontend-usage-and-maintenance-guide.md)

## Prossimi step coerenti

Le direzioni piu sensate da qui sono:

1. collegare il frontend `Tenant Admin` alle API reali appena introdotte
2. introdurre `Anagrafiche` come primo dominio business tenant-aware
3. aggiungere test automatici API per scoping `admin` vs `tenant_admin`
4. introdurre `ip_address` e `user_agent` reali nell'audit

## Rischi o limiti da tenere presenti

- il frontend puo dare l'impressione di essere piu avanzato del backend: molte viste sono ancora mockup
- il tenant scoping e reale, ma solo su alcuni moduli
- il documento `auth-module-spec.md` e una specifica viva: va tenuto allineato a ogni salto architetturale
- non esiste ancora una strategia completa di migrazione del dominio legacy verso i moduli business
