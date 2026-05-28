# Auth Routes

> 45 nodes · cohesion 0.07

## Key Concepts

- **ProductionService** (21 connections) — `backend/app/services/production/production_service.py`
- **refresh_token()** (10 connections) — `backend/app/api/v1/auth/routes.py`
- **update_production()** (10 connections) — `backend/app/api/v1/production/routes.py`
- **login()** (9 connections) — `backend/app/api/v1/auth/routes.py`
- **logout()** (9 connections) — `backend/app/api/v1/auth/routes.py`
- **routes.py** (8 connections) — `backend/app/api/v1/auth/routes.py`
- **build_security_request_context()** (8 connections) — `backend/app/core/security/request_context.py`
- **_imposta_refresh_cookie()** (6 connections) — `backend/app/api/v1/auth/routes.py`
- **Response** (6 connections) — `backend/app/api/v1/auth/routes.py`
- **_rimuovi_refresh_cookie()** (5 connections) — `backend/app/api/v1/auth/routes.py`
- **AuthService** (4 connections) — `backend/app/api/v1/auth/routes.py`
- **Request** (4 connections) — `backend/app/api/v1/auth/routes.py`
- **routes.py** (4 connections) — `backend/app/api/v1/production/routes.py`
- **request_context.py** (4 connections) — `backend/app/core/security/request_context.py`
- **get_production_service()** (4 connections) — `backend/app/api/v1/production/routes.py`
- **ProductionService** (4 connections) — `backend/app/api/v1/production/routes.py`
- **me()** (3 connections) — `backend/app/api/v1/auth/routes.py`
- **AuthSessionResponse** (3 connections) — `backend/app/api/v1/auth/routes.py`
- **CurrentUserResponse** (3 connections) — `backend/app/api/v1/auth/routes.py`
- **CurrentUserResponse** (3 connections) — `backend/app/api/v1/production/routes.py`
- **EventPublisher** (3 connections) — `backend/app/api/v1/production/routes.py`
- **ProductionUpdateRequest** (3 connections) — `backend/app/api/v1/production/routes.py`
- **ProductionUpdateResponse** (3 connections) — `backend/app/api/v1/production/routes.py`
- **Redis** (3 connections) — `backend/app/api/v1/production/routes.py`
- **Request** (3 connections) — `backend/app/api/v1/production/routes.py`
- *... and 20 more nodes in this community*

## Relationships

- [[Audit & User Models]] (10 shared connections)
- [[Notifications & Events]] (9 shared connections)
- [[Auth Service]] (8 shared connections)
- [[Community 42]] (4 shared connections)
- [[App Bootstrap & Health]] (1 shared connections)
- [[Tenant Settings & Dashboard]] (1 shared connections)
- [[Articolo CRUD Methods]] (1 shared connections)

## Source Files

- `backend/app/api/v1/auth/routes.py`
- `backend/app/api/v1/production/routes.py`
- `backend/app/core/security/request_context.py`
- `backend/app/services/production/production_service.py`

## Audit Trail

- EXTRACTED: 121 (71%)
- INFERRED: 49 (29%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*