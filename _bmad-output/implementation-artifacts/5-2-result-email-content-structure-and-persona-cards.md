# Story 5.2: Result Email - Content Structure & Persona Cards

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user who receives a result email,
I want to see the most surprising finding immediately upon opening the email - without scrolling,
so that I experience the "aha moment" at the moment of email open, not after clicking through.

## Acceptance Criteria

1. Given a run has completed with >=12 personas, when the result email is composed by `run_processor.py`, then the aggregate sentiment score is computed as support/reject/conditional stance counts across all personas (FR15), and if >=15 personas align on support or rejection, `ConsensusFlag` is set with count + direction (FR17).
2. Given the result email is opened, when the user views above-the-fold content (no scroll), then `ConsensusFlag` (if triggered) is the first visible element (bold, high-contrast, icon + count text), aggregate sentiment score is visible above the fold, and the consensus block uses `role="alert"` in React Email context (FR15, FR17).
3. Given the user scrolls the email, when persona cards are rendered, then each full persona card shows persona name, role, stance label, primary argument, and condition for changing mind (FR16), with 4px left stance border colors (rose=reject, emerald=support, amber=conditional).
4. Given persona cards are rendered in email, when viewed on desktop and mobile, then cards display in a 3-column layout on desktop and 1-column layout on mobile.
5. Given the result email includes persona cards, when the footer area is rendered, then an interpretive disclaimer is present stating results are AI-generated synthetic simulations and not real human research (FR18).

## Tasks / Subtasks

- [x] Extend run result aggregation payload for email-first insights (AC: 1)
  - [x] In `backend/app/services/run_processor.py`, compute deterministic stance counts from `PersonaResponse.stance` and expose a stable `aggregate_score` display payload (Hungarian, user-facing safe).
  - [x] Add consensus derivation helper: trigger only for `support` or `reject` with threshold `>=15`; never trigger for `conditional` or mixed-majority below threshold.
  - [x] Include explicit consensus metadata in payload (recommended split: machine fields + localized display string) so template rendering is deterministic and testable.

- [x] Implement dedicated email-safe consensus block and above-the-fold ordering (AC: 2)
  - [x] Add an email-safe consensus component (e.g. `frontend/emails/consensus-flag-email.tsx`) using inline styles and `role="alert"`.
  - [x] Update `frontend/emails/result-email.tsx` so rendered order is: consensus block (if present) -> aggregate score summary -> remaining context.
  - [x] Keep visual hierarchy high-contrast and compatible with Gmail web/mobile, Apple Mail, and Outlook 2019.

- [x] Upgrade persona card content from summary-only to full argument model (AC: 3)
  - [x] Extend `ResultEmailPersona` and `PersonaCardEmail` to include and render `primary_argument` and `change_condition` as separate fields.
  - [x] Preserve existing stance semantics and token usage from Story 5.1 (`stanceReject`, `stanceSupport`, `stanceConditional`, 4px left border).
  - [x] Ensure stance meaning is never color-only (keep visible stance label text).

- [x] Implement robust responsive email layout for persona cards (AC: 4)
  - [x] Render persona cards using an email-compatible grid strategy that results in 3 columns on desktop and 1 column on mobile.
  - [x] Use table-safe markup with `role="presentation"`; keep styles inline to preserve cross-client behavior.
  - [x] Validate no clipping/overlap in above-the-fold block and first row of persona cards.

- [x] Add interpretive disclaimer block for AI simulation transparency (AC: 5)
  - [x] Add dedicated disclaimer copy under `messages.email.result` (or reuse shared legal copy if already defined) in Hungarian.
  - [x] Render disclaimer at bottom of email with secondary visual weight, without competing with the primary insight block.

- [x] Expand automated and manual verification coverage (AC: 1-5)
  - [x] Frontend email tests (`frontend/emails/result-email.test.tsx`) for ordering, consensus block visibility/absence, role attribute, aggregate score block, full persona fields, and disclaimer presence.
  - [x] Backend tests (`backend/tests/services/test_run_processor.py`) for aggregate-score counts, consensus threshold behavior, and edge cases (`15/15`, `15/18`, `14/18`, all-conditional).
  - [x] Keep/refresh compatibility evidence document for Gmail web/mobile, Apple Mail, and Outlook 2019.

