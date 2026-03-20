# Story 2.4: UI Redesign — Landing Page and Research Form

Status: review

## Story

As a visitor,
I want to experience a polished, professional landing page with a clear CTA that leads to a focused research submission screen,
so that I immediately understand the product's value and can submit my hypothesis without friction.

## Context

This story implements the visual redesign based on the Google Stitch-generated designs located in `docs/stitch/stitch/`. Two screens are redesigned:

1. **Landing page** (`/`) — new scrollable marketing page replacing the current combined landing+form page
2. **Research form** (`/research`) — new focused submission screen extracted from the current `page.tsx`

The Stitch design system ("Zinc Monolith / Silent Authority") introduces a new color palette and dual-font system. Reference files:
- `docs/stitch/stitch/swarmsense_landing_page/code.html`
- `docs/stitch/stitch/swarmsense_research_submission/code.html`
- `docs/stitch/stitch/zinc_monolith/DESIGN.md`

## Acceptance Criteria

### Design System

1. Given the Stitch design is adopted, when the app renders, then `frontend/lib/tokens.ts` contains the new Stitch color tokens (`surfaceContainer`, `surfaceContainerLow`, `surfaceContainerHigh`, `surfaceContainerHighest`, `onSurface`, `onPrimary`, `outlineVariant`, `errorDim`, `tertiaryContainer`) as hardcoded hex constants alongside existing tokens.
2. Given Tailwind v4 PostCSS is used (no `tailwind.config.js`), when new color tokens are needed as Tailwind utilities, then all new Stitch semantic colors are defined as CSS custom properties in `frontend/app/globals.css` using `@layer base` — never via a config file.
3. Given Inter and Space Grotesk are used in the Stitch design, when the app loads, then both fonts are loaded via `next/font/google` in `frontend/app/layout.tsx` and applied via CSS variables (`--font-headline`, `--font-label`); no `<link>` tags or CDN font loading.
4. Given Material Symbols icons appear in the Stitch HTML, when implemented in React, then all Material Symbols icons are replaced with `lucide-react` equivalents (`ArrowRight` for `arrow_forward`, `Send` for `send`, `ShieldCheck` for `verified_user`, `Info` for `info`, `Mail` for `mail`, `Zap` for `hub`, `FilePlus` for `post_add`).

### Landing Page (`/`)

5. Given a visitor navigates to `/`, when the page renders, then the current `app/page.tsx` content (combined landing+form) is replaced by a new scrollable landing page with the following sections in order: Navigation, Hero, Example Result Preview, How It Works, Trust Stats Bar, Closing CTA, Footer.
6. Given the navigation bar renders, when viewed on any screen size, then it contains only the SwarmSense logo (left) and a single "Ingyen kipróbálom" CTA button (right, amber) — no other nav links.
7. Given the navigation bar renders, when the user scrolls, then the nav is `position: sticky top-0` with a semi-transparent backdrop blur background.
8. Given the Hero section renders, when viewed, then it contains: a headline ("Tudd meg, mit gondol a piacod — 90 másodperc alatt." with "90 másodperc" in amber), a subheadline paragraph, and a primary CTA button ("Ingyen kipróbálom") — the secondary "Hogyan működik?" button from the Stitch HTML is omitted.
9. Given the "Ingyen kipróbálom" CTA button is clicked (nav or hero or closing CTA), when the click event fires, then the user navigates to `/research`.
10. Given the Example Result Preview section renders, when viewed, then it displays: an eyebrow label, a section heading, and a result card containing the research topic, target audience, consensus alert badge (amber, ⚠), sentiment split bar, and exactly 3 `PersonaCard` components (reject/conditional/support) reusing the existing `PersonaCard` component with `variant="compact"`.
11. Given the How It Works section renders, when viewed, then it shows 3 steps with lucide-react icons, headings, and descriptions as defined in `messages.ts`.
12. Given the Trust Stats Bar renders, when viewed, then it displays 4 statistics: cost per run, average wait time, no registration required, persona count — all text sourced from `messages.ts`.
13. Given the Closing CTA section renders, when viewed, then it contains a heading, the primary CTA button ("Ingyen kipróbálom" → navigates to `/research`), and a helper note ("Egy ingyenes futtatás. Nincs hitelkártya.").
14. Given the Footer renders, when viewed, then it contains the SwarmSense logo/name and a Privacy Policy link only (no Terms, Security, Contact links — those are out of MVP scope).
15. Given the landing page is a marketing page with no client interactivity, when rendered, then it is implemented as a React Server Component (no `"use client"` directive on the page itself).
16. Given the amber background glow decorative element appears in the Stitch hero, when implemented, then it is included as a purely decorative `aria-hidden="true"` div.

### Research Form (`/research`)

