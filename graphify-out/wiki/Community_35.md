# Community 35

> 19 nodes · cohesion 0.13

## Key Concepts

- **Permission** (7 connections) — `backend/app/models/security/permission.py`
- **RolePermission** (7 connections) — `backend/app/models/security/role_permission.py`
- **Role** (6 connections) — `backend/app/models/security/role.py`
- **str** (5 connections) — `backend/app/repositories/security/role_repository.py`
- **Session** (4 connections) — `backend/app/repositories/security/role_repository.py`
- **Role** (4 connections) — `backend/app/repositories/security/role_repository.py`
- **.get_role()** (4 connections) — `backend/app/repositories/security/role_repository.py`
- **.list_permissions_by_role()** (3 connections) — `backend/app/repositories/security/role_repository.py`
- **permission.py** (2 connections) — `backend/app/models/security/permission.py`
- **role_permission.py** (2 connections) — `backend/app/models/security/role_permission.py`
- **role.py** (2 connections) — `backend/app/models/security/role.py`
- **.__init__()** (2 connections) — `backend/app/repositories/security/role_repository.py`
- **Modello ORM del permesso.** (1 connections) — `backend/app/models/security/permission.py`
- **Permesso di sicurezza.** (1 connections) — `backend/app/models/security/permission.py`
- **Modello ORM di associazione ruolo-permesso.** (1 connections) — `backend/app/models/security/role_permission.py`
- **Associazione tra ruolo e permesso.** (1 connections) — `backend/app/models/security/role_permission.py`
- **Modello ORM del ruolo.** (1 connections) — `backend/app/models/security/role.py`
- **Restituisce un singolo ruolo.** (1 connections) — `backend/app/repositories/security/role_repository.py`
- **Restituisce i permessi associati a un ruolo.** (1 connections) — `backend/app/repositories/security/role_repository.py`

## Relationships

- [[Community 48]] (6 shared connections)
- [[Tenant Settings & Dashboard]] (3 shared connections)

## Source Files

- `backend/app/models/security/permission.py`
- `backend/app/models/security/role.py`
- `backend/app/models/security/role_permission.py`
- `backend/app/repositories/security/role_repository.py`

## Audit Trail

- EXTRACTED: 34 (62%)
- INFERRED: 21 (38%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*