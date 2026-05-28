# User Management

> 33 nodes · cohesion 0.16

## Key Concepts

- **UserService** (36 connections) — `backend/app/services/users/user_service.py`
- **CurrentUserResponse** (20 connections) — `backend/app/services/users/user_service.py`
- **str** (18 connections) — `backend/app/services/users/user_service.py`
- **UserResponse** (14 connections) — `backend/app/services/users/user_service.py`
- **User** (12 connections) — `backend/app/services/users/user_service.py`
- **.change_role()** (12 connections) — `backend/app/services/users/user_service.py`
- **.change_status()** (11 connections) — `backend/app/services/users/user_service.py`
- **.update_user()** (11 connections) — `backend/app/services/users/user_service.py`
- **.create_user()** (10 connections) — `backend/app/services/users/user_service.py`
- **._get_scoped_user()** (10 connections) — `backend/app/services/users/user_service.py`
- **._to_response()** (10 connections) — `backend/app/services/users/user_service.py`
- **.get_user()** (8 connections) — `backend/app/services/users/user_service.py`
- **._resolve_target_tenant_id()** (8 connections) — `backend/app/services/users/user_service.py`
- **._registra_evento_audit()** (7 connections) — `backend/app/services/users/user_service.py`
- **._require_actor_tenant()** (7 connections) — `backend/app/services/users/user_service.py`
- **.list_users()** (6 connections) — `backend/app/services/users/user_service.py`
- **._list_users_for_actor()** (6 connections) — `backend/app/services/users/user_service.py`
- **._validate_role_assignment()** (6 connections) — `backend/app/services/users/user_service.py`
- **._verifica_password_non_compromessa()** (5 connections) — `backend/app/services/users/user_service.py`
- **Modifica lo stato attivo di un utente.** (1 connections) — `backend/app/services/users/user_service.py`
- **Modifica il ruolo di un utente.** (1 connections) — `backend/app/services/users/user_service.py`
- **Converte il modello ORM utente nello schema di risposta.** (1 connections) — `backend/app/services/users/user_service.py`
- **Restituisce la lista utenti compatibile con il perimetro dell'attore.** (1 connections) — `backend/app/services/users/user_service.py`
- **Restituisce un utente applicando il perimetro del ruolo chiamante.** (1 connections) — `backend/app/services/users/user_service.py`
- **Determina e valida il tenant target del nuovo utente.** (1 connections) — `backend/app/services/users/user_service.py`
- *... and 8 more nodes in this community*

## Relationships

- [[Audit & User Models]] (26 shared connections)
- [[User Admin Routes]] (16 shared connections)
- [[Community 48]] (11 shared connections)
- [[Tenant Encryption & Sequences]] (5 shared connections)
- [[Community 33]] (5 shared connections)

## Source Files

- `backend/app/services/users/user_service.py`

## Audit Trail

- EXTRACTED: 180 (78%)
- INFERRED: 51 (22%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*