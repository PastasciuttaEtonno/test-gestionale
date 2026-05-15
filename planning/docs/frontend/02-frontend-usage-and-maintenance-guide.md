# Guida Uso e Manutenzione Frontend

## Obiettivo

Spiegare come avviare, usare ed evolvere il frontend minimale di test del modulo `Auth & Identity`.

## Avvio locale

### Con Node

```bash
cd frontend
npm install
npm run dev
```

Il frontend risponde su `http://localhost:5173`.

### Con Docker Compose

```bash
docker compose up --build
```

Servizi esposti:

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000`
- swagger backend: `http://localhost:8000/docs`

## Check di qualita

```bash
cd frontend
npm install
npm run lint
npm run build
```

Approccio scelto:

- `eslint` con regole Vue essenziali
- build Vite come check strutturale finale

## Variabili

File di riferimento: `frontend/.env.example`

- `VITE_API_BASE_URL`: base path usato dal browser, di default `/api/v1`
- `VITE_PROXY_TARGET`: target del proxy Vite lato server

## Baseline versioni correnti

- runtime container: `node:24.14.1-alpine3.23`
- `Vue`: `3.5.34`
- `Axios`: `1.16.1`
- `Vite`: `8.0.13`
- `@vitejs/plugin-vue`: `6.0.7`
- `Tailwind CSS`: `4.3.0`

## Riferimento stilistico

La direzione visiva del gestionale e documentata in:

- [00-gestionale-visual-style.md](/c:/Users/ivan.lisciotto_webra/Desktop/project/planning/style/00-gestionale-visual-style.md)

## Come funziona

### Sessione

Lo stato auth e centralizzato in `src/stores/auth.js`.

La chiave `localStorage` usata e:

- `esseduesoft.auth.sessione`

Il payload memorizzato contiene:

- `accessToken`
- `refreshToken`
- `user`

### Interceptor

La request interceptor:

- legge l'access token dalla sessione
- aggiunge `Authorization: Bearer <token>`

La response interceptor:

- intercetta `401`
- prova il refresh una sola volta
- ritenta la richiesta originale
- in caso di fallimento, svuota la sessione locale

## Dove prestare attenzione

### Sicurezza

- la presenza di controlli di route lato Vue non sostituisce i controlli backend
- `localStorage` e accettato qui solo per il test client richiesto; per contesti piu sensibili andra rivalutato
- evitare di duplicare logica autorizzativa complessa nel frontend
- i riferimenti a funzioni amministrative devono essere nascosti ai non admin anche a livello di navigazione
- `admin` e `tenant_admin` devono vedere console differenti: il super admin Esseduesoft non deve navigare la console tenant, e il tenant admin non deve vedere la console globale Esseduesoft

### Mockup standard-user

- la dashboard ERP corrente e volutamente statica
- prima di collegarla al backend, mantenere separato il lavoro di layout dal lavoro di integrazione dati

### Mockup Super Admin

- la console `Super Admin` corrente e uno scaffold di prodotto
- tenants, licenze, metriche e audit globale sono dati dummy locali
- prima di integrare i dati reali, fissare perimetro funzionale e regole di sicurezza lato backend

### Mockup Tenant Admin

- la console `Tenant Admin` corrente e uno scaffold di prodotto per l'azienda cliente
- utenti, RBAC, SMTP, numerazioni e audit locale sono dati dummy locali
- la visibilita della console tenant admin e legata al ruolo reale `tenant_admin`
- la console non deve essere esposta al ruolo `admin`

### Manutenzione

- ogni nuova chiamata API deve passare da `src/services/`
- ogni nuova regola di accesso deve essere esplicitata in `router/index.js`
- evitare richieste Axios dirette dentro molte viste
- con Tailwind 4 il progetto usa `@tailwindcss/vite`; non reintrodurre `postcss.config.js` o `tailwind.config.js` senza una necessita concreta
- i nuovi componenti devono usare la palette grigio tecnico + rosso operativo definita nel planning
- i nuovi pattern visuali devono essere centralizzati in `src/components/ui/` o `src/components/layout/`
- l'header condiviso deve mantenere tre zone stabili: brand, navigazione, profilo/azioni
- le viste gestionali devono poter usare la larghezza piena della viewport quando serve densita informativa
- la sidebar ERP deve evolvere tramite componenti condivisi e non con markup duplicato nelle viste

### Evoluzione futura

Quando il frontend crescera:

- introdurre `Pinia` se lo stato diventera piu ricco
- separare layout, componenti business e componenti shared
- aggiungere test automatici UI e test di integrazione API

## Checklist modifica frontend

- aggiornare i contratti API usati se il backend cambia
- mantenere commenti e note descrittive in italiano
- aggiornare `planning/docs/frontend/` quando cambia il comportamento
- verificare login, `me`, refresh e pagina admin dopo ogni modifica auth
- eseguire `npm audit` e `npm run build` dopo ogni aggiornamento dipendenze
