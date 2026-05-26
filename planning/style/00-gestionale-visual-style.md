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

## Integrazione PrimeVue

Il progetto usa **PrimeVue v4 in modalità `unstyled: true`** per componenti ad alta complessità
logica o con comportamento interattivo non triviale da replicare.

### Principio

PrimeVue non porta stili propri. Ogni componente PrimeVue viene stilizzato interamente tramite
il sistema **Pass-Through (PT)**, applicando le stesse utility class Tailwind v4 usate nei
componenti custom.

### Cosa non usare

- **Non importare** `primevue/passthrough/tailwind` — quel preset è per Tailwind v3 e non
  riconosce i token custom (`brand-500`, `steel-900`).
- **Non importare** `@primevue/themes` — serve solo per la modalità styled (Aura, Lara, Nora).
- **Non importare** `primeicons` — usare SVG inline per le icone dei componenti.
- **Non usare PrimeVue** per `<input>` semplici, toggle booleani, o elementi che non aggiungono
  logica reale rispetto a HTML nativo — es. il toggle password usa `ref` locale + `<input :type>`.

### Componenti attivi

| Componente | Dove usato | Valore aggiunto |
|---|---|---|
| `Tooltip` | AppShell | Tooltip accessibili senza implementazione custom |
| `Avatar` | AppShell | Label avatar con fallback iniziale |
| `IconField` + `InputIcon` + `InputText` | DashboardView | Input con icona posizionata correttamente |
| `Select` | DashboardView | Dropdown con keyboard nav, `show-clear`, opzioni filtrabili |
| `Tag` | DashboardView, AdminOnlyView, TenantAdminView | Badge semantico con PT status-aware |
| `ProgressBar` | AdminOnlyView | Barra utilizzo risorse con valore percentuale |

### Componenti candidati futuri

| Componente | Quando introdurlo |
|---|---|
| **DataTable** | Quando le tabelle mockup si collegano ad API reali (sorting, filtering, pagination server-side) |
| **Dialog** | Form di dettaglio, conferme distruttive, modal complessi |
| **DatePicker** | Filtri data/range su documenti |
| **MultiSelect** | Assegnazione ruoli e permessi multipli |

### Pattern PT — oggetto statico

```js
const ptInputText = {
  root: {
    class: "h-11 rounded-xl border border-steel-200 bg-steel-50 px-4 text-sm text-steel-900 ...",
  },
};
```

```vue
<InputText v-model="valore" :pt="ptInputText" />
```

### Pattern PT — funzione status-aware

```js
function ptTag(stato) {
  const critico = ["Bloccabile", "Scaduto", "Da osservare"].includes(stato);
  return {
    root: {
      class: critico
        ? "... bg-brand-500 text-white border-brand-500"
        : "... bg-brand-50 text-brand-700 border-brand-100",
    },
  };
}
```

```vue
<Tag :value="tenant.stato" :pt="ptTag(tenant.stato)" />
```

### Confini di responsabilità

| Componente | Approccio |
|---|---|
| BaseButton, BaseCard, SectionLabel, KpiTile, SidebarSection | Scritto a mano con Tailwind — nessuna dipendenza da PrimeVue |
| Tooltip, Avatar, InputText, Select, Tag, ProgressBar | PrimeVue unstyled + PT Tailwind |
| DataTable, Dialog, DatePicker, MultiSelect | PrimeVue unstyled + PT Tailwind — da introdurre nella fase dati reali |

### PT inline vs condiviso

- **PT inline nel file** — per uso in un solo punto della codebase
- **`src/plugins/primevue-pt.js`** — estrarre il PT quando lo stesso componente PrimeVue
  viene usato in ≥ 2 view, per evitare duplicazione
