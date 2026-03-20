# Story 2.2: Research Query Submission Form

Status: ready-for-dev

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

- [ ] Build the submission form layout in `frontend/app/page.tsx` (AC: 1, 2, 5, 7)
  - [ ] Add labeled research topic and target audience textareas using shadcn/ui components
  - [ ] Add the PII warning below the research topic field
  - [ ] Use High Contrast Impact styling: pure black background, amber CTA, system font stack
  - [ ] Ensure responsive layout: `flex flex-col md:flex-row gap-3` and `max-w-lg` form width
- [ ] Implement form state and validation behavior (AC: 3, 4, 6)
  - [ ] Track field values in local state; disable submit until both are non-empty
  - [ ] Validate on blur; show inline error text below each field
  - [ ] Preserve field values after submit and reveal inline email capture UI
- [ ] Add inline email capture stub (UI only) below the form (AC: 6)
  - [ ] Render an email input field with label and microcopy (no submit wiring)
  - [ ] Do not call any Server Actions or FastAPI endpoints
- [ ] Accessibility and UX checks (AC: 1, 2, 3, 4, 7)
  - [ ] Ensure labels are visible and associated with inputs
  - [ ] Confirm `aria-disabled` is set on the CTA when disabled
  - [ ] Confirm tap targets meet 44x44px minimum

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

### Completion Notes List

### File List
