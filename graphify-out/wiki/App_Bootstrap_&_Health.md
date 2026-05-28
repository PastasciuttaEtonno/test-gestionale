# App Bootstrap & Health

> 45 nodes · cohesion 0.06

## Key Concepts

- **main.py** (11 connections) — `backend/app/main.py`
- **readiness_check()** (6 connections) — `backend/app/main.py`
- **request_context_middleware()** (6 connections) — `backend/app/main.py`
- **str** (6 connections) — `backend/app/main.py`
- **_check_redis()** (5 connections) — `backend/app/main.py`
- **reset_request_id()** (5 connections) — `backend/app/core/request_id.py`
- **set_request_id()** (5 connections) — `backend/app/core/request_id.py`
- **app_meta()** (4 connections) — `backend/app/main.py`
- **_check_database()** (4 connections) — `backend/app/main.py`
- **demo_readonly_middleware()** (4 connections) — `backend/app/main.py`
- **logging.py** (4 connections) — `backend/app/core/logging.py`
- **request_id.py** (4 connections) — `backend/app/core/request_id.py`
- **Request** (4 connections) — `backend/app/main.py`
- **configure_logging()** (4 connections) — `backend/app/core/logging.py`
- **JsonLogFormatter** (4 connections) — `backend/app/core/logging.py`
- **RequestContextFilter** (4 connections) — `backend/app/core/logging.py`
- **.filter()** (4 connections) — `backend/app/core/logging.py`
- **get_request_id()** (4 connections) — `backend/app/core/request_id.py`
- **healthcheck()** (3 connections) — `backend/app/main.py`
- **liveness_check()** (3 connections) — `backend/app/main.py`
- **str** (3 connections) — `backend/app/core/request_id.py`
- **.format()** (3 connections) — `backend/app/core/logging.py`
- **JSONResponse** (3 connections) — `backend/app/main.py`
- **LogRecord** (2 connections) — `backend/app/core/logging.py`
- **Token** (2 connections) — `backend/app/core/request_id.py`
- *... and 20 more nodes in this community*

## Relationships

- [[Community 42]] (1 shared connections)
- [[Community 55]] (1 shared connections)
- [[Auth Routes]] (1 shared connections)

## Source Files

- `backend/app/core/logging.py`
- `backend/app/core/request_id.py`
- `backend/app/main.py`

## Audit Trail

- EXTRACTED: 120 (94%)
- INFERRED: 7 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*