# Auth Service

> 43 nodes · cohesion 0.12

## Key Concepts

- **AuthService** (36 connections) — `backend/app/services/auth/auth_service.py`
- **LoginProtectionService** (24 connections) — `backend/app/services/auth/login_protection_service.py`
- **InvalidTokenError** (24 connections) — `backend/app/domain/security/exceptions.py`
- **LoginProtectionRepository** (23 connections) — `backend/app/repositories/security/login_protection_repository.py`
- **InactiveUserError** (19 connections) — `backend/app/domain/security/exceptions.py`
- **AuthSessionResult** (18 connections) — `backend/app/services/auth/auth_service.py`
- **SecurityRequestContext** (18 connections) — `backend/app/services/auth/auth_service.py`
- **str** (17 connections) — `backend/app/services/auth/auth_service.py`
- **JwtTokenManager** (17 connections) — `backend/app/core/security/jwt.py`
- **CurrentUserResponse** (16 connections) — `backend/app/services/auth/auth_service.py`
- **datetime** (15 connections) — `backend/app/services/auth/auth_service.py`
- **User** (15 connections) — `backend/app/services/auth/auth_service.py`
- **LoginRequest** (14 connections) — `backend/app/services/auth/auth_service.py`
- **Session** (14 connections) — `backend/app/services/auth/auth_service.py`
- **._genera_token_response()** (10 connections) — `backend/app/services/auth/auth_service.py`
- **.__init__()** (8 connections) — `backend/app/services/auth/auth_service.py`
- **.get_current_user()** (7 connections) — `backend/app/services/auth/auth_service.py`
- **.login()** (7 connections) — `backend/app/services/auth/auth_service.py`
- **.refresh()** (7 connections) — `backend/app/services/auth/auth_service.py`
- **._registra_evento_audit()** (7 connections) — `backend/app/services/auth/auth_service.py`
- **._crea_risposta_utente()** (6 connections) — `backend/app/services/auth/auth_service.py`
- **.logout()** (6 connections) — `backend/app/services/auth/auth_service.py`
- **auth_service.py** (5 connections) — `backend/app/services/auth/auth_service.py`
- **Session** (4 connections) — `backend/app/api/deps/auth.py`
- **LoginProtectionRepository** (3 connections) — `backend/app/services/auth/login_protection_service.py`
- *... and 18 more nodes in this community*

## Relationships

- [[Audit & User Models]] (52 shared connections)
- [[Community 48]] (20 shared connections)
- [[Login Protection / Lockout]] (20 shared connections)
- [[Community 31]] (13 shared connections)
- [[Community 33]] (10 shared connections)
- [[Auth Routes]] (8 shared connections)
- [[Community 51]] (8 shared connections)
- [[Community 68]] (4 shared connections)
- [[Community 42]] (1 shared connections)

## Source Files

- `backend/app/api/deps/auth.py`
- `backend/app/core/security/jwt.py`
- `backend/app/domain/security/exceptions.py`
- `backend/app/repositories/security/login_protection_repository.py`
- `backend/app/services/auth/auth_service.py`
- `backend/app/services/auth/login_protection_service.py`

## Audit Trail

- EXTRACTED: 137 (38%)
- INFERRED: 223 (62%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*