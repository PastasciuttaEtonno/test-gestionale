# Community 31

> 22 nodes · cohesion 0.15

## Key Concepts

- **auth.py** (10 connections) — `backend/app/api/deps/auth.py`
- **CurrentUserResponse** (10 connections) — `backend/app/api/deps/auth.py`
- **get_current_user()** (8 connections) — `backend/app/api/deps/auth.py`
- **AuthService** (7 connections) — `backend/app/api/deps/auth.py`
- **get_sse_user()** (7 connections) — `backend/app/api/deps/auth.py`
- **get_optional_current_user()** (6 connections) — `backend/app/api/deps/auth.py`
- **HTTPAuthorizationCredentials** (6 connections) — `backend/app/api/deps/auth.py`
- **str** (5 connections) — `backend/app/api/deps/auth.py`
- **get_auth_service()** (4 connections) — `backend/app/api/deps/auth.py`
- **get_active_user()** (3 connections) — `backend/app/api/deps/auth.py`
- **require_admin()** (3 connections) — `backend/app/api/deps/auth.py`
- **require_admin_or_tenant_admin()** (3 connections) — `backend/app/api/deps/auth.py`
- **require_tenant_admin()** (3 connections) — `backend/app/api/deps/auth.py`
- **Dependency di autenticazione e autorizzazione.  Le dependency di ruolo (requir** (1 connections) — `backend/app/api/deps/auth.py`
- **Verifica che l'utente corrente abbia ruolo admin o tenant admin.** (1 connections) — `backend/app/api/deps/auth.py`
- **Dependency per endpoint SSE: accetta token da header Bearer o query param.** (1 connections) — `backend/app/api/deps/auth.py`
- **Restituisce la dependency del servizio di autenticazione.** (1 connections) — `backend/app/api/deps/auth.py`
- **Risolve l'utente corrente a partire dal token di accesso.** (1 connections) — `backend/app/api/deps/auth.py`
- **Risolve l'utente corrente quando disponibile, altrimenti restituisce None.** (1 connections) — `backend/app/api/deps/auth.py`
- **Verifica che l'utente corrente sia attivo.** (1 connections) — `backend/app/api/deps/auth.py`
- **Verifica che l'utente corrente abbia ruolo amministratore.** (1 connections) — `backend/app/api/deps/auth.py`
- **Verifica che l'utente corrente abbia ruolo tenant admin.** (1 connections) — `backend/app/api/deps/auth.py`

## Relationships

- [[Auth Service]] (13 shared connections)
- [[Community 42]] (1 shared connections)

## Source Files

- `backend/app/api/deps/auth.py`

## Audit Trail

- EXTRACTED: 72 (86%)
- INFERRED: 12 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*