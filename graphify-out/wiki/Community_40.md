# Community 40

> 15 nodes · cohesion 0.16

## Key Concepts

- **SyncEventPublisher** (13 connections) — `backend/app/services/events/sync_publisher.py`
- **genera_report_massivo_task()** (6 connections) — `backend/app/tasks/report_tasks.py`
- **int** (4 connections) — `backend/app/tasks/report_tasks.py`
- **str** (4 connections) — `backend/app/tasks/report_tasks.py`
- **.close()** (3 connections) — `backend/app/services/events/sync_publisher.py`
- **sync_publisher.py** (2 connections) — `backend/app/services/events/sync_publisher.py`
- **report_tasks.py** (2 connections) — `backend/app/tasks/report_tasks.py`
- **.__exit__()** (2 connections) — `backend/app/services/events/sync_publisher.py`
- **Publisher sincrono per contesti Celery (non async).** (1 connections) — `backend/app/services/events/sync_publisher.py`
- **Pubblica eventi SSE da un contesto sincrono (Celery task).      Crea una conness** (1 connections) — `backend/app/services/events/sync_publisher.py`
- **Chiude la connessione Redis.** (1 connections) — `backend/app/services/events/sync_publisher.py`
- **.__enter__()** (1 connections) — `backend/app/services/events/sync_publisher.py`
- **.__init__()** (1 connections) — `backend/app/services/events/sync_publisher.py`
- **Task Celery per lavorazioni report lunghe.** (1 connections) — `backend/app/tasks/report_tasks.py`
- **Simula un report massivo usando una sessione DB propria del worker.** (1 connections) — `backend/app/tasks/report_tasks.py`

## Relationships

- [[Community 61]] (4 shared connections)
- [[Tenant Settings & Dashboard]] (2 shared connections)
- [[Articolo CRUD Methods]] (2 shared connections)
- [[Report Task Routes]] (1 shared connections)

## Source Files

- `backend/app/services/events/sync_publisher.py`
- `backend/app/tasks/report_tasks.py`

## Audit Trail

- EXTRACTED: 32 (74%)
- INFERRED: 11 (26%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*