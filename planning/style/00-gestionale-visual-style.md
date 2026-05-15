# Stile Gestionale

## Obiettivo

Definire una direzione visiva coerente per il gestionale Esseduesoft, in modo che
frontend e componenti futuri condividano gli stessi criteri di colore, gerarchia
e percezione operativa.

## Principi

- look sobrio e tecnico, non marketing
- interfaccia leggibile per uso prolungato
- contrasto chiaro tra contenuto neutro e azioni rilevanti
- accento rosso usato come identita e priorita visiva, non come rumore continuo

## Palette

### Grigi principali

- `steel-50`: `#f6f7f8`
- `steel-100`: `#eceef1`
- `steel-200`: `#d7dce2`
- `steel-400`: `#8b95a1`
- `steel-700`: `#39424d`
- `steel-900`: `#1e252c`

### Rossi principali

- `accent-50`: `#fff1f1`
- `accent-100`: `#ffd9d9`
- `accent-300`: `#ff8e8e`
- `accent-500`: `#c62828`
- `accent-700`: `#8f1d1d`
- `accent-900`: `#5e1313`

### Colori di supporto

- bordo neutro: `#d7dce2`
- sfondo pagina: `#f3f4f6`
- superficie primaria: `#ffffff`
- superficie secondaria: `#f8fafb`
- testo principale: `#1e252c`
- testo secondario: `#5a6572`

## Uso della palette

### Grigi

Usare i grigi per:

- sfondi di pagina
- card
- bordi
- testi secondari
- tabelle e superfici gestionali

### Rosso

Usare il rosso per:

- pulsanti primari
- link attivi o evidenziati
- highlight di sezione
- badge critici o amministrativi

Non usare il rosso come colore dominante di tutta la pagina.

## Componenti

### Header

- sfondo chiaro quasi pieno
- bordo inferiore netto
- piccolo accento rosso nel marchio o nella navigazione attiva
- layout a tre zone: brand, navigazione, profilo/azioni
- allineamento verticale sempre centrato
- link di navigazione e bottoni con altezza uniforme
- username con peso forte ma dimensione armonizzata ai link di navigazione

### Card

- fondo bianco
- bordi morbidi ma non troppo “tondi”
- ombra leggera e ampia
- eventuale filetto superiore rosso per pannelli prioritari

### Bottoni

- primario: rosso pieno
- secondario: bianco o grigio chiaro con bordo neutro
- stati hover con incremento di contrasto, non con animazioni vistose

### Tabelle

- header grigio chiaro
- righe leggibili
- niente eccessi cromatici
- rosso solo per selezioni, badge o dati di attenzione

## Tipografia

- stile pulito e funzionale
- pesi forti solo per heading e punti di stato
- uppercase usato solo per micro-label e metadata

## Motion

- transizioni rapide e discrete
- evitare effetti vistosi
- privilegiare feedback funzionale: hover, focus, loading

## Regole evolutive

- ogni nuova vista deve partire da questa palette
- se viene introdotto un nuovo colore, deve avere una motivazione funzionale
- i componenti condivisi devono usare token semantici, non colori hardcoded sparsi
