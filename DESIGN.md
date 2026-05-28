---
name: Gestionale
description: Italian B2B gestionale — modern web ERP replacing a legacy desktop tool. Calm, precise, document-grade.
colors:
  brand-50: "#fff1f1"
  brand-100: "#ffd9d9"
  brand-300: "#ff8e8e"
  brand-500: "#c62828"
  brand-700: "#8f1d1d"
  brand-900: "#5e1313"
  steel-50: "#f6f7f8"
  steel-100: "#eceef1"
  steel-200: "#d7dce2"
  steel-400: "#8b95a1"
  steel-700: "#39424d"
  steel-900: "#1e252c"
  sidebar-ink: "#232a31"
typography:
  display:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "1.875rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "normal"
  title:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "normal"
  body:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  label:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.28em"
rounded:
  sm: "0.5rem"
  md: "0.75rem"
  lg: "1rem"
  xl: "1.5rem"
  pill: "9999px"
spacing:
  xs: "0.5rem"
  sm: "0.75rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "2rem"
components:
  button-primary:
    backgroundColor: "{colors.brand-500}"
    textColor: "#ffffff"
    rounded: "{rounded.md}"
    padding: "0.75rem 1rem"
  button-primary-hover:
    backgroundColor: "{colors.brand-700}"
  button-secondary:
    backgroundColor: "#ffffff"
    textColor: "{colors.steel-700}"
    rounded: "{rounded.md}"
    padding: "0.75rem 1rem"
  button-secondary-hover:
    backgroundColor: "{colors.steel-100}"
  input-field:
    backgroundColor: "#ffffff"
    textColor: "{colors.steel-900}"
    rounded: "{rounded.md}"
    padding: "0.75rem 1rem"
  card-panel:
    backgroundColor: "#ffffff"
    rounded: "{rounded.xl}"
    padding: "1.5rem"
---

# Design System: Gestionale

## 1. Overview

**Creative North Star: "The Accounting Binder"**

Gestionale is a daytime work surface for back-office staff. The aesthetic is that of a well-organized binder: white paper, steel-grey rules, a single red mark for the action that matters. Nothing shouts. Density is welcome where it helps the work, but the underlying rhythm is generous enough that a long session does not fatigue.

The system explicitly rejects two lineages. It is not a 1990s Italian ERP (TeamSystem, Zucchetti, classic SAP): no grey-on-grey, no dense window-chrome toolbars, no ambiguous icons. It is also not a cookie-cutter B2B SaaS template: no purple/indigo "trustworthy" accents, no identical icon-and-heading card grids, no hero-metric tiles, no friendly illustrations. The product replaces a desktop gestionale; visual familiarity to a legacy user matters, but the craft must be unambiguously modern.

**Key Characteristics:**
- One accent (brand red `#c62828`), used like a pen mark, ≤10% of any screen.
- Steel-tinted neutrals (`#1e252c` through `#f6f7f8`) carry everything else.
- Dark sidebar (`#232a31`) against light content for stable spatial anchoring.
- Generous corner radius (`1rem`–`1.5rem`) softens density.
- Motion is short, ease-out, opacity-led. No bounce, no decorative animation.

## 2. Colors

The palette is two-toned: a single saturated brand red and a steel-neutral ramp. Color carries meaning, never decoration.

### Primary
- **Brand Red 500** (`#c62828`): primary action, active nav item, brand mark. Used as a foreground or solid fill, never as a gradient or decorative wash.
- **Brand Red 700** (`#8f1d1d`): primary-button hover and active-tab text. The deeper register of the same voice.

### Tertiary (supporting brand tints)
- **Brand 50** (`#fff1f1`) / **Brand 100** (`#ffd9d9`) / **Brand 300** (`#ff8e8e`): selected-row hover wash, status-tag fills, focus-ring tint. Tints, not fills; never on a whole panel.
- **Brand 900** (`#5e1313`): reserved for high-emphasis emphasis where 700 reads too light.

### Neutral
- **Steel 900** (`#1e252c`): body text on light surfaces. The default ink.
- **Steel 700** (`#39424d`): secondary text, table cells, secondary-button label.
- **Steel 400** (`#8b95a1`): placeholders, helper text, table headers, disabled hints. Never body text.
- **Steel 200** (`#d7dce2`): borders, dividers, input strokes.
- **Steel 100** (`#eceef1`): table header backgrounds, hover fills on neutral buttons.
- **Steel 50** (`#f6f7f8`): page background, neutral input backgrounds.
- **Sidebar Ink** (`#232a31`): the dark sidebar; a desaturated cousin of steel-900 with a touch more warmth so it does not feel black against white.

