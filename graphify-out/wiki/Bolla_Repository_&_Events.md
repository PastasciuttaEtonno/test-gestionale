# Bolla Repository & Events

> 28 nodes · cohesion 0.15

## Key Concepts

- **BollaRepository** (41 connections) — `backend/app/repositories/core/bolla_repository.py`
- **Bolla** (32 connections) — `backend/app/models/core/bolla.py`
- **BollaRiga** (21 connections) — `backend/app/models/core/bolla_riga.py`
- **AnagraficaRepository** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **ArticoloRepository** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **BollaCreateRequest** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **BollaListResponse** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **BollaUpdateRequest** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **EventPublisher** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **Redis** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **RigaCreateRequest** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **RigaUpdateRequest** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **BollaListParams** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **BollaRepository** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **EventPublisher** (7 connections) — `backend/app/api/v1/bolle/routes.py`
- **Redis** (7 connections) — `backend/app/api/v1/bolle/routes.py`
- **Session** (7 connections) — `backend/app/api/v1/bolle/routes.py`
- **.__init__()** (6 connections) — `backend/app/services/bolle/bolla_service.py`
- **.list_bolle()** (5 connections) — `backend/app/services/bolle/bolla_service.py`
- **_service()** (5 connections) — `backend/app/api/v1/bolle/routes.py`
- **Session** (3 connections) — `backend/app/repositories/core/bolla_repository.py`
- **bolla_repository.py** (2 connections) — `backend/app/repositories/core/bolla_repository.py`
- **.__init__()** (2 connections) — `backend/app/repositories/core/bolla_repository.py`
- **Restituisce la lista paginata delle bolle del tenant.** (1 connections) — `backend/app/services/bolle/bolla_service.py`
- **Documento di trasporto (DDT) tenant-aware con testata e righe.** (1 connections) — `backend/app/models/core/bolla.py`
- *... and 3 more nodes in this community*

## Relationships

- [[Articolo CRUD Methods]] (25 shared connections)
- [[Bolla Service]] (23 shared connections)
- [[Anagrafica Models]] (14 shared connections)
- [[Notifications & Events]] (14 shared connections)
- [[Bolle Routes]] (12 shared connections)
- [[Community 34]] (12 shared connections)
- [[Tenant Settings & Dashboard]] (8 shared connections)
- [[Articoli Services]] (3 shared connections)
- [[Tenant Encryption & Sequences]] (2 shared connections)
- [[Articoli Schemas]] (2 shared connections)
- [[Community 67]] (2 shared connections)

## Source Files

- `backend/app/api/v1/bolle/routes.py`
- `backend/app/models/core/bolla.py`
- `backend/app/models/core/bolla_riga.py`
- `backend/app/repositories/core/bolla_repository.py`
- `backend/app/services/bolle/bolla_service.py`

## Audit Trail

- EXTRACTED: 57 (25%)
- INFERRED: 174 (75%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*