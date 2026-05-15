# Frontend Overview

## Obiettivo

Fornire un client web minimale in `Vue 3` per validare il modulo `Auth & Identity` del backend FastAPI.

## Stack

- `Vue.js 3` con Composition API e `script setup`
- `Vite` come dev server e bundler
- `Vue Router` per routing e guardie
- `Axios` come client HTTP centralizzato
- `Tailwind CSS` per styling rapido

## Ambito attuale

- login con `identifier` e `password`
- access token mantenuto solo in memoria
- refresh token mantenuto in cookie `HttpOnly`
- inizializzazione sessione tramite endpoint `POST /api/v1/auth/refresh`
- refresh automatico del token su `401`
- mockup ERP standard-user con sidebar, toolbar e griglia dati statica
- console `Tenant Admin` statica per l'azienda cliente
- console `Super Admin` statica per il personale Esseduesoft
- primi componenti UI condivisi estratti per shell, card, bottoni, badge e label
- sidebar ERP trattata come pattern UI condiviso

## Scelte attive

- `Axios` e stato auth centralizzato sono preferiti a fetch sparso nelle viste
- il frontend usa guardie router, ma l'autorizzazione reale resta di competenza del backend
- il refresh token non deve essere accessibile a JavaScript
- i messaggi e le note descrittive sono in italiano
- i pattern visuali devono essere centralizzati in `src/components/ui/` o `src/components/layout/`
- le funzioni admin non devono comparire nella navigazione di utenti non admin
- `admin` e `tenant_admin` devono vedere console diverse e separate
