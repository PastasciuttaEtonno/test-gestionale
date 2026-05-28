# Audit & User Models

> 50 nodes · cohesion 0.09

## Key Concepts

- **AuditRepository** (48 connections) — `backend/app/repositories/security/audit_repository.py`
- **AuditLog** (46 connections) — `backend/app/models/security/audit_log.py`
- **User** (40 connections) — `backend/app/models/security/user.py`
- **AuditEventType** (35 connections) — `backend/app/domain/security/enums.py`
- **SecurityRequestContext** (22 connections) — `backend/app/core/security/request_context.py`
- **LogoutResponse** (14 connections) — `backend/app/services/auth/auth_service.py`
- **RoleCode** (12 connections) — `backend/app/domain/security/enums.py`
- **.update_production_status()** (11 connections) — `backend/app/services/production/production_service.py`
- **CurrentUserResponse** (10 connections) — `backend/app/services/production/production_service.py`
- **CreateUserRequest** (10 connections) — `backend/app/services/users/user_service.py`
- **EventPublisher** (9 connections) — `backend/app/services/production/production_service.py`
- **ProductionUpdateRequest** (9 connections) — `backend/app/services/production/production_service.py`
- **ProductionUpdateResponse** (9 connections) — `backend/app/services/production/production_service.py`
- **Redis** (9 connections) — `backend/app/services/production/production_service.py`
- **SecurityRequestContext** (9 connections) — `backend/app/services/production/production_service.py`
- **Session** (9 connections) — `backend/app/services/production/production_service.py`
- **str** (9 connections) — `backend/app/services/production/production_service.py`
- **ChangeUserRoleRequest** (9 connections) — `backend/app/services/users/user_service.py`
- **ChangeUserStatusRequest** (9 connections) — `backend/app/services/users/user_service.py`
- **UpdateUserRequest** (9 connections) — `backend/app/services/users/user_service.py`
- **UserListResponse** (9 connections) — `backend/app/services/users/user_service.py`
- **AuditLog** (5 connections) — `backend/app/repositories/security/audit_repository.py`
- **._validate_tenant_scope()** (5 connections) — `backend/app/services/production/production_service.py`
- **.list_events_by_tenant()** (4 connections) — `backend/app/repositories/security/audit_repository.py`
- **.__init__()** (3 connections) — `backend/app/services/audit/audit_service.py`
- *... and 25 more nodes in this community*

## Relationships

- [[Auth Service]] (52 shared connections)
- [[User Management]] (26 shared connections)
- [[Tenant Settings & Dashboard]] (22 shared connections)
- [[Community 48]] (21 shared connections)
- [[Community 33]] (10 shared connections)
- [[Auth Routes]] (10 shared connections)
- [[Articolo CRUD Methods]] (8 shared connections)
- [[Notifications & Events]] (8 shared connections)
- [[Tenant Encryption & Sequences]] (5 shared connections)
- [[Audit Routes]] (4 shared connections)
- [[User Admin Routes]] (4 shared connections)
- [[Community 39]] (2 shared connections)

## Source Files

- `backend/app/core/security/request_context.py`
- `backend/app/domain/security/enums.py`
- `backend/app/models/security/audit_log.py`
- `backend/app/models/security/user.py`
- `backend/app/repositories/security/audit_repository.py`
- `backend/app/services/audit/audit_service.py`
- `backend/app/services/auth/auth_service.py`
- `backend/app/services/production/production_service.py`
- `backend/app/services/users/user_service.py`

## Audit Trail

- EXTRACTED: 95 (23%)
- INFERRED: 311 (77%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*