# Product

## Register

product

## Users

Office staff at Italian SMBs — accounting, back-office, and operations roles. They sit at a desk on a 1080p or larger monitor for long sessions, working with customers/suppliers, invoices, fiscal documents, and master data. Many are migrating from a long-used legacy desktop gestionale (VB6/VB.NET) and bring strong muscle memory: they expect dense forms, predictable layouts, keyboard flow, and the ability to scan a screen full of information without surprises. They are not designers and do not want to be impressed; they want to finish their work.

## Product Purpose

A modern web "gestionale" replacing a legacy desktop ERP, rebranded as Gestionale. Multi-tenant SaaS with role-based access (admin, tenant_admin, end users) covering authentication, anagrafiche (clienti/fornitori/agenti with P.IVA, CF, SDI, PEC, regime fiscale, multi-address), tenant settings, document sequences, real-time notifications, KPI dashboards, and (planned) document, fiscal, and reporting modules. Success means daily operators finish back-office work faster than on the legacy app without retraining friction, and tenant admins can configure the workspace without IT involvement.

## Brand Personality

Precise, calm, document-grade.

The interface should feel like a well-organized accounting binder: nothing shouts, every label is exact, every action lands where the user expects it. Voice is professional Italian, formal-but-direct (`Salva`, `Annulla`, `Crea anagrafica`), never chatty, never playful. Accent color is a single brand red (`#c62828`) used sparingly for primary action and identity, not decoration.

## Anti-references

- **Legacy Italian ERP UIs** (TeamSystem, Zucchetti, classic SAP screens): grey-on-grey, dense toolbars, 90s window-chrome density, no whitespace, ambiguous icons. The product replaces these tools, so it must not visually resemble them. Modern type, real spacing rhythm, and OKLCH neutrals separate us from that lineage.
- **Cookie-cutter SaaS templates**: identical icon-plus-heading card grids, hero-metric tiles (big number, small label, gradient), purple/indigo "trustworthy" accents, generic illustrations, marketing-style empty states. This is the AI-slop default for B2B dashboards and must be actively avoided.
- Implied anti-refs from the above: gradient text, glassmorphism, side-stripe accent borders, modals as first thought, illustrations of friendly characters, emoji in UI copy.

## Design Principles

1. **Document over dashboard.** Most screens are working surfaces (forms, tables, detail views), not status displays. Information density is welcome when the structure is clear; whitespace serves rhythm, not decoration.
2. **One brand red, used like a pen mark.** Red signals primary action, brand identity, and selected/active state. It is never decoration, never a gradient, never a background fill for whole panels. Steel neutrals carry everything else.
3. **Familiar to a legacy user, modern to a new one.** Field labels, button verbs, and table layouts match the mental model of a long-time gestionale user. Type, spacing, and motion are quietly modern so the app does not feel dated.
4. **No surprise, no flourish.** Motion is short and functional (fade, ease-out). No bounce, no decorative animation, no scroll-triggered theatre. A skeleton or spinner is enough.
5. **Forms and tables are first-class.** They get the same craft as a marketing site usually reserves for heroes: alignment, hierarchy, density modes, keyboard targets, empty/error/loading states. Get these right and the rest follows.

## Accessibility & Inclusion

No formal WCAG target; users are internal/B2B and there is no regulatory pressure today. Apply a best-effort floor:

- Keep text contrast comfortable on the steel-50 background (avoid steel-400 on white for body text).
- Every interactive element reachable by keyboard with a visible focus ring.
- Form inputs paired with persistent labels (no placeholder-as-label).
- Respect `prefers-reduced-motion` for the small set of transitions we do use.
- Italian-only UI today; copy should stay translation-friendly (avoid baked-in word order assumptions) so a future second locale is cheap.
