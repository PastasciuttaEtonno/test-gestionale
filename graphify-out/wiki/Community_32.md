# Community 32

> 21 nodes · cohesion 0.12

## Key Concepts

- **Notification** (9 connections) — `backend/app/models/core/notification.py`
- **str** (6 connections) — `backend/app/repositories/core/notification_repository.py`
- **.get_for_user()** (5 connections) — `backend/app/repositories/core/notification_repository.py`
- **Notification** (5 connections) — `backend/app/repositories/core/notification_repository.py`
- **int** (4 connections) — `backend/app/repositories/core/notification_repository.py`
- **.count_unread()** (4 connections) — `backend/app/repositories/core/notification_repository.py`
- **.create()** (4 connections) — `backend/app/repositories/core/notification_repository.py`
- **.get_by_id()** (4 connections) — `backend/app/repositories/core/notification_repository.py`
- **.mark_all_read()** (4 connections) — `backend/app/repositories/core/notification_repository.py`
- **.mark_read()** (3 connections) — `backend/app/repositories/core/notification_repository.py`
- **notification.py** (2 connections) — `backend/app/models/core/notification.py`
- **Session** (2 connections) — `backend/app/repositories/core/notification_repository.py`
- **.__init__()** (2 connections) — `backend/app/repositories/core/notification_repository.py`
- **Modello ORM delle notifiche applicative.** (1 connections) — `backend/app/models/core/notification.py`
- **Notifica applicativa persistente per un utente o un intero tenant.** (1 connections) — `backend/app/models/core/notification.py`
- **Crea e persiste una nuova notifica.** (1 connections) — `backend/app/repositories/core/notification_repository.py`
- **Restituisce le notifiche visibili all'utente (personali + broadcast tenant).** (1 connections) — `backend/app/repositories/core/notification_repository.py`
- **Conta le notifiche non lette visibili all'utente.** (1 connections) — `backend/app/repositories/core/notification_repository.py`
- **Cerca una notifica per id.** (1 connections) — `backend/app/repositories/core/notification_repository.py`
- **Segna una notifica come letta.** (1 connections) — `backend/app/repositories/core/notification_repository.py`
- **Segna come lette tutte le notifiche visibili all'utente. Restituisce il conteggi** (1 connections) — `backend/app/repositories/core/notification_repository.py`

## Relationships

- [[Notifications & Events]] (8 shared connections)
- [[Tenant Settings & Dashboard]] (1 shared connections)
- [[Community 67]] (1 shared connections)

## Source Files

- `backend/app/models/core/notification.py`
- `backend/app/repositories/core/notification_repository.py`

## Audit Trail

- EXTRACTED: 52 (84%)
- INFERRED: 10 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*