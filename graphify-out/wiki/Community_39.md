# Community 39

> 15 nodes · cohesion 0.20

## Key Concepts

- **invalidate_cache_key_best_effort()** (10 connections) — `backend/app/core/cache.py`
- **build_tenant_dashboard_kpis_cache_key()** (8 connections) — `backend/app/core/cache.py`
- **get_or_set_model_cache()** (7 connections) — `backend/app/core/cache.py`
- **invalidate_cache_key()** (6 connections) — `backend/app/core/cache.py`
- **cache.py** (5 connections) — `backend/app/core/cache.py`
- **str** (4 connections) — `backend/app/core/cache.py`
- **Redis** (3 connections) — `backend/app/core/cache.py`
- **bool** (2 connections) — `backend/app/core/cache.py`
- **int** (1 connections) — `backend/app/core/cache.py`
- **Utility condivise per cache JSON e chiavi Redis tenant-aware.** (1 connections) — `backend/app/core/cache.py`
- **Restituisce la chiave Redis isolata per i KPI dashboard di un tenant.** (1 connections) — `backend/app/core/cache.py`
- **Legge un modello Pydantic da Redis o lo calcola e salva con TTL.** (1 connections) — `backend/app/core/cache.py`
- **Elimina una singola chiave di cache e indica se esisteva.** (1 connections) — `backend/app/core/cache.py`
- **Prova a invalidare una chiave senza interrompere il flusso applicativo.** (1 connections) — `backend/app/core/cache.py`
- **TModel** (1 connections) — `backend/app/core/cache.py`

## Relationships

- [[Articolo CRUD Methods]] (2 shared connections)
- [[Bolla Service]] (2 shared connections)
- [[Tenant Settings & Dashboard]] (2 shared connections)
- [[Audit & User Models]] (2 shared connections)
- [[Tenant Encryption & Sequences]] (2 shared connections)

## Source Files

- `backend/app/core/cache.py`

## Audit Trail

- EXTRACTED: 42 (81%)
- INFERRED: 10 (19%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*