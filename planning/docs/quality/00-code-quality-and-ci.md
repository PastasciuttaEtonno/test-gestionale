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

Regole attive:

- errori Python essenziali
- import ordinati
- upgrade sintattici semplici

Non sono attivi, in questa fase:

- type checking severo con `mypy`
- policy di coverage
- blocchi rigidi su complessita o docstring coverage

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

Job:

- `backend-checks`
- `frontend-checks`

La pipeline deve restare veloce. Se un controllo introduce troppo attrito, va giustificato
prima di essere reso obbligatorio.
