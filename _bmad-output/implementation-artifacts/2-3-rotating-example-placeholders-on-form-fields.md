# Story 2.3: Rotating Example Placeholders on Form Fields

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a visitor,
I want to see example research topics and target audience descriptions cycling through the form fields,
so that I understand what good input looks like and can overcome the "what do I write?" cognitive barrier.

## Acceptance Criteria

1. Given a visitor arrives at the landing page with the form visible, when neither form field has been focused, then the RotatingPlaceholder component cycles through at least 3 example research topics in the topic field every 4 seconds.
2. Given a visitor arrives at the landing page with the form visible, when neither form field has been focused, then the RotatingPlaceholder component cycles through at least 3 example target audience descriptions in the audience field every 4 seconds.
3. Given the user prefers reduced motion, when the page is loaded, then placeholder cycling stops for that field (`prefers-reduced-motion`).
4. Given a visitor clicks into a form field, when the field receives focus, then the placeholder cycling stops immediately for that field.
5. Given a visitor has focused a field once, when they clear the field and blur, then the cycling does not restart for that field.
6. Given the page is read by a screen reader, when the RotatingPlaceholder is active, then the cycling animation does not affect screen reader announcements (placeholder is supplemental; the label is the accessible name).

## Tasks / Subtasks

- [x] Implement a RotatingPlaceholder component for textareas (AC: 1, 2, 3, 4, 5, 6)
  - [x] Create `frontend/components/rotating-placeholder.tsx` with per-field cycling state (topic vs audience) and a 4s interval
  - [x] Stop cycling immediately on focus; permanently disable cycling after first focus for that field
  - [x] Respect `prefers-reduced-motion` via `matchMedia` and short-circuit cycling when active
- [x] Wire RotatingPlaceholder into the landing page form (AC: 1, 2, 4, 5)
  - [x] Use RotatingPlaceholder for both topic and audience textareas in `frontend/app/page.tsx`
  - [x] Keep existing validation and email capture behavior unchanged (Story 2.2)
  - [x] Store example strings in `frontend/lib/messages.ts` and import them (no hard-coded Hungarian strings)
- [x] Add/update tests for rotating placeholders (AC: 1, 2, 3, 4, 5, 6)
  - [x] Component test for 4s cycling using fake timers
  - [x] Stop-on-focus and no-restart-on-blur behavior
  - [x] `prefers-reduced-motion` disables cycling

## Dev Notes

- Do not modify shadcn files under `frontend/components/ui/` (project rule). Place the custom component in `frontend/components/`.
- All Hungarian user-visible strings (including rotating examples) must live in `frontend/lib/messages.ts` (architecture + project-context rule). No inline strings in components.
- No new dependencies; use React state + `useEffect` timers.
- The rotating placeholder must be purely visual (placeholder only). Do not add `aria-live` or other announcements; labels remain the accessible name.
- Interval: 4 seconds per UX spec; stop immediately on focus; never resume after the first focus for that field.
- Preserve existing form validation behavior and submit gating from Story 2.2.

### Project Structure Notes

- Custom component location conflict: UX spec mentions custom components in `/components/ui/`, but project-context and architecture rules say custom components belong in `frontend/components/` and shadcn files must not be edited. Follow `frontend/components/`.
- Landing page form lives in `frontend/app/page.tsx`.
- Tests should be co-located (e.g., `frontend/components/rotating-placeholder.test.tsx`), per project-context rules.

### References

- Story 2.3 acceptance criteria: `_bmad-output/planning-artifacts/epics.md`
- UX rotating placeholder requirements + reduced motion: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Architecture rules for Hungarian strings and component placement: `_bmad-output/planning-artifacts/architecture.md`
- Project-wide constraints (no shadcn edits, test co-location): `_bmad-output/project-context.md`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.2-codex

### Debug Log References
- pnpm test
- pnpm lint
- pnpm build
- pnpm test
- pnpm lint

### Completion Notes List
- Implemented RotatingPlaceholder with 4s cycling, focus stop, and reduced-motion handling; wired it into landing page textareas and added example strings in messages.
- Added component-level tests for cycling, focus/blur behavior, and reduced-motion handling; updated test setup with matchMedia polyfill.
- Fixed build-time type check issue by removing legacy matchMedia listener fallback; verified build, tests, and lint.

### File List
- frontend/app/page.tsx
- frontend/components/rotating-placeholder.tsx
- frontend/components/rotating-placeholder.test.tsx
- frontend/lib/messages.ts
- frontend/test/setup.ts

### Change Log
- 2026-03-20: Added rotating placeholder component, wired landing page, and covered behavior with component tests.
- 2026-03-20: Fixed build-time type check issue in matchMedia handling and revalidated build/tests/lint.
- 2026-03-20: Applied code review patches (claude-sonnet-4-6): email capture made functional (controlled state, form wrapper, submit handler, validation); formatAriaLabel fallback changed from "" to "{key}" for missing tokens; legacy addListener cleanup added; intervalMs clamped to min 100ms; isComplete effect now also clears errors; matchMedia mock restored in afterEach; zero-tick focus test and aria-live absence test added; emailCta and errors.email strings added to messages.ts. All tests pass (21/21), lint clean, build successful.
