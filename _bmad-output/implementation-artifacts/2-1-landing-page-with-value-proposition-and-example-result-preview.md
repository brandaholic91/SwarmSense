# Story 2.1: Landing Page with Value Proposition & Example Result Preview

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a visitor,
I want to see SwarmSense's value proposition and an example result preview when I arrive at the landing page,
so that I can immediately understand what the product does and whether it is worth trying.

## Acceptance Criteria

1. Given a visitor arrives at `/`, when the page loads, then the page renders within 3 seconds for p95 visits (NFR1).
2. Given the landing page renders, when the hero section is visible, then a bold headline (44px, weight 800, letter-spacing -1px) states the value proposition in Hungarian.
3. Given the example preview section is visible, when a visitor scans it, then it shows: an oversized persona count stat, a blockquote-style top objection callout, and at least 3 PersonaCard components in `compact` variant displaying distinct stances (reject/support/conditional) with left-border color indicators.
4. Given the example preview is rendered, when content is reviewed, then the persona data is real-looking and specific (no placeholder text) and demonstrates persona diversity.
5. Given the page background is rendered, when style is applied, then the background is pure black (`#000`) in line with High Contrast Impact direction.
6. Given an automated axe-core scan is run, when the landing page is evaluated, then it reports zero critical accessibility violations.
7. Given the root layout is rendered, when `<html>` is inspected, then `lang="hu"` is set and all user-visible text is Hungarian (NFR21).

## Tasks / Subtasks

- [x] Build landing hero and example preview layout in `frontend/app/page.tsx` (AC: 2, 3, 5, 7)
  - [x] Add hero headline and supporting copy using `frontend/lib/messages.ts` keys (no hard-coded HU strings)
  - [x] Apply High Contrast Impact styling: `#000` background, 44px/800 headline, amber accent, tabular-nums for stats
  - [x] Set container sizing (`max-w-2xl`, `mx-auto`, `px-4 sm:px-6`) consistent with UX spec
- [x] Implement or extend `PersonaCard` for `compact` variant in `frontend/components/persona-card.tsx` (AC: 3, 4)
  - [x] Add 4px left-border stance indicator (rose/emerald/amber) and stance label text (not color-only)
  - [x] Add `aria-label` on card container
  - [x] Ensure compact variant truncates copy appropriately for preview
- [x] Add example preview content and data model in `frontend/app/page.tsx` (AC: 3, 4)
  - [x] Oversized persona count stat (e.g., "15 / 18 persona elutasítja") using tabular-nums
  - [x] Blockquote-style top objection callout
  - [x] Render 3 PersonaCard instances with distinct stances and roles
- [x] Accessibility and compliance checks (AC: 6, 7)
  - [x] Ensure all headings/sections are semantic and labels use proper hierarchy
  - [x] Confirm no English or placeholder strings appear on the landing page

## Dev Notes

- Scope boundaries: do NOT implement the research form fields, email capture, or rotating placeholders here (Story 2.2 and 2.3 handle those). This story only covers hero + example preview content on the landing page.
- Use design tokens from `frontend/lib/tokens.ts` for color values and import Hungarian text from `frontend/lib/messages.ts` (no hard-coded HU strings in components).
- Apply High Contrast Impact direction: pure black background, large bold headline, amber accent, oversized numeric stat, blockquote-style objection callout, and 3-column PersonaCard grid (`grid-cols-1 md:grid-cols-2 lg:grid-cols-3`).
- Follow architecture patterns: Next.js App Router, Tailwind, shadcn/ui; system font stack only (no web fonts); tabular-nums for persona counts; `aria` attributes per UX spec.

### Project Structure Notes

- Landing page content lives in `frontend/app/page.tsx`.
- PersonaCard component is `frontend/components/persona-card.tsx` and is shared by landing preview and result email.
- Token and copy single-source requirements: `frontend/lib/tokens.ts`, `frontend/lib/messages.ts`.

### References

- Epic 2 Story 2.1 acceptance criteria: `_bmad-output/planning-artifacts/epics.md`
- UX High Contrast Impact direction and landing requirements: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Architecture patterns, file locations, and Hungarian text rule: `_bmad-output/planning-artifacts/architecture.md`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.2-codex

### Implementation Plan

- Replace the default landing content with hero + preview layout using tokens/messages.
- Add PersonaCard component with compact variant and stance indicators.
- Wire example preview data from messages and ensure accessibility attributes.

### Debug Log References

- 2026-03-20: Added vitest + jest-axe setup, implemented landing layout and PersonaCard, ran `pnpm test` (Vite CJS deprecation warning).
- 2026-03-20: Fixed build type error for WebkitBoxOrient and added jest-axe types; `pnpm build` now passes.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created
- Landing hero + preview layout implemented with tokens/messages; PersonaCard compact variant added with stance indicators and aria-labels.
- Tests added for PersonaCard, landing page rendering, and axe critical violations; `pnpm test` passes.
- Build fixed by typing WebkitBoxOrient style and adding @types/jest-axe; `pnpm build` passes.

### File List

- _bmad-output/implementation-artifacts/2-1-landing-page-with-value-proposition-and-example-result-preview.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- frontend/app/globals.css
- frontend/app/page.tsx
- frontend/app/page.test.tsx
- frontend/components/persona-card.tsx
- frontend/components/persona-card.test.tsx
- frontend/lib/messages.ts
- frontend/lib/tokens.ts
- frontend/package.json
- frontend/pnpm-lock.yaml
- frontend/test/setup.ts
- frontend/tsconfig.json
- frontend/vitest.config.ts