## Dev Notes

- Story 5.1 already established React Email structure and tokenized styling in `frontend/emails/result-email.tsx`; this story should evolve that template rather than replacing it.
- Current backend result payload in `run_processor.py` already contains `stance_counts` and persona list, but email-facing fields are not yet optimized for AC-level presentation logic (consensus-first "aha" hierarchy).
- Current `email_service.py` still sends compact JSON payload HTML. If full template rendering wiring is deferred to Story 5.3, keep payload contract ready and backward-compatible now to avoid rework.
- Persona model already provides required fields via `PersonaResponse`: `name`, `role`, `stance`, `primary_argument`, `change_condition`.

### Architecture Compliance

- Keep result-email implementation under `frontend/emails/` and backend composition in `backend/app/services/run_processor.py`.
- Keep all user-visible Hungarian strings in `frontend/lib/messages.ts`; never hard-code Hungarian text in templates.
- Continue using `frontend/lib/tokens.ts` as single source of truth for email/browser color parity.
- Preserve canonical run statuses and existing partial/completed behavior from Story 4.4.

### Library / Framework Requirements

- React Email + inline CSS only for email blocks.
- TypeScript strict typing for email prop contracts (no `any`).
- Python 3.12 + Pydantic v2 style preserved in backend helpers/tests.

### File Structure Requirements

- Primary expected files:
  - `frontend/emails/result-email.tsx`
  - `frontend/emails/persona-card-email.tsx`
  - `frontend/emails/result-email.test.tsx`
  - `backend/app/services/run_processor.py`
  - `backend/tests/services/test_run_processor.py`
  - `frontend/lib/messages.ts`
- Optional new helper file:
  - `frontend/emails/consensus-flag-email.tsx`

### Testing Requirements

- Frontend: `cd frontend && pnpm test` (include focused coverage for result email rendering).
- Backend: `cd backend && pytest` (include new run-processor aggregation/consensus tests).
- Validate aria/semantics: `role="alert"` for consensus, `role="presentation"` for layout tables.

### Previous Story Intelligence (5.1)

- Keep 5.1 fixes intact: null-safe persona list handling, consensus empty-string fallback behavior, and Outlook table compatibility choices.
- Reuse existing email primitive structure instead of introducing a parallel template stack.
- Preserve existing compatibility evidence workflow and extend it with consensus-above-fold screenshots/checklist notes.

### Git Intelligence Summary

- Recent commit pattern shows story lifecycle: create story context -> implement -> apply code review patches -> close story.
- Most recent commits for Epic 5 touched email template contracts and regression tests; expect adjacent-file changes and preserve established naming/style conventions.

### Latest Tech Information

- Project context pins React 19.2.4 / Next.js 16.2.0 and emphasizes React Email inline-style compatibility requirements.
- For this story, priority is deterministic rendering and client compatibility over introducing new dependencies.

### Project Context Reference

- `_bmad-output/project-context.md`

### References

- Epic source: `_bmad-output/planning-artifacts/epics.md` (Epic 5, Story 5.2)
- PRD source: `_bmad-output/planning-artifacts/prd.md` (FR15, FR16, FR17, FR18)
- Architecture source: `_bmad-output/planning-artifacts/architecture.md` (React Email, shared tokens, email/browser continuity)
- UX source: `_bmad-output/planning-artifacts/ux-design-specification.md` (above-the-fold insight hierarchy, persona card semantics, responsive behavior)
- Prior story context: `_bmad-output/implementation-artifacts/5-1-result-email-react-email-templates-and-design-tokens.md`
- Existing implementation anchors: `frontend/emails/result-email.tsx`, `frontend/emails/persona-card-email.tsx`, `backend/app/services/run_processor.py`, `backend/app/services/email_service.py`, `frontend/lib/messages.ts`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- `git log -5 --pretty=format:'%h %s'`
- `frontend/emails/result-email.tsx`
- `frontend/emails/persona-card-email.tsx`
- `backend/app/services/run_processor.py`
- `backend/app/services/email_service.py`
- `frontend/lib/messages.ts`
- `frontend/emails/consensus-flag-email.tsx`
- `frontend/emails/result-email-compatibility-evidence.md`
- `pnpm test -- --run` (frontend)
- `pnpm lint` (frontend)
- `pytest` (backend)

### Completion Notes List

- Ultimate context analysis completed for Story 5.2 with implementation guardrails focused on consensus-first email hierarchy and full persona argument rendering.
- Previous-story learnings and recent git patterns were incorporated to reduce regression risk during implementation.
- Added deterministic backend aggregation payloads in `run_processor.py`: stance counts, localized aggregate score display, and machine+display consensus metadata with strict `>=15` threshold behavior.
- Added backend regression coverage for consensus edge-cases (`15/15`, `15/18`, `14/18`, all-conditional) and validated no regressions with full backend suite.
- Implemented dedicated consensus alert component and reordered email above-the-fold hierarchy to render consensus first (when present), then aggregate score.
- Upgraded persona card rendering to full argument model with explicit labels for primary argument and change condition while preserving stance text semantics and 4px tokenized borders.
- Implemented responsive persona-card email layout strategy (3-column desktop, 1-column mobile) with table-safe markup and mobile media fallback.
- Added Hungarian interpretive disclaimer copy in `messages.email.result` and rendered it in the email footer with secondary visual weight.
- Refreshed compatibility design-intent checklist for Story 5.2 and validated frontend test and lint suites pass.

### Code Review Addendum (Intent Gaps)

- IG-1: Tie-break behavior for consensus in threshold-equal support/reject cases is not yet explicitly specified in AC text; implementation currently needs a follow-up decision.
- IG-2: `role="alert"` usage on table-based email markup conflicts with ARIA validity expectations; implementation should be adjusted while preserving email-client compatibility.

### Code Review Patches Applied (2026-03-21)

- P-1: Removed dead code branches 3 and 4 from `_build_consensus_payload` — both were unreachable given branches 1 and 2 already cover all cases where one side meets the threshold and exceeds the other. Tie case (both ≥ 15 and equal) correctly produces no consensus.
- P-2: Replaced direct `stance_counts["key"]` indexing with `.get("key", 0)` in both `_build_aggregate_score_payload` and `_build_consensus_payload` for defense-in-depth.
- P-3 (deferred to Story 5.3): Hungarian display strings in backend (`aggregate_score_display`, `consensus_flag_display`) cannot be cleanly moved to `messages.ts` without changing the email payload contract; addressed when full React Email wiring is completed in Story 5.3.
- P-4: Added filler `<td>` cells for partial last rows in the persona card grid (1 or 2 personas in last row) to preserve 3-column table structure.
- P-5: Fixed `paddingRight` logic to use `columnIndex < row.length - 1` instead of hardcoded `columnIndex < 2`, correctly handling partial rows.
- P-6: Moved `⚠` icon from hard-coded template literal in `consensus-flag-email.tsx` to `messages.ts` (`consensusIcon` key); `result-email.tsx` now composes the label from `copy.consensusIcon` + `copy.consensusLabel`.
- P-7: Removed `personas ?? []` defensive guard from `groupPersonas` call; `personas` is non-optional in `ResultEmailProps` and the guard was masking a potential upstream bug.

### File List

- _bmad-output/implementation-artifacts/5-2-result-email-content-structure-and-persona-cards.md
- backend/app/services/run_processor.py
- backend/tests/services/test_run_processor.py
- frontend/emails/consensus-flag-email.tsx
- frontend/emails/persona-card-email.tsx
- frontend/emails/result-email.tsx
- frontend/emails/result-email.test.tsx
- frontend/emails/result-email-compatibility-evidence.md
- frontend/lib/messages.ts

### Change Log

- 2026-03-21: Implemented Story 5.2 consensus-first email composition, full persona card argument model, responsive card layout, Hungarian disclaimer transparency copy, and expanded backend/frontend verification coverage.
- 2026-03-21: Added code-review intent-gap addendum (IG-1 tie-break and IG-2 ARIA validity) without resetting implementation history.
- 2026-03-21: Applied code review patches P-1 through P-7 (P-3 deferred to 5.3); all backend and frontend tests pass.
