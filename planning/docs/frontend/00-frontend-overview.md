# Frontend Overview

## Obiettivo

Fornire un client web minimale in `Vue 3` per validare il modulo `Auth & Identity` del backend FastAPI.

## Stack

- `Vue.js 3` con Composition API e `script setup`
- `Vite` come dev server e bundler
- `Vue Router` per routing e guardie
- `Pinia` per lo stato auth condiviso
- `Axios` come client HTTP centralizzato
- `Tailwind CSS v4` per styling (CSS-first, nessun `tailwind.config.js`)
- `PrimeVue v4` in modalità `unstyled: true` per componenti interattivi complessi

## Ambito attuale

- login enterprise con `identifier` e `password`, toggle visibilità nativo
- access token mantenuto solo in memoria
- refresh token mantenuto in cookie `HttpOnly`
- inizializzazione sessione tramite endpoint `POST /api/v1/auth/refresh`
- refresh automatico del token su `401`
- frontend completamente responsive mobile-first (375px → desktop)
- sidebar di navigazione globale in `AppShell`: persistente su desktop (colonna sinistra), drawer off-canvas su mobile via hamburger, gestita da `useSidebar.js`
- la sidebar mostra: Dashboard, Anagrafiche (reali), Tenant Admin / Super Admin (role-gated), moduli mockup futuri (Bolle, Fatture…) chiaramente disabilitati
- chiusura automatica del drawer al cambio di route (watch sul prop `routeName`)
- mockup ERP standard-user con toolbar e griglia dati con filtri reali (testo libero + Select tipo/stato)
- demo di task asincrono report con SSE real-time
- console `Tenant Admin` statica per l'azienda cliente
- console `Super Admin` statica per il personale Gestionale
- componenti UI condivisi per shell, card, bottoni, badge, label, tile KPI
- PrimeVue integrato per: Tooltip, Avatar, IconField, InputIcon, InputText, Select, Tag, Dialog, ProgressBar
- **Anagrafiche** — primo modulo business collegato ad API reali:
  - `AnagraficheView`: lista filtrata (IconField+InputText, Select tipo con PT, toggle "Solo attivi", reset filtri), righe cliccabili, modale create/edit, soft-delete
  - `AnagraficaDetailView`: hero card, dati fiscali, fatturazione elettronica, indirizzi, sidebar riepilogo, pulsante back con hover animato
  - routing `/anagrafiche` e `/anagrafiche/:id` con guardia `anagrafiche.read`

## Scelte attive

- `Axios` e stato auth centralizzato sono preferiti a fetch sparso nelle viste
- `Pinia` e usata in modo minimo per la sola sessione auth; eventuali store futuri vanno separati per dominio
- il polling dei task asincroni passa da servizi `Axios` dedicati e non da chiamate sparse nel markup
- il frontend usa guardie router dichiarative (`requiredRoles`, `requiredPermissions`) e una direttiva `v-can`
- l'autorizzazione reale resta di competenza del backend
- il refresh token non deve essere accessibile a JavaScript
- i messaggi e le note descrittive sono in italiano
- i pattern visuali devono essere centralizzati in `src/components/ui/` o `src/components/layout/`
- le funzioni admin non devono comparire nella navigazione di utenti non admin
- `admin` e `tenant_admin` devono vedere console diverse e separate
