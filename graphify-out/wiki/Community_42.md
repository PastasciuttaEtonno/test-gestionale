# Community 42

> 14 nodes · cohesion 0.14

## Key Concepts

- **FastAPI** (39 connections) — `backend/app/main.py`
- **rbac.py** (3 connections) — `backend/app/api/deps/rbac.py`
- **articolo_service.py** (3 connections) — `backend/app/services/articoli/articolo_service.py`
- **categoria_service.py** (3 connections) — `backend/app/services/articoli/categoria_service.py`
- **dashboard_service.py** (3 connections) — `backend/app/services/dashboard/dashboard_service.py`
- **notification_service.py** (3 connections) — `backend/app/services/notifications/notification_service.py`
- **tenant_settings_service.py** (3 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **Servizio applicativo per il modulo Articoli.** (1 connections) — `backend/app/services/articoli/articolo_service.py`
- **Servizio applicativo per le categorie articolo.** (1 connections) — `backend/app/services/articoli/categoria_service.py`
- **router.py** (1 connections) — `backend/app/api/v1/router.py`
- **Servizi applicativi per KPI dashboard tenant-aware con cache Redis.** (1 connections) — `backend/app/services/dashboard/dashboard_service.py`
- **Dependency RBAC dichiarative e tenant-aware.  Pattern di autorizzazione nel pr** (1 connections) — `backend/app/api/deps/rbac.py`
- **Servizio applicativo per la creazione e gestione delle notifiche.** (1 connections) — `backend/app/services/notifications/notification_service.py`
- **Servizio applicativo per le impostazioni tenant admin.** (1 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`

## Relationships

- [[Articoli Services]] (4 shared connections)
- [[Auth Routes]] (4 shared connections)
- [[Report Task Routes]] (3 shared connections)
- [[Settings Routes]] (2 shared connections)
- [[Community 55]] (2 shared connections)
- [[Audit Routes]] (2 shared connections)
- [[BOM Module]] (2 shared connections)
- [[Finance Cost Module]] (2 shared connections)
- [[User Admin Routes]] (2 shared connections)
- [[Tenant Settings & Dashboard]] (1 shared connections)
- [[Notifications & Events]] (1 shared connections)
- [[App Bootstrap & Health]] (1 shared connections)

## Source Files

- `backend/app/api/deps/rbac.py`
- `backend/app/api/v1/router.py`
- `backend/app/main.py`
- `backend/app/services/articoli/articolo_service.py`
- `backend/app/services/articoli/categoria_service.py`
- `backend/app/services/dashboard/dashboard_service.py`
- `backend/app/services/notifications/notification_service.py`
- `backend/app/services/tenant_admin/tenant_settings_service.py`

## Audit Trail

- EXTRACTED: 64 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*