17. Given a visitor navigates to `/research`, when the page renders, then a new focused submission screen is shown with: a minimal sticky header (SwarmSense logo centered), a centered single-column layout (max-w-[600px]), and the "Mi a hipotézised?" heading with subtext.
18. Given the research form renders (State 1), when viewed, then it contains two textareas — "Mit vizsgálsz?" and "Kinek szól?" — with the bottom-border focus style from the Stitch design (no full border, amber bottom border on focus-within), the existing `RotatingPlaceholder` component for both fields, and a full-width amber "Elemzés indítása →" CTA button with `ArrowRight` lucide icon.
19. Given both form fields are empty, when the form renders, then the submit button is disabled (`aria-disabled="true"`) — same logic as the current `page.tsx`.
20. Given a visitor blurs a field without filling it, when the blur event fires, then an inline error message appears below the field (text sourced from `messages.ts`) — same validation logic as current `page.tsx`. No toast notifications.
21. Given a visitor fills both fields and submits, when the submit succeeds, then the two filled textareas remain visible above (read-only appearance) and the email capture section (State 2) appears below with a smooth reveal — no page reload.
22. Given the email capture section (State 2) renders, when viewed, then it shows: "Hova küldjük az eredményt?" heading, subtext, an email input field with the same bottom-border focus style, a full-width amber "Eredmény küldése →" CTA button with `Send` lucide icon, and a privacy note with `ShieldCheck` icon — all text sourced from `messages.ts`.
23. Given the research form has interactive state, when rendered, then `app/research/page.tsx` uses `"use client"` directive.
24. Given the Stitch design uses subtle fixed background gradient blobs, when implemented, then they are included as `position: fixed`, `pointer-events: none`, `aria-hidden="true"`, `-z-10` decorative elements.

### Token & Style Consistency

25. Given the project rule that no hardcoded hex colors appear in components, when the new pages use Stitch colors, then all color values are imported from `frontend/lib/tokens.ts` via inline `style={{}}` props or referenced as CSS custom properties — never hardcoded hex strings in JSX.
26. Given the project rule that all Hungarian strings live in `messages.ts`, when new landing page and form copy is added, then all user-visible Hungarian text (headings, subheadings, labels, CTAs, helper text, step descriptions, stat labels, footer text) is stored in `frontend/lib/messages.ts` under appropriate keys (`landing.nav`, `landing.hero`, `landing.preview`, `landing.howItWorks`, `landing.stats`, `landing.closingCta`, `landing.footer`, `research.form`).

### Accessibility & Responsive

27. Given the landing page has decorative glow elements, when rendered, then all decorative-only elements have `aria-hidden="true"`.
28. Given the landing page is desktop-primary, when viewed on mobile (320px–767px), then the How It Works steps stack vertically, Trust Stats Bar wraps, and all CTAs are full-width.
29. Given the research form is centered on desktop, when viewed on mobile, then the layout is full-width with `px-6` padding and the form fields stack vertically.

### Tests

30. Given new pages and layout changes are introduced, when tests run, then existing tests in `frontend/app/page.test.tsx` are updated to reflect the new landing page structure (the form is no longer on `/`).
31. Given the research form at `/research` has interactive behavior, when tests run, then a new `frontend/app/research/page.test.tsx` covers: both fields empty → submit disabled; blur empty field → error appears; fill both fields + submit → email capture section appears; email capture renders correct microcopy.

## Tasks / Subtasks

- [x] Extend design system tokens and fonts (AC: 1, 2, 3, 4)
  - [x] Add new Stitch color tokens to `frontend/lib/tokens.ts` (surfaceContainer, surfaceContainerLow, surfaceContainerHigh, surfaceContainerHighest, onSurface, onPrimary, outlineVariant, errorDim, tertiaryContainer)
  - [x] Add new CSS custom properties to `frontend/app/globals.css` `@layer base` block for Tailwind v4 compatibility
  - [x] Load Inter and Space Grotesk fonts via `next/font/google` in `frontend/app/layout.tsx`; expose as `--font-headline` and `--font-label` CSS variables; apply to `<html>` element
  - [x] Verify `lucide-react` is available (already a shadcn/ui dependency); no new packages needed

- [x] Build new landing page at `app/page.tsx` (AC: 5–16, 25, 26, 27, 28)
  - [x] Replace current `app/page.tsx` content with new Server Component landing page
  - [x] Implement sticky nav: logo (left) + "Ingyen kipróbálom" button (right) only — `<Link href="/research">`
  - [x] Implement Hero section: headline with amber "90 másodperc" span, subheadline, primary CTA `<Link href="/research">`
  - [x] Implement Example Result Preview section: reuse `PersonaCard` component with `variant="compact"` for 3 mock cards; sentiment bar; consensus badge
  - [x] Implement How It Works section: 3 steps with lucide-react icons
  - [x] Implement Trust Stats Bar: 4 statistics
  - [x] Implement Closing CTA section: heading + CTA `<Link href="/research">` + helper note
  - [x] Implement Footer: logo + Privacy Policy link only
  - [x] Add decorative amber glow blobs as `aria-hidden="true"`
  - [x] Add all new Hungarian strings to `frontend/lib/messages.ts`
  - [x] Ensure all colors reference `tokens.ts` — no hardcoded hex in JSX

- [x] Build new research form at `app/research/page.tsx` (AC: 17–24, 25, 26, 29)
  - [x] Create `frontend/app/research/` directory and `page.tsx` with `"use client"`
  - [x] Migrate form state, validation logic, and email capture logic from current `app/page.tsx`
  - [x] Apply Stitch visual design: bottom-border focus style, centered layout, `max-w-[600px]`
  - [x] Reuse `RotatingPlaceholder` for both textareas
  - [x] Apply new font variables (`font-headline`, `font-label`) to appropriate elements
  - [x] Add lucide-react icons: `ArrowRight` on submit CTA, `Send` on email CTA, `ShieldCheck` on privacy note, `Info` on PII warning
  - [x] Add fixed background gradient blobs as `aria-hidden="true"` decorative elements
  - [x] Add new research form strings to `frontend/lib/messages.ts` under `research` key

- [x] Update and add tests (AC: 30, 31)
  - [x] Update `frontend/app/page.test.tsx`: remove form-related tests (form is now at `/research`); add basic landing page render tests (nav CTA present, hero headline present, example result preview present)
  - [x] Create `frontend/app/research/page.test.tsx`: submit disabled when fields empty; blur empty field shows error; fill both + submit reveals email capture; email capture microcopy correct

## Dev Notes

- **Route change:** The research form moves from `/` to `/research`. The current `app/page.tsx` becomes a pure marketing landing page (Server Component). The form logic migrates to `app/research/page.tsx` (Client Component).
- **Font loading:** Use `next/font/google` — never `<link>` tags. Example: `const inter = Inter({ subsets: ['latin'], variable: '--font-headline' })`. Apply via `className` on `<html>` in `layout.tsx`.
- **Tailwind v4 custom colors:** Define via CSS custom properties in `globals.css`, NOT via config file. Pattern: `--color-surface-container: #19191d;` then use as `bg-[var(--color-surface-container)]` in JSX or define as `@theme` inline.
- **No Material Symbols:** Do not add the Google Material Symbols font. All icons use `lucide-react` only.
- **PersonaCard reuse:** The existing `PersonaCard` component is used as-is for the Example Result Preview on the landing page. The mock data for the 3 preview cards stays in `messages.ts`.
- **RotatingPlaceholder reuse:** The existing component from Story 2.3 is used as-is in the research form. No modifications to the component itself.
- **Amber glow blobs:** The decorative `bg-primary/5 rounded-full blur-[120px]` elements from the Stitch design are implemented as `aria-hidden="true"` divs. On the research form, use `position: fixed` (as in Stitch). On the landing page hero, use `position: absolute`.
- **`next/navigation` for routing:** Use `<Link href="/research">` from `next/link` for CTA navigation — never `<a href>` tags for internal routes.
- **Nav secondary button omitted:** The "Hogyan működik?" secondary button from the Stitch hero is intentionally excluded per product decision.

### Project Structure Notes

- New files: `frontend/app/research/page.tsx`, `frontend/app/research/page.test.tsx`
- Modified files: `frontend/app/page.tsx`, `frontend/app/page.test.tsx`, `frontend/app/layout.tsx`, `frontend/lib/tokens.ts`, `frontend/lib/messages.ts`, `frontend/app/globals.css`
- No new npm packages required (lucide-react already available, Inter and Space Grotesk via next/font/google)

### References

- Stitch landing page HTML: `docs/stitch/stitch/swarmsense_landing_page/code.html`
- Stitch research form HTML: `docs/stitch/stitch/swarmsense_research_submission/code.html`
- Stitch design system: `docs/stitch/stitch/zinc_monolith/DESIGN.md`
- UX design specification: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Architecture constraints and Hungarian text rule: `_bmad-output/planning-artifacts/architecture.md`
- Project-wide rules (tokens, messages, no shadcn edits): `_bmad-output/project-context.md`
- Existing PersonaCard component: `frontend/components/persona-card.tsx`
- Existing RotatingPlaceholder component: `frontend/components/rotating-placeholder.tsx`

## Dev Agent Record

### Implementation Plan

- Extend tokens, CSS variables, and font loading to match Stitch requirements.
- Rebuild landing page as a Server Component with the new section structure.
- Create the research page as a Client Component with migrated form logic and new visuals.
- Update messages and tests to reflect the new routes and copy.

### Debug Log

- 2026-03-20: `pnpm test` (frontend) — passed; React Testing Library emitted act warnings for Link.

### Completion Notes

- Added Stitch color tokens and CSS custom properties; updated font loading to Inter + Space Grotesk.
- Implemented the redesigned landing page sections and new `/research` form with updated interaction states.
- Updated message keys and added new tests for landing and research pages.

## File List

- frontend/lib/tokens.ts
- frontend/app/globals.css
- frontend/app/layout.tsx
- frontend/lib/messages.ts
- frontend/app/page.tsx
- frontend/app/research/page.tsx
- frontend/app/page.test.tsx
- frontend/app/research/page.test.tsx
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-03-20: Added Stitch tokens, redesigned landing and research pages, and updated tests.
