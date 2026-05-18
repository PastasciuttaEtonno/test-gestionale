# Code Quality and CI

## Obiettivo

Introdurre controlli rapidi e non eccessivamente rigidi per intercettare errori evidenti,
import non coerenti, problemi di stile e regressioni banali di build.

## Backend

Strumento scelto:

- `ruff`

Controlli attivi:

- `ruff check app alembic`
- `ruff format --check app alembic`
- `python -m compileall app alembic`
- `python -m pytest`

Regole attive:

- errori Python essenziali
- import ordinati
- upgrade sintattici semplici

Non sono attivi, in questa fase:

- type checking severo con `mypy`
- policy di coverage
- blocchi rigidi su complessita o docstring coverage
- integrazione test con database o Redis reali in CI

## Frontend

Strumento scelto:

- `eslint` con `eslint-plugin-vue`

Controlli attivi:

- `npm run lint`
- `npm run build`

Approccio:

- regole Vue essenziali
- config minimale
- niente obblighi estetici troppo invasivi

## Pipeline

Workflow:

- `.github/workflows/checks.yml`
- `.github/workflows/publish-backend-image.yml`

Job:

- `backend-checks`
- `frontend-checks`
- `publish-backend-image`

La pipeline deve restare veloce. Se un controllo introduce troppo attrito, va giustificato
prima di essere reso obbligatorio.

Baseline attuale backend in CI:

- test route-level su `health`
- test route-level su `auth`
- test unitari su dependency RBAC tenant-aware

Disciplina iniziale di publication:

- l'immagine Docker del backend viene pubblicata su `GHCR`
- la pubblicazione automatica parte solo dopo `Checks` completato con successo su `main`
- sono emessi tag `sha-*`, `main` e `latest`
- il deploy verso Aruba non e ancora incluso in questa fase
