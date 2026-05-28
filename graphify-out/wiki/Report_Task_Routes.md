# Report Task Routes

> 42 nodes · cohesion 0.07

## Key Concepts

- **ReportTaskService** (15 connections) — `backend/app/services/reports/report_task_service.py`
- **._assert_tenant_exists()** (6 connections) — `backend/app/services/reports/report_task_service.py`
- **.enqueue_report_generation()** (6 connections) — `backend/app/services/reports/report_task_service.py`
- **generate_report()** (6 connections) — `backend/app/api/v1/reports/routes.py`
- **get_task_status()** (6 connections) — `backend/app/api/v1/tasks/routes.py`
- **str** (5 connections) — `backend/app/services/reports/report_task_service.py`
- **get_db_session_context()** (5 connections) — `backend/app/core/db.py`
- **._validate_tenant_scope()** (5 connections) — `backend/app/services/reports/report_task_service.py`
- **routes.py** (4 connections) — `backend/app/api/v1/reports/routes.py`
- **routes.py** (4 connections) — `backend/app/api/v1/tasks/routes.py`
- **db.py** (4 connections) — `backend/app/core/db.py`
- **.get_task_status()** (4 connections) — `backend/app/services/reports/report_task_service.py`
- **ReportTaskService** (3 connections) — `backend/app/api/v1/reports/routes.py`
- **ReportTaskService** (3 connections) — `backend/app/api/v1/tasks/routes.py`
- **report_task_service.py** (3 connections) — `backend/app/services/reports/report_task_service.py`
- **CurrentUserResponse** (3 connections) — `backend/app/services/reports/report_task_service.py`
- **get_db_session()** (3 connections) — `backend/app/core/db.py`
- **get_report_task_service()** (3 connections) — `backend/app/api/v1/reports/routes.py`
- **get_report_task_service()** (3 connections) — `backend/app/api/v1/tasks/routes.py`
- **CurrentUserResponse** (2 connections) — `backend/app/api/v1/reports/routes.py`
- **CurrentUserResponse** (2 connections) — `backend/app/api/v1/tasks/routes.py`
- **str** (2 connections) — `backend/app/api/v1/tasks/routes.py`
- **TaskStatusResponse** (2 connections) — `backend/app/api/v1/tasks/routes.py`
- **Session** (2 connections) — `backend/app/core/db.py`
- **TaskStatusResponse** (2 connections) — `backend/app/services/reports/report_task_service.py`
- *... and 17 more nodes in this community*

## Relationships

- [[Tenant Encryption & Sequences]] (5 shared connections)
- [[Community 42]] (3 shared connections)
- [[Tenant Settings & Dashboard]] (1 shared connections)
- [[Community 40]] (1 shared connections)

## Source Files

- `backend/app/api/v1/reports/routes.py`
- `backend/app/api/v1/tasks/routes.py`
- `backend/app/core/db.py`
- `backend/app/services/reports/report_task_service.py`

## Audit Trail

- EXTRACTED: 98 (80%)
- INFERRED: 24 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*