# Login Protection / Lockout

> 36 nodes · cohesion 0.08

## Key Concepts

- **LoginProtection** (15 connections) — `backend/app/models/security/login_protection.py`
- **str** (10 connections) — `backend/app/services/auth/login_protection_service.py`
- **.get_lock_result()** (7 connections) — `backend/app/services/auth/login_protection_service.py`
- **.get_lock_state()** (7 connections) — `backend/app/services/auth/login_protection_service.py`
- **.register_failed_attempt()** (7 connections) — `backend/app/services/auth/login_protection_service.py`
- **._register_failed_attempt_for_key()** (7 connections) — `backend/app/services/auth/login_protection_service.py`
- **LoginProtectionResult** (6 connections) — `backend/app/services/auth/login_protection_service.py`
- **._iter_scope_keys()** (6 connections) — `backend/app/services/auth/login_protection_service.py`
- **.clear_state()** (5 connections) — `backend/app/services/auth/login_protection_service.py`
- **.is_locked()** (5 connections) — `backend/app/services/auth/login_protection_service.py`
- **._max_attempts_for_scope()** (5 connections) — `backend/app/services/auth/login_protection_service.py`
- **int** (4 connections) — `backend/app/services/auth/login_protection_service.py`
- **LoginProtection** (4 connections) — `backend/app/services/auth/login_protection_service.py`
- **.get_entry()** (4 connections) — `backend/app/repositories/security/login_protection_repository.py`
- **LoginProtection** (3 connections) — `backend/app/repositories/security/login_protection_repository.py`
- **login_protection_service.py** (3 connections) — `backend/app/services/auth/login_protection_service.py`
- **bool** (3 connections) — `backend/app/services/auth/login_protection_service.py`
- **.save()** (3 connections) — `backend/app/repositories/security/login_protection_repository.py`
- **login_protection.py** (2 connections) — `backend/app/models/security/login_protection.py`
- **Session** (2 connections) — `backend/app/repositories/security/login_protection_repository.py`
- **str** (2 connections) — `backend/app/repositories/security/login_protection_repository.py`
- **.__init__()** (2 connections) — `backend/app/repositories/security/login_protection_repository.py`
- **Servizio applicativo per rate limiting e cooldown del login.** (1 connections) — `backend/app/services/auth/login_protection_service.py`
- **Azzera lo stato di protezione login dopo autenticazione riuscita.** (1 connections) — `backend/app/services/auth/login_protection_service.py`
- **Restituisce le chiavi logiche da proteggere per un login.** (1 connections) — `backend/app/services/auth/login_protection_service.py`
- *... and 11 more nodes in this community*

## Relationships

- [[Auth Service]] (20 shared connections)
- [[Tenant Settings & Dashboard]] (1 shared connections)
- [[Community 67]] (1 shared connections)

## Source Files

- `backend/app/models/security/login_protection.py`
- `backend/app/repositories/security/login_protection_repository.py`
- `backend/app/services/auth/login_protection_service.py`

## Audit Trail

- EXTRACTED: 101 (80%)
- INFERRED: 25 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*