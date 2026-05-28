# BOM Module

> 39 nodes · cohesion 0.08

## Key Concepts

- **BomRepository** (17 connections) — `backend/app/repositories/core/bom_repository.py`
- **BomService** (10 connections) — `backend/app/services/bom/bom_service.py`
- **Bom** (8 connections) — `backend/app/models/core/bom.py`
- **get_bom()** (6 connections) — `backend/app/api/v1/bom/routes.py`
- **routes.py** (5 connections) — `backend/app/api/v1/bom/routes.py`
- **Session** (5 connections) — `backend/app/api/v1/bom/routes.py`
- **str** (5 connections) — `backend/app/api/v1/bom/routes.py`
- **resolve_bom_tenant_id()** (5 connections) — `backend/app/api/v1/bom/routes.py`
- **BomService** (5 connections) — `backend/app/api/v1/bom/routes.py`
- **BomResponse** (4 connections) — `backend/app/api/v1/bom/routes.py`
- **CurrentUserResponse** (4 connections) — `backend/app/api/v1/bom/routes.py`
- **.get_bom()** (4 connections) — `backend/app/services/bom/bom_service.py`
- **get_bom_service()** (4 connections) — `backend/app/api/v1/bom/routes.py`
- **.get_bom()** (4 connections) — `backend/app/repositories/core/bom_repository.py`
- **str** (3 connections) — `backend/app/repositories/core/bom_repository.py`
- **bom_service.py** (3 connections) — `backend/app/services/bom/bom_service.py`
- **.__init__()** (3 connections) — `backend/app/services/bom/bom_service.py`
- **.get_bom_tenant_id()** (3 connections) — `backend/app/repositories/core/bom_repository.py`
- **bom.py** (2 connections) — `backend/app/models/core/bom.py`
- **bom_repository.py** (2 connections) — `backend/app/repositories/core/bom_repository.py`
- **Session** (2 connections) — `backend/app/repositories/core/bom_repository.py`
- **BomResponse** (2 connections) — `backend/app/services/bom/bom_service.py`
- **Session** (2 connections) — `backend/app/services/bom/bom_service.py`
- **str** (2 connections) — `backend/app/services/bom/bom_service.py`
- **Bom** (2 connections) — `backend/app/repositories/core/bom_repository.py`
- *... and 14 more nodes in this community*

## Relationships

- [[Articoli Services]] (5 shared connections)
- [[Community 42]] (2 shared connections)
- [[Tenant Settings & Dashboard]] (1 shared connections)
- [[Community 67]] (1 shared connections)

## Source Files

- `backend/app/api/v1/bom/routes.py`
- `backend/app/models/core/bom.py`
- `backend/app/repositories/core/bom_repository.py`
- `backend/app/services/bom/bom_service.py`

## Audit Trail

- EXTRACTED: 81 (64%)
- INFERRED: 46 (36%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*