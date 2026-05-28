# Notifications & Events

> 37 nodes · cohesion 0.10

## Key Concepts

- **EventPublisher** (102 connections) — `backend/app/services/events/event_publisher.py`
- **NotificationRepository** (20 connections) — `backend/app/repositories/core/notification_repository.py`
- **NotificationService** (20 connections) — `backend/app/services/notifications/notification_service.py`
- **CurrentUserResponse** (7 connections) — `backend/app/services/notifications/notification_service.py`
- **.mark_read()** (6 connections) — `backend/app/services/notifications/notification_service.py`
- **MarkReadResponse** (5 connections) — `backend/app/services/notifications/notification_service.py`
- **str** (5 connections) — `backend/app/services/notifications/notification_service.py`
- **.create_and_publish()** (5 connections) — `backend/app/services/notifications/notification_service.py`
- **.list_notifications()** (5 connections) — `backend/app/services/notifications/notification_service.py`
- **EventPublisher** (4 connections) — `backend/app/services/notifications/notification_service.py`
- **int** (4 connections) — `backend/app/services/notifications/notification_service.py`
- **NotificationListResponse** (4 connections) — `backend/app/services/notifications/notification_service.py`
- **NotificationResponse** (4 connections) — `backend/app/services/notifications/notification_service.py`
- **Session** (4 connections) — `backend/app/services/notifications/notification_service.py`
- **._assert_readable()** (4 connections) — `backend/app/services/notifications/notification_service.py`
- **.mark_all_read()** (4 connections) — `backend/app/services/notifications/notification_service.py`
- **EventPublisher** (3 connections) — `backend/app/api/v1/notifications/routes.py`
- **int** (3 connections) — `backend/app/api/v1/notifications/routes.py`
- **NotificationListResponse** (3 connections) — `backend/app/api/v1/notifications/routes.py`
- **NotificationResponse** (3 connections) — `backend/app/api/v1/notifications/routes.py`
- **Session** (3 connections) — `backend/app/api/v1/notifications/routes.py`
- **str** (3 connections) — `backend/app/api/v1/notifications/routes.py`
- **.__init__()** (3 connections) — `backend/app/services/notifications/notification_service.py`
- **notification_repository.py** (2 connections) — `backend/app/repositories/core/notification_repository.py`
- **event_publisher.py** (2 connections) — `backend/app/services/events/event_publisher.py`
- *... and 12 more nodes in this community*

## Relationships

- [[Articolo CRUD Methods]] (20 shared connections)
- [[Articoli Services]] (18 shared connections)
- [[Bolla Repository & Events]] (14 shared connections)
- [[Community 41]] (12 shared connections)
- [[Bolle Routes]] (10 shared connections)
- [[Auth Routes]] (9 shared connections)
- [[Community 32]] (8 shared connections)
- [[Audit & User Models]] (8 shared connections)
- [[Community 60]] (4 shared connections)
- [[Bolla Service]] (4 shared connections)
- [[Community 64]] (3 shared connections)
- [[Community 42]] (1 shared connections)

## Source Files

- `backend/app/api/v1/notifications/routes.py`
- `backend/app/repositories/core/notification_repository.py`
- `backend/app/services/events/event_publisher.py`
- `backend/app/services/notifications/notification_service.py`

## Audit Trail

- EXTRACTED: 86 (36%)
- INFERRED: 155 (64%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*