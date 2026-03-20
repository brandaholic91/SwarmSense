# Story 2.3: Rotating Example Placeholders on Form Fields

Status: ready-for-dev

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

- [ ] Implement a RotatingPlaceholder component for textareas (AC: 1, 2, 3, 4, 5, 6)
  - [ ] Create `frontend/components/rotating-placeholder.tsx` with per-field cycling state (topic vs audience) and a 4s interval
  - [ ] Stop cycling immediately on focus; permanently disable cycling after first focus for that field
  - [ ] Respect `prefers-reduced-motion` via `matchMedia` and short-circuit cycling when active
- [ ] Wire RotatingPlaceholder into the landing page form (AC: 1, 2, 4, 5)
  - [ ] Use RotatingPlaceholder for both topic and audience textareas in `frontend/app/page.tsx`
  - [ ] Keep existing validation and email capture behavior unchanged (Story 2.2)
  - [ ] Store example strings in `frontend/lib/messages.ts` and import them (no hard-coded Hungarian strings)
- [ ] Add/update tests for rotating placeholders (AC: 1, 2, 3, 4, 5, 6)
  - [ ] Component test for 4s cycling using fake timers
  - [ ] Stop-on-focus and no-restart-on-blur behavior
  - [ ] `prefers-reduced-motion` disables cycling

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

### Completion Notes List

### File List
