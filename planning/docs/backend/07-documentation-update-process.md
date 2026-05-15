# Documentation Update Process

## Regola di processo

Ogni prompt che produce una modifica concreta al progetto deve aggiornare anche la documentazione pertinente sotto `planning/`.

## Procedura minima

1. identificare quali aree sono state toccate
2. aggiornare il file di stato se cambia l'avanzamento reale
3. aggiornare il file tecnico piu vicino al cambiamento
4. creare un nuovo file solo se emerge un tema stabile e riutilizzabile

## Quando creare nuovi file

Creare un nuovo file quando:

- nasce un nuovo modulo tecnico
- emerge una nuova convenzione rilevante
- un documento esistente diventerebbe troppo grande o ambiguo

## Quando aggiornare file esistenti

Aggiornare file esistenti quando:

- cambia lo stato del backend
- cambia il workflow runtime
- cambia una decisione architetturale gia documentata
- cambiano standard di API, sicurezza o persistenza

## Regola di qualità

La documentazione non deve ripetere il codice riga per riga. Deve spiegare:

- perché esiste una scelta
- dove si trova
- come va estesa correttamente
