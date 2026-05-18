# Linee Guida Responsive — Gestionale Esseduesoft

## Obiettivo

Interfaccia Mobile-First che mantiene la potenza informativa del gestionale su tutti i
dispositivi. Priorità in ordine decrescente: smartphone (375px) → tablet (768px) → desktop (1280px+).

---

## Breakpoint di riferimento

| Token Tailwind | Larghezza | Uso tipico |
|---|---|---|
| *(default)* | 0px+ | Smartphone portrait |
| `sm:` | 640px+ | Smartphone landscape, tablet piccolo |
| `md:` | 768px+ | Tablet portrait |
| `lg:` | 1024px+ | Tablet landscape, laptop small |
| `xl:` | 1280px+ | Desktop — layout a due colonne attivo |
| `2xl:` | 1536px+ | Desktop wide — solo per padding extra |

---

## Layout principale

### Sidebar + content (DashboardView)

- **Mobile (< xl):** Sidebar off-canvas, triggerata da burger nell'header.
  Stato gestito dal composable `src/composables/useSidebar.js` (module-level reactive).
- **Desktop (≥ xl):** Sidebar statica nel grid `xl:grid-cols-[248px_minmax(0,1fr)]`.

### Colonne asimmetriche (AdminOnly, TenantAdmin)

- **Mobile/tablet (< xl):** Colonna singola — pannello secondario va sotto.
- **Desktop (≥ xl):** `xl:grid-cols-[1.3fr_0.7fr]` o `xl:grid-cols-[1.15fr_0.85fr]`.

---

## Navigazione e Header

### Burger menu

- Visibile solo su `< xl` (`xl:hidden` nel componente AppShell).
- Tap target: `h-11 w-11` (44×44px) — minimo raccomandato.
- Chiama `toggleDrawer()` da `useSidebar`.

### Drawer sidebar (mobile)

- `fixed inset-y-0 left-0 z-40` — off-canvas sinistro.
- Transizione: `transition-transform duration-300` con `translate-x-0` / `-translate-x-full`.
- Overlay scrim: `fixed inset-0 z-30 bg-steel-900/60` — click chiude il drawer (`chiudiDrawer()`).
- Bottone chiusura X dentro la sidebar, visibile solo su mobile (`xl:hidden`).
- CSS transition: classi `.fade-enter-active / .fade-leave-active / .fade-enter-from / .fade-leave-to` in `style.css`.

### Nav links

- `hidden xl:flex` — nascosti su mobile, visibili solo su desktop nell'header.
- Su mobile la navigazione avviene dalla sidebar drawer.

---

## Componenti Base

### BaseCard (`.card-pannello` / `.card-pannello-evidenza`)

- Padding: `p-4 sm:p-6` — ridotto su mobile, standard da sm+.
- Definito in `src/style.css` — non hardcodare padding nelle view.

### KpiTile

- Padding: `p-3 sm:p-4`.
- Font valore: `text-2xl sm:text-3xl` — più compatto su mobile.
- Grid: `grid-cols-1 md:grid-cols-2 xl:grid-cols-4`.

### BaseButton

- Altezza: `h-11` (44px) — soddisfa già il tap target minimo 44×44px.
- Non modificare.

---

## Griglia KPI

```html
<div class="grid gap-3 sm:gap-4 md:grid-cols-2 xl:grid-cols-4">
  <KpiTile ... />
</div>
```

| Viewport | Colonne |
|---|---|
| < md (mobile) | 1 |
| md – xl | 2 |
| ≥ xl | 4 |

---

## Tabelle dati — Column Hiding

Strategia: `hidden {breakpoint}:table-cell` su `<th>` e `<td>` corrispondenti.
Applicare in coppia: ogni colonna nascosta deve nascondere sia l'header che le celle dati.

### Mappa breakpoint consigliata

| Importanza | Visibilità |
|---|---|
| Essenziale (ID, nome, stato, importo) | Sempre visibile |
| Secondaria (tipo, ruolo) | Da `sm:` |
| Dettaglio (data, cliente, tenant) | Da `md:` |
| Descrittiva (causale, dettaglio) | Da `lg:` |

### Testo lungo

Celle con testo lungo (nomi aziende, descrizioni):
```html
<td class="max-w-[160px] truncate ...">{{ valore }}</td>
```

---

## Form e input

- Tutti gli input devono usare `w-full` su mobile.
- La classe `.campo-input` in `style.css` applica già `w-full`.
- Input di ricerca/filtro che su desktop hanno `min-w-[...]`: aggiungere `w-full sm:w-auto sm:min-w-[...]`.

### Bottoni azione form (futuri)

Su mobile, i bottoni "Salva / Annulla" di form lunghe devono essere sticky in fondo:
```html
<div class="sticky bottom-0 bg-white/95 px-4 py-3 backdrop-blur sm:static sm:bg-transparent sm:p-0">
  <BaseButton ...>Salva</BaseButton>
</div>
```

---

## PrimeVue — componenti ad alta complessità

PrimeVue v4 è installato con `unstyled: true`. Si usa solo per componenti con logica
complessa non replicabile facilmente (NON per semplici input o toggle).

| Componente | Quando usarlo |
|---|---|
| **DataTable** | Tabelle con sorting, filtering, pagination da API reali |
| **Dialog** | Form di dettaglio, conferme distruttive, modal complessi |
| **DatePicker** | Filtri per data/range su documenti |
| **MultiSelect** | Assegnazione ruoli e permessi multipli |
| **Password** (login) | NON usare — toggle con `ref` locale è sufficiente |
| **InputText** | NON usare — l'input nativo con `.campo-input` è sufficiente |

Consultare `planning/style/00-gestionale-visual-style.md` § Integrazione PrimeVue per il
pattern PT corretto con Tailwind v4.

---

## Regole evolutive

1. Ogni nuova view inizia mobile-first: definire il layout mobile prima di aggiungere breakpoint.
2. Nessun padding o font size hardcodato nelle view — usare i componenti Base e le utility Tailwind.
3. Il drawer sidebar è gestito da `useSidebar` — non creare nuovi sistemi di stato per l'UI navigation.
4. I tap target interattivi devono essere ≥ 44×44px su touch.
5. Le tabelle non devono usare `overflow-x-auto` come unica strategia — applicare sempre column hiding.
6. I form su mobile devono avere input `w-full` e bottoni sticky se la form è lunga.
