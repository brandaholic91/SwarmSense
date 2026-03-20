# Story 2.2: Research Query Submission Form

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a visitor,
I want to fill in a research topic and a target audience description and submit my query,
so that I can initiate a SwarmSense analysis without needing an account or any pre-registration.

## Acceptance Criteria

1. Given a visitor is on the landing page, when they view the submission form, then two textarea fields are visible with labels: one for the research topic and one for the target audience description.
2. Given the research topic field is visible, when the form renders, then a static PII warning appears below the research topic field: "Ne adj meg személyes adatokat a kutatási témában" (FR34).
3. Given the form is visible, when the visitor has not completed both fields, then the primary CTA button is disabled with `aria-disabled="true"` until both fields contain non-empty text.
4. Given the visitor completes both fields, when they blur a field, then inline validation errors render below the field (no toast) and validation does not fire on keystroke.
5. Given the form renders, when the visitor views the CTA, then the only submit action is a primary amber-400 button with black text and weight 800.
6. Given the visitor submits the form with both fields filled, when the submit action completes, then the email capture field appears inline below the form without page reload or redirect, and the research topic and audience values remain visible.
7. Given the page is viewed on a mobile device (320px–767px), when the form renders, then the two textareas stack vertically and all tap targets are at least 44x44px.

> Implementation note: The email capture field is a UI scaffold only in this story. Do not wire Server Actions or call `POST /api/v1/auth/check-email` until Story 3.1.

## Tasks / Subtasks

- [x] Build the submission form layout in `frontend/app/page.tsx` (AC: 1, 2, 5, 7)
  - [x] Add labeled research topic and target audience textareas using shadcn/ui components
  - [x] Add the PII warning below the research topic field
  - [x] Use High Contrast Impact styling: pure black background, amber CTA, system font stack
  - [x] Ensure responsive layout: `flex flex-col md:flex-row gap-3` and `max-w-lg` form width
- [x] Implement form state and validation behavior (AC: 3, 4, 6)
  - [x] Track field values in local state; disable submit until both are non-empty
  - [x] Validate on blur; show inline error text below each field
  - [x] Preserve field values after submit and reveal inline email capture UI
- [x] Add inline email capture stub (UI only) below the form (AC: 6)
  - [x] Render an email input field with label and microcopy (no submit wiring)
  - [x] Do not call any Server Actions or FastAPI endpoints
- [x] Accessibility and UX checks (AC: 1, 2, 3, 4, 7)
  - [x] Ensure labels are visible and associated with inputs
  - [x] Confirm `aria-disabled` is set on the CTA when disabled
  - [x] Confirm tap targets meet 44x44px minimum

## Dev Notes

- Scope boundaries: do NOT implement rotating placeholders (Story 2.3) or email check wiring (Story 3.1). This story is the form UI + local validation + inline email capture scaffold only.
- Follow architecture rules: all Hungarian text must come from `frontend/lib/messages.ts` (no hard-coded strings in components). Colors must use `frontend/lib/tokens.ts`.
- Validation behavior: on blur only; inline error text below fields; no toasts. Submit disabled until both fields are non-empty.
- Maintain High Contrast Impact design: black background, amber CTA, bold weight on primary button, tabular-nums where counts appear.
- Keep layout consistent with UX spec: landing page `max-w-2xl`, form block `max-w-lg`, `mx-auto px-4 sm:px-6`.

### Project Structure Notes

- Landing page form is implemented in `frontend/app/page.tsx`.
- Shared copy and tokens live in `frontend/lib/messages.ts` and `frontend/lib/tokens.ts`.
- Use existing shadcn/ui components from `frontend/components/ui/` (`textarea`, `button`, `input`).

### References

- Epic 2 Story 2.2 acceptance criteria: `_bmad-output/planning-artifacts/epics.md`
- UX form patterns, responsive layout, and microcopy rules: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Architecture constraints and Hungarian text rule: `_bmad-output/planning-artifacts/architecture.md`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.2-codex

### Debug Log References

- 2026-03-20: Implemented landing form UI, local validation, and email capture stub; ran `pnpm test` and `pnpm lint` in `frontend/`.

### Completion Notes List

- Added submission form UI with responsive layout, PII warning, and amber CTA using tokens and messages.
- Implemented on-blur validation, disabled submit gating, and inline email capture scaffold with value preservation.
- Added input/textarea shadcn components and expanded landing page tests for form behavior.
- Verified `pnpm test` and `pnpm lint` pass in `frontend/`.

### File List

- _bmad-output/implementation-artifacts/2-2-research-query-submission-form.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- frontend/app/page.tsx
- frontend/app/page.test.tsx
- frontend/components/ui/input.tsx
- frontend/components/ui/textarea.tsx
- frontend/lib/messages.ts

### Change Log

- 2026-03-20: Implemented the research submission form UI, validation, and email capture stub with supporting components and tests.
