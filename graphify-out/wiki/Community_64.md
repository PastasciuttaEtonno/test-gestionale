# Community 64

> 7 nodes · cohesion 0.29

## Key Concepts

- **get_event_publisher()** (5 connections) — `backend/app/api/deps/events.py`
- **events.py** (3 connections) — `backend/app/api/deps/events.py`
- **EventPublisher** (2 connections) — `backend/app/api/deps/events.py`
- **Redis** (2 connections) — `backend/app/api/deps/events.py`
- **Request** (2 connections) — `backend/app/api/deps/events.py`
- **Dependency per il bus eventi (EventPublisher).** (1 connections) — `backend/app/api/deps/events.py`
- **Restituisce l'EventPublisher collegato al client Redis condiviso.** (1 connections) — `backend/app/api/deps/events.py`

## Relationships

- [[Notifications & Events]] (3 shared connections)
- [[Community 42]] (1 shared connections)

## Source Files

- `backend/app/api/deps/events.py`

## Audit Trail

- EXTRACTED: 13 (81%)
- INFERRED: 3 (19%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*