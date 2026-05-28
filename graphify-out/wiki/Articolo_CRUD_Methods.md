# Articolo CRUD Methods

> 39 nodes · cohesion 0.11

## Key Concepts

- **ArticoloRepository** (68 connections) — `backend/app/repositories/core/articolo_repository.py`
- **EventTypes** (49 connections) — `backend/app/schemas/events/sse.py`
- **Articolo** (34 connections) — `backend/app/models/core/articolo.py`
- **str** (13 connections) — `backend/app/services/articoli/articolo_service.py`
- **.create_articolo()** (8 connections) — `backend/app/services/articoli/articolo_service.py`
- **._notifica_mutazione()** (8 connections) — `backend/app/services/articoli/articolo_service.py`
- **.update_articolo()** (8 connections) — `backend/app/services/articoli/articolo_service.py`
- **ArticoloResponse** (8 connections) — `backend/app/services/articoli/articolo_service.py`
- **Articolo** (7 connections) — `backend/app/services/articoli/articolo_service.py`
- **._get_or_404()** (6 connections) — `backend/app/services/articoli/articolo_service.py`
- **ArticoloListParams** (6 connections) — `backend/app/services/articoli/articolo_service.py`
- **ArticoloCreateRequest** (6 connections) — `backend/app/services/articoli/articolo_service.py`
- **ArticoloListResponse** (6 connections) — `backend/app/services/articoli/articolo_service.py`
- **ArticoloRepository** (6 connections) — `backend/app/services/articoli/articolo_service.py`
- **ArticoloUpdateRequest** (6 connections) — `backend/app/services/articoli/articolo_service.py`
- **CategoriaArticoloRepository** (6 connections) — `backend/app/services/articoli/articolo_service.py`
- **EventPublisher** (6 connections) — `backend/app/services/articoli/articolo_service.py`
- **Redis** (6 connections) — `backend/app/services/articoli/articolo_service.py`
- **.delete_articolo()** (5 connections) — `backend/app/services/articoli/articolo_service.py`
- **.get_articolo()** (5 connections) — `backend/app/services/articoli/articolo_service.py`
- **.__init__()** (5 connections) — `backend/app/services/articoli/articolo_service.py`
- **.list_articoli()** (5 connections) — `backend/app/services/articoli/articolo_service.py`
- **._valida_categoria_nel_tenant()** (5 connections) — `backend/app/services/articoli/articolo_service.py`
- **Session** (3 connections) — `backend/app/repositories/core/categoria_articolo_repository.py`
- **articolo_repository.py** (2 connections) — `backend/app/repositories/core/articolo_repository.py`
- *... and 14 more nodes in this community*

## Relationships

- [[Articoli Services]] (42 shared connections)
- [[Bolla Repository & Events]] (25 shared connections)
- [[Notifications & Events]] (20 shared connections)
- [[Community 38]] (11 shared connections)
- [[Bolle Routes]] (10 shared connections)
- [[Bolla Service]] (8 shared connections)
- [[Audit & User Models]] (8 shared connections)
- [[Tenant Settings & Dashboard]] (7 shared connections)
- [[Categoria CRUD Methods]] (5 shared connections)
- [[Community 39]] (2 shared connections)
- [[Community 40]] (2 shared connections)
- [[Articoli Schemas]] (1 shared connections)

## Source Files

- `backend/app/models/core/articolo.py`
- `backend/app/repositories/core/articolo_repository.py`
- `backend/app/repositories/core/categoria_articolo_repository.py`
- `backend/app/schemas/events/sse.py`
- `backend/app/services/articoli/articolo_service.py`

## Audit Trail

- EXTRACTED: 108 (36%)
- INFERRED: 196 (64%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*