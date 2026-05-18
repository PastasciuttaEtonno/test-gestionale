# Backend Overview

## Stack

- `FastAPI`: esposizione API e OpenAPI
- `Pydantic`: validazione, serializzazione, contratti API
- `SQLAlchemy`: ORM e mapping verso PostgreSQL
- `PostgreSQL`: persistenza primaria
- `Celery + Redis`: code asincrone per lavori lunghi
- `uv`: gestione dipendenze e workflow Python
- `Docker`: runtime coerente tra sviluppo e test

## Obiettivo architetturale

Il backend non viene impostato come insieme di microservizi distribuiti. Viene costruito come `core_service` modulare, con confini interni netti tra sicurezza, dominio, persistenza e API.

## Stato corrente

- backend avviabile via `uv` e Docker
- router v1 attivi
- RBAC dichiarativo tenant-aware disponibile tramite dependency `RequirePermission`
- modulo `Auth` persistito su PostgreSQL
- modelli `security` definiti e migrati via Alembic
- servizi `Auth`, `Users`, `Audit` e `Tenant Admin` collegati al DB reale
- scoping tenant attivo su utenti, audit locale e configurazione aziendale
- infrastruttura task asincroni pronta con broker Redis e worker Celery
- Redis asincrono usato anche per cache tenant-aware e rate limiting API

## Vincolo guida

Ogni nuovo modulo deve integrarsi nella stessa struttura a layer senza introdurre logica SQL negli endpoint o dipendenze trasversali non controllate.