### Named Rules
**The Pen Mark Rule.** Brand red occupies ≤10% of any rendered screen. If a mockup shows red filling more than that, it is no longer the accent and the design is wrong.

**The No Pure Black or White Rule.** `#000000` and `#ffffff` are not used as text colors. Body ink is steel-900; the closest thing to white is the card surface, which still sits on a tinted page background.

**The One Accent Rule.** Status, success, warning, and info do not introduce new hues yet. Brand-50/100 carries status-tag fills today. When semantic colors are added, they must be added with restraint (one each, low chroma).

## 3. Typography

**Display Font:** system-ui (Segoe UI on Windows, San Francisco on macOS)
**Body Font:** system-ui
**Label/Mono Font:** none distinct today; uppercase wide-tracked labels carry the role.

**Character:** Neutral, screen-native, fast to render and instantly familiar to users on Windows back-office machines. The hierarchy is carried by weight contrast and a strong uppercase-tracked label style, not by exotic fonts.

### Hierarchy
- **Display** (600, `1.875rem`/`2rem` responsive, line-height 1.2): page H1 — "Vista elenco documenti", "Anagrafiche", "Tenant Admin".
- **Title** (600, `1rem`–`1.125rem`, line-height 1.4): card titles, section headings inside a card.
- **Body** (400, `0.875rem`, line-height 1.5): default copy, table cells, paragraphs.
- **Helper** (400, `0.75rem`–`0.8125rem`, line-height 1.4): metadata, captions, error/help text.
- **Label** (600, `0.6875rem`–`0.75rem`, letter-spacing `0.16em`–`0.28em`, UPPERCASE): section labels, status tags, table headers, sidebar group titles. The signature texture of the system.

### Named Rules
**The Wide-Tracked Label Rule.** Section labels and tags are uppercase, letter-spaced between `0.16em` and `0.28em`, weight 600, in steel-400 (neutral) or brand-700 (emphasis). This is the system's typographic signature; it carries hierarchy without enlarging the type scale.

**The System-Font Rule.** Stay on system-ui. No webfont network cost, no FOUT, no aesthetic distraction. Italian back-office machines are most often Windows; Segoe UI is exactly right.

## 4. Elevation

The system is mostly flat. Depth is conveyed by tonal layering (`steel-50` page → `#ffffff` cards → `steel-100` table headers) and by a single soft "panel" shadow on raised cards. The dark sidebar provides a structural counter-surface; it does not need a shadow to separate from content.

### Shadow Vocabulary
- **Panel** (`box-shadow: 0 26px 56px -30px rgba(30, 37, 44, 0.25)`): the only ambient shadow in the system. Soft, far-offset, very low opacity. Used on `card-pannello`.
- **Active nav glow** (`box-shadow: 0 10px 24px -16px rgba(198, 40, 40, 0.9)`): tiny red wash under the currently active sidebar item. Used only on the active state, never on hover.

### Named Rules
**The Flat-at-Rest Rule.** Buttons, inputs, tags, and table rows are flat at rest. State (hover, focus, active) introduces a tonal shift or a 1px border change, never a new shadow. The Panel shadow is reserved for the card surface itself.

## 5. Components

