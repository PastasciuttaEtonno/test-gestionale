# User Admin Routes

> 31 nodes · cohesion 0.12

## Key Concepts

- **UserNotFoundError** (26 connections) — `backend/app/services/users/user_service.py`
- **routes.py** (9 connections) — `backend/app/api/v1/users/routes.py`
- **UserService** (9 connections) — `backend/app/api/v1/users/routes.py`
- **CurrentUserResponse** (8 connections) — `backend/app/api/v1/users/routes.py`
- **UserResponse** (7 connections) — `backend/app/api/v1/users/routes.py`
- **change_user_role()** (7 connections) — `backend/app/api/v1/users/routes.py`
- **change_user_status()** (7 connections) — `backend/app/api/v1/users/routes.py`
- **update_user()** (7 connections) — `backend/app/api/v1/users/routes.py`
- **str** (6 connections) — `backend/app/api/v1/users/routes.py`
- **create_user()** (6 connections) — `backend/app/api/v1/users/routes.py`
- **get_user()** (6 connections) — `backend/app/api/v1/users/routes.py`
- **get_user_service()** (5 connections) — `backend/app/api/v1/users/routes.py`
- **list_users()** (5 connections) — `backend/app/api/v1/users/routes.py`
- **user_service.py** (4 connections) — `backend/app/services/users/user_service.py`
- **ChangeUserRoleRequest** (3 connections) — `backend/app/api/v1/users/routes.py`
- **ChangeUserStatusRequest** (3 connections) — `backend/app/api/v1/users/routes.py`
- **CreateUserRequest** (3 connections) — `backend/app/api/v1/users/routes.py`
- **Redis** (3 connections) — `backend/app/api/v1/users/routes.py`
- **Session** (3 connections) — `backend/app/api/v1/users/routes.py`
- **UpdateUserRequest** (3 connections) — `backend/app/api/v1/users/routes.py`
- **UserListResponse** (3 connections) — `backend/app/api/v1/users/routes.py`
- **Route di amministrazione utenti.  Pattern di autorizzazione: role guard + scop** (1 connections) — `backend/app/api/v1/users/routes.py`
- **Crea un nuovo utente applicativo.      La richiesta viene validata, la passwor** (1 connections) — `backend/app/api/v1/users/routes.py`
- **Aggiorna i metadati modificabili di un utente.      In questa fase sono espost** (1 connections) — `backend/app/api/v1/users/routes.py`
- **Modifica lo stato di attivazione di un account utente.      L'utente di destin** (1 connections) — `backend/app/api/v1/users/routes.py`
- *... and 6 more nodes in this community*

## Relationships

- [[User Management]] (16 shared connections)
- [[Audit & User Models]] (4 shared connections)
- [[Community 42]] (2 shared connections)
- [[Community 48]] (2 shared connections)
- [[Community 68]] (1 shared connections)
- [[Tenant Encryption & Sequences]] (1 shared connections)
- [[Community 33]] (1 shared connections)

## Source Files

- `backend/app/api/v1/users/routes.py`
- `backend/app/services/users/user_service.py`

## Audit Trail

- EXTRACTED: 102 (71%)
- INFERRED: 41 (29%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*