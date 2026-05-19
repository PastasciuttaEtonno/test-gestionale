# Cloud Migration Plan

Questa cartella contiene il piano operativo per portare il progetto da runtime locale `Docker Compose + Celery + Redis + PostgreSQL` a una baseline Azure piu solida, multitenant e gestibile da un unico sviluppatore.

Obiettivi:

- evitare una migrazione guidata da `click ops`
- definire i servizi Azure target e i loro vincoli reali
- tradurre l'architettura in modifiche concrete al codice
- preparare pipeline, observability, secret management e rollout

Documenti:

- [01-target-architecture.md](/c:/Users/ivan.lisciotto_webra/Desktop/project/planning/cloud/01-target-architecture.md)
- [02-code-adaptation-plan.md](/c:/Users/ivan.lisciotto_webra/Desktop/project/planning/cloud/02-code-adaptation-plan.md)
- [03-infrastructure-and-delivery-plan.md](/c:/Users/ivan.lisciotto_webra/Desktop/project/planning/cloud/03-infrastructure-and-delivery-plan.md)
- [04-rollout-backlog.md](/c:/Users/ivan.lisciotto_webra/Desktop/project/planning/cloud/04-rollout-backlog.md)

Decisione architetturale di base:

- backend HTTP su `Azure Functions Flex Consumption`
- gateway pubblico su `Azure API Management Standard v2`
- code applicative su `Azure Service Bus`
- database su `Azure Database for PostgreSQL Flexible Server`
- servizi privati in VNet

Decisione di migrazione applicativa:

- mantenere il backend come `modular monolith`
- non spezzare subito in microservizi
- sostituire progressivamente `Celery + Redis broker` con adapter asincroni basati su `Service Bus`
- tenere `Redis` opzionale e introdurlo solo se il costo/beneficio resta favorevole dopo il lancio

Regola guida:

- prima si rende il codice portabile su Azure
- poi si automatizza il provisioning
- solo dopo si effettua il cutover del runtime