### Buttons
- **Shape:** `0.75rem` radius (`rounded-xl` in Tailwind). Comfortable but unmistakably modern.
- **Primary** (`.pulsante-primario`): `bg-brand-500`, white text, `px-4 py-3`, font-semibold, text-sm. Hover → `bg-brand-700`.
- **Secondary** (`.pulsante-secondario`): white background, `border steel-200`, `text-steel-700`, same padding. Hover → `bg-steel-100`.
- **Focus:** brand-500 ring on inputs is the canonical focus treatment; buttons inherit a focus-visible ring from the browser today. Make this explicit (see Don'ts).

### Cards / Containers
- **Corner Style:** `1.5rem` radius (`rounded-[1.5rem]`). Generous, softens density.
- **Background:** `#ffffff` on `steel-50` page.
- **Border:** `1px solid steel-200`. Always present, even with the Panel shadow.
- **Shadow:** the Panel shadow (see Elevation).
- **Internal Padding:** `1rem` mobile, `1.5rem` from `sm:` breakpoint.
- **Highlight variant** (`card-pannello-evidenza`): adds an inset top-stripe in brand-500 via `box-shadow: inset 0 4px 0 0 brand-500`. Used sparingly; see the Don'ts about side stripes.

### Inputs / Fields
- **Style** (`.campo-input`): `border steel-200`, `bg-white`, `rounded-xl`, `px-4 py-3`, `text-sm steel-900`. Persistent border at all times.
- **Focus:** `border-brand-500` plus a 2px ring of `brand-100`. The clearest single state signal in the system.
- **Placeholder:** `steel-400`. Never used as a label substitute.

### Tags / Chips
- **Style:** `rounded-full`, `border brand-100`, `bg brand-50`, `text-[11px]` uppercase, `tracking-[0.16em]`, `text-brand-700`. The shared style for status, role badges, and filter chips today.
- **Note:** the tag style does not yet vary by semantic state (open/draft/sent are all the same tint). This is a known gap; see Do's.

### Navigation
- **Header:** sticky, white-with-backdrop-blur, `border-b steel-200`, `py-4`. Brand square (`bg-brand-500`, "ES" mark), product name (uppercase wide-tracked brand-700) over short title (steel-900).
- **Sidebar:** dark surface (`#232a31`), 248px wide on xl+, slide-in drawer below xl. Each item is a 12-unit tall pill with a 32px square icon container. Active item: `bg-brand-500`, white text, the small red glow shadow.
- **"In arrivo" (placeholder modules):** rendered at reduced opacity, `cursor-not-allowed`, with a "Presto" pill. Clear visual demotion.

### Tables
- **Header:** `bg-steel-100`, uppercase steel-400 labels, wide tracking, `text-[11px]`.
- **Rows:** `divide-y steel-100`. Hover wash: `bg-brand-50/55`. No alternating row stripes.
- **Empty state:** italic steel-400 message inside the table, never a separate empty-state component.

### Task progress (signature pattern)
The async-report panel uses a brand-gradient progress bar (`linear-gradient(90deg, #8c1d18 0%, #d2412e 100%)`) inside a `steel-100` track. This is the one place a brand gradient appears in the system, justified by the "energy moving" semantic. Do not borrow this gradient for decorative use elsewhere.

## 6. Do's and Don'ts

### Do
- **Do** keep brand red at or below 10% of any screen. If a new design pushes past that, demote one usage to steel.
- **Do** tint every neutral toward the steel hue. Pure `#000` and `#fff` are banned.
- **Do** use the wide-tracked uppercase label style for section headings, table headers, and tags. It is the system's signature.
- **Do** pair every input with a persistent label above the field. Placeholders are placeholders, not labels.
- **Do** add a visible `:focus-visible` ring (brand-500 outline or brand-100 ring) on every interactive element. The keyboard path must be obvious.
- **Do** reach for a tonal shift (`bg-steel-50` → `bg-steel-100`, or `bg-white` inside `bg-steel-50`) before reaching for a new shadow.
- **Do** keep motion to opacity and `transform`, ease-out, under 250ms. The fade transition in `style.css` is the canonical example.
- **Do** vary spacing: `gap-3` for tight clusters, `gap-5`/`gap-6` for section rhythm, `mt-6`/`mt-8` between sections within a card. Same padding everywhere reads as monotony.

### Don't
- **Don't** introduce purple, indigo, or teal "trust" accents. This product has one accent and it is red.
- **Don't** use gradient text or `background-clip: text` anywhere. The brand-gradient progress bar is the only sanctioned gradient and it is a 100%-real surface, not text.
- **Don't** apply glassmorphism as a default style. The header's `backdrop-blur` over `bg-white/92` is the only sanctioned use; do not extend it to cards, modals, or panels.
- **Don't** add side-stripe `border-left`/`border-right` accents on cards, list items, or alerts. The existing `card-pannello-evidenza` top stripe is the limit; do not add left/right siblings.
- **Don't** ship the cookie-cutter "icon + heading + 2 lines" card grid. The "Moduli in arrivo" list in the sidebar gets away with it because it is explicitly a placeholder; do not extend that pattern to real content.
- **Don't** ship a hero-metric tile (big number + small label + gradient). KPI tiles must stay restrained — number in `steel-900`, label uppercase steel-400, no decorative accent on the tile itself.
- **Don't** reach for a modal as the first answer. Inline edit, drawer, or progressive disclosure first.
- **Don't** use `steel-400` for body copy on a white background. It is helper text only.
- **Don't** introduce a webfont. The system-font stack is part of the visual identity and the performance budget.
- **Don't** echo legacy ERP density: 11-row toolbars, 4-pixel-padding rows, ambiguous mini icons, grey-on-grey checkboxes. If a screen starts to look like TeamSystem, stop and rework the spacing rhythm before continuing.
