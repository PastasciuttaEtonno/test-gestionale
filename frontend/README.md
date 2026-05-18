# Frontend Auth Client

Client minimale `Vue 3` usato per validare il flusso `JWT` del backend Esseduesoft.

## Baseline versioni correnti

- Node container: `node:24.14.1-alpine3.23`
- `Vue`: `3.5.34`
- `Pinia`: `3.0.4`
- `Axios`: `1.16.1`
- `Vite`: `8.0.13`
- `@vitejs/plugin-vue`: `6.0.7`
- `Tailwind CSS`: `4.3.0`

## Avvio locale

```bash
npm install
npm run dev
```

## Check di qualita

```bash
npm install
npm run lint
npm run build
```

URL:

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000`

## Avvio con Docker

```bash
docker compose up --build
```

## Funzioni attive

- login con `identifier` e `password`
- access token mantenuto solo in memoria
- refresh token mantenuto in cookie `HttpOnly`
- ripristino sessione tramite `POST /api/v1/auth/refresh`
- refresh automatico del token tramite interceptor Axios
- mockup ERP statico per utenti standard con sidebar, header e lista documenti
- demo di task asincrono report con polling su backend `Celery + Redis`
- console `Tenant Admin` statica per l'amministratore della singola azienda cliente
- console `Super Admin` statica per il personale Esseduesoft
- console `Super Admin` visibile solo a utenti con ruolo `admin`
- console `Tenant Admin` visibile solo a utenti con ruolo `tenant_admin`
- le viste gestionali usano la larghezza completa della viewport per massimizzare lo spazio utile

## File principali

- `src/components/layout/AppShell.vue`: shell condivisa applicativa
- `src/components/ui/`: componenti UI condivisi
- `src/components/ui/SidebarSection.vue`: pattern condiviso per sidebar ERP
- `src/router/index.js`: rotte e guardie
- `src/stores/auth.js`: store Pinia della sessione auth in memoria e inizializzazione auth
- `src/lib/http.js`: client Axios e refresh centralizzato
- `src/services/auth.js`: chiamate API
- `src/services/reports.js`: accodamento report e polling stato task
- `src/views/`: viste di login, dashboard e aree amministrative

## Attenzioni

- la protezione reale resta nel backend
- il refresh token non e leggibile dal frontend: viene inviato solo dal browser tramite cookie `HttpOnly`
- `withCredentials` deve restare attivo nel client Axios per supportare il refresh cookie
- Pinia e introdotta solo per lo stato `auth`; non usare ancora uno store globale monolitico per i futuri moduli business
- se cambiano shape o URL degli endpoint backend, aggiornare prima `src/services/` e poi la documentazione in `planning/docs/frontend/`
- Tailwind 4 usa il plugin Vite ufficiale `@tailwindcss/vite`, quindi non ci sono piu `postcss.config.js` e `tailwind.config.js` in questa fase
- nuovi pattern visivi vanno aggiunti prima in `src/components/ui/` e poi riusati nelle viste
- i non-admin non devono vedere riferimenti alle sezioni amministrative nella shell applicativa
- la vista standard-user corrente e un mockup statico: dati dummy locali, nessuna logica business
- per le viste ERP evitare wrapper stretti tipo `max-w-*` sulla shell principale
- la vista `Super Admin` corrente e anch'essa un mockup statico: nessuna logica business, nessuna persistenza dedicata
- la vista `Tenant Admin` corrente e un mockup statico; la visibilita reale del ruolo e distinta da quella del `Super Admin`
