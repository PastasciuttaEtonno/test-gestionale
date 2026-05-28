# Community 55

> 10 nodes · cohesion 0.22

## Key Concepts

- **lifespan()** (4 connections) — `backend/app/main.py`
- **redis.py** (4 connections) — `backend/app/core/redis.py`
- **create_redis_client()** (4 connections) — `backend/app/core/redis.py`
- **get_redis_client()** (4 connections) — `backend/app/core/redis.py`
- **Redis** (2 connections) — `backend/app/core/redis.py`
- **Inizializza e chiude il client Redis condiviso dell'applicazione.** (1 connections) — `backend/app/main.py`
- **Request** (1 connections) — `backend/app/core/redis.py`
- **Bootstrap e dependency del client Redis asincrono.** (1 connections) — `backend/app/core/redis.py`
- **Crea il client Redis asincrono condiviso dall'app FastAPI.** (1 connections) — `backend/app/core/redis.py`
- **Restituisce il client Redis salvato nello stato dell'applicazione.** (1 connections) — `backend/app/core/redis.py`

## Relationships

- [[Community 42]] (2 shared connections)
- [[App Bootstrap & Health]] (1 shared connections)

## Source Files

- `backend/app/core/redis.py`
- `backend/app/main.py`

## Audit Trail

- EXTRACTED: 21 (91%)
- INFERRED: 2 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*