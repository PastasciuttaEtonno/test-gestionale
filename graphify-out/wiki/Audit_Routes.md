# Audit Routes

> 37 nodes · cohesion 0.07

## Key Concepts

- **AuditService** (15 connections) — `backend/app/services/audit/audit_service.py`
- **._to_list_response()** (6 connections) — `backend/app/services/audit/audit_service.py`
- **get_audit_log()** (5 connections) — `backend/app/api/v1/admin/routes.py`
- **.list_events_for_tenant()** (5 connections) — `backend/app/services/audit/audit_service.py`
- **get_tenant_audit_log()** (5 connections) — `backend/app/api/v1/tenant_admin/routes.py`
- **get_audit_service()** (4 connections) — `backend/app/api/v1/admin/routes.py`
- **.list_events()** (4 connections) — `backend/app/services/audit/audit_service.py`
- **AuditLogResponse** (4 connections) — `backend/app/schemas/audit/responses.py`
- **routes.py** (4 connections) — `backend/app/api/v1/admin/routes.py`
- **AuditLogListResponse** (4 connections) — `backend/app/services/audit/audit_service.py`
- **get_audit_service()** (4 connections) — `backend/app/api/v1/tenant_admin/routes.py`
- **AuditLogListResponse** (3 connections) — `backend/app/schemas/audit/responses.py`
- **AuditService** (3 connections) — `backend/app/api/v1/admin/routes.py`
- **routes.py** (3 connections) — `backend/app/api/v1/tenant_admin/routes.py`
- **AuditService** (3 connections) — `backend/app/api/v1/tenant_admin/routes.py`
- **responses.py** (3 connections) — `backend/app/schemas/audit/responses.py`
- **AuditLogListResponse** (2 connections) — `backend/app/api/v1/admin/routes.py`
- **CurrentUserResponse** (2 connections) — `backend/app/api/v1/admin/routes.py`
- **Session** (2 connections) — `backend/app/api/v1/admin/routes.py`
- **AuditLogListResponse** (2 connections) — `backend/app/api/v1/tenant_admin/routes.py`
- **CurrentUserResponse** (2 connections) — `backend/app/api/v1/tenant_admin/routes.py`
- **Session** (2 connections) — `backend/app/api/v1/tenant_admin/routes.py`
- **audit_service.py** (2 connections) — `backend/app/services/audit/audit_service.py`
- **str** (2 connections) — `backend/app/services/audit/audit_service.py`
- **Route amministrative.** (1 connections) — `backend/app/api/v1/admin/routes.py`
- *... and 12 more nodes in this community*

## Relationships

- [[Audit & User Models]] (4 shared connections)
- [[Auth Schemas]] (2 shared connections)
- [[Community 42]] (2 shared connections)

## Source Files

- `backend/app/api/v1/admin/routes.py`
- `backend/app/api/v1/tenant_admin/routes.py`
- `backend/app/schemas/audit/responses.py`
- `backend/app/services/audit/audit_service.py`

## Audit Trail

- EXTRACTED: 83 (80%)
- INFERRED: 21 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*