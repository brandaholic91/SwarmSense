# Story 4.1: Qualifier Survey Screen

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a verified user,
I want to answer two quick questions about my role and intended use case before my analysis starts,
so that persona generation can be calibrated to my context without adding significant friction.

## Acceptance Criteria

1. Given a user has successfully verified their magic link and arrives at `/qualifier`, when the qualifier screen loads, then the page displays framing copy "Segits kalibralni a personakat".
2. Given the qualifier screen is visible, when Question 1 is rendered, then it is a Select/dropdown labeled "Mi jellemzi legjobban a szerepkoret?" with at least 5 role options.
3. Given the qualifier screen is visible, when Question 2 is rendered, then it is a RadioGroup labeled "Milyen celra szeretne leginkabb hasznalni a szintetikus kutatast?" with at least 4 use-case options.
4. Given the user views the screen, when interacting with fields, then no free-text inputs are present (clickable selectors only).
5. Given both questions are not answered, when viewing primary action, then submit button is disabled until both are selected.
6. Given the qualifier screen renders on mobile, when Question 2 is shown, then RadioGroup items are full-width and minimum 48px height.
7. Given migrations `20260319_003_runs.sql` and `20260319_004_qualifier_responses.sql` are applied, when schema is checked, then table `runs` exists with required columns and canonical statuses (`queued`, `running`, `composing`, `completed`, `partial`, `failed`).
8. Given migrations `20260319_003_runs.sql` and `20260319_004_qualifier_responses.sql` are applied, when schema is checked, then `qualifier_responses` exists with required columns (`id`, `run_id`, `user_id`, `role_answer`, `use_case_answer`, `created_at`).
9. Given both tables are present, when security is validated, then RLS is active for service-role-only access on `runs` and `qualifier_responses`.

## Tasks / Subtasks

- [ ] Build `/qualifier` page and preserve single-focus funnel behavior (AC: 1, 4, 5)
  - [ ] Implement `frontend/app/qualifier/page.tsx` as App Router page (default export) with one primary action and no competing CTAs.
  - [ ] Use copy from `frontend/lib/messages.ts` (no hardcoded Hungarian strings in component).
  - [ ] Ensure page keeps conversion-focused layout (`max-w-lg`, centered flow, one primary CTA).

- [ ] Implement selector-only qualifier inputs (AC: 2, 3, 4)
  - [ ] Add role Select (>=5 options) and use-case RadioGroup (>=4 options) using shadcn/ui components.
  - [ ] Validate no textareas/inputs are used for answers; only predefined options allowed.
  - [ ] Keep labels explicit and visible for accessibility compliance.

- [ ] Implement disabled/validation behavior matching project patterns (AC: 5)
  - [ ] Submit button disabled until both answers are selected.
  - [ ] Apply on-blur validation behavior and inline field error patterns from existing frontend conventions.
  - [ ] Keep state local via `useState`; do not introduce global client state store.

- [ ] Enforce responsive and accessibility requirements (AC: 6)
  - [ ] Mobile RadioGroup options full-width, min-height 48px.
  - [ ] Keyboard navigation works across Select, RadioGroup, and submit.
  - [ ] Focus-visible ring and semantic structure align with existing design tokens and WCAG guidance.

- [ ] Verify schema prerequisites and backend compatibility (AC: 7, 8, 9)
  - [ ] Confirm migration files for `runs` and `qualifier_responses` define expected columns and status constraints.
  - [ ] Confirm RLS policy state for both tables and document any missing policy/action required before production.
  - [ ] Ensure frontend payload and API boundary fields are `snake_case` in anticipation of Story 4.2 submit wiring.

- [ ] Add tests for qualifier UI contract (AC: 1-6)
  - [ ] Add page/component tests for framing copy, selector types, option counts, and disabled submit behavior.
  - [ ] Add responsive/a11y assertions for mobile RadioGroup sizing and label presence.
  - [ ] Ensure tests follow co-located frontend test conventions and pass with existing Vitest setup.

## Dev Notes

- This story is UI + schema-readiness focused; run initiation and background dispatch belong to Story 4.2.
- Keep funnel continuity from Story 3.2 verification output to `/qualifier` entry, but do not re-implement verification logic here.
- Do not introduce frontend Supabase client usage; persistence remains backend-only.
- All user-facing copy must come from `frontend/lib/messages.ts`.

### Architecture Compliance

- App Router path: `frontend/app/qualifier/page.tsx`.
- Canonical run statuses must remain: `queued`, `running`, `composing`, `completed`, `partial`, `failed`.
- API/JSON field names are `snake_case`.
- No secrets in browser; Server Actions handle sensitive calls.

### Library / Framework Requirements

- Next.js 16.2 App Router + React 19 + TypeScript strict.
- shadcn/ui Select + RadioGroup for input controls.
- Tailwind v4 utility styling + tokens from `frontend/lib/tokens.ts`.
- Vitest + React Testing Library for frontend tests.

### File Structure Requirements

- Frontend page: `frontend/app/qualifier/page.tsx`
- Optional server action scaffold (if needed for handoff only): `frontend/app/actions/` (no persistence in this story)
- Message catalog updates: `frontend/lib/messages.ts`
- Tests: co-located under `frontend/app/qualifier/` and/or related component files

### Testing Requirements

- Frontend tests: `cd frontend && pnpm test`
- Frontend lint/type checks: `cd frontend && pnpm lint` and project type-check command
- Migration/schema validation (if run locally): `supabase db push` + schema inspection for `runs` and `qualifier_responses`

### Previous Story Intelligence (Epic 3 closure)

- Reuse deterministic flow handoff patterns established in Story 3.2/3.3 (server-side redirect and contract-safe params).
- Continue centralized error/message mapping (`frontend/lib/errors.ts`, `frontend/lib/messages.ts`).
- Keep strict single-action screen principle and no competing CTAs in conversion-critical steps.

### Git Intelligence Summary

- Recent work established robust auth + blocked flow; qualifier screen should integrate with that flow without introducing alternate paths.
- Existing backend routers/tests are already in place for auth and waitlist; this story should avoid backend refactors outside schema verification.
- Keep story hygiene consistent with recent pattern: explicit AC mapping, tests, and sprint status transitions.

### Latest Tech Information

- Use project-pinned stack from `_bmad-output/project-context.md`.
- No new libraries are required for this story.
- Keep TanStack Query polling concerns out of this story; waiting-state polling is Story 4.5 scope.

### Project Context Reference

- Follow `_bmad-output/project-context.md` for strict TS rules, naming conventions, testing patterns, and anti-pattern bans.

### References

- Epic source and AC: `_bmad-output/planning-artifacts/epics.md` (Epic 4, Story 4.1)
- PRD requirements mapping: `_bmad-output/planning-artifacts/prd.md` (FR36, FR10-FR13 context)
- Architecture constraints: `_bmad-output/planning-artifacts/architecture.md`
- UX behavior and responsive/a11y details: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Project rules: `_bmad-output/project-context.md`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- Story selected explicitly by user request: `4.1`

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

- _bmad-output/implementation-artifacts/4-1-qualifier-survey-screen.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
