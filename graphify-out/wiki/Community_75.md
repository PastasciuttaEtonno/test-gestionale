# Community 75

> 5 nodes · cohesion 0.40

## Key Concepts

- **create_pubsub_redis_client()** (4 connections) — `backend/app/core/pubsub.py`
- **pubsub.py** (2 connections) — `backend/app/core/pubsub.py`
- **Redis** (1 connections) — `backend/app/core/pubsub.py`
- **Client Redis dedicato alle connessioni pub/sub degli eventi applicativi.** (1 connections) — `backend/app/core/pubsub.py`
- **Crea un client Redis fresco per un subscriber pub/sub (db 3).      Ogni stream S** (1 connections) — `backend/app/core/pubsub.py`

## Relationships

- [[Community 57]] (1 shared connections)

## Source Files

- `backend/app/core/pubsub.py`

## Audit Trail

- EXTRACTED: 8 (89%)
- INFERRED: 1 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*