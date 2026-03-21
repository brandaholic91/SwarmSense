# Story 5.2: Result Email - Content Structure & Persona Cards

Status: ready-for-dev

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

- [ ] Extend run result aggregation payload for email-first insights (AC: 1)
  - [ ] In `backend/app/services/run_processor.py`, compute deterministic stance counts from `PersonaResponse.stance` and expose a stable `aggregate_score` display payload (Hungarian, user-facing safe).
  - [ ] Add consensus derivation helper: trigger only for `support` or `reject` with threshold `>=15`; never trigger for `conditional` or mixed-majority below threshold.
  - [ ] Include explicit consensus metadata in payload (recommended split: machine fields + localized display string) so template rendering is deterministic and testable.

- [ ] Implement dedicated email-safe consensus block and above-the-fold ordering (AC: 2)
  - [ ] Add an email-safe consensus component (e.g. `frontend/emails/consensus-flag-email.tsx`) using inline styles and `role="alert"`.
  - [ ] Update `frontend/emails/result-email.tsx` so rendered order is: consensus block (if present) -> aggregate score summary -> remaining context.
  - [ ] Keep visual hierarchy high-contrast and compatible with Gmail web/mobile, Apple Mail, and Outlook 2019.

- [ ] Upgrade persona card content from summary-only to full argument model (AC: 3)
  - [ ] Extend `ResultEmailPersona` and `PersonaCardEmail` to include and render `primary_argument` and `change_condition` as separate fields.
  - [ ] Preserve existing stance semantics and token usage from Story 5.1 (`stanceReject`, `stanceSupport`, `stanceConditional`, 4px left border).
  - [ ] Ensure stance meaning is never color-only (keep visible stance label text).

- [ ] Implement robust responsive email layout for persona cards (AC: 4)
  - [ ] Render persona cards using an email-compatible grid strategy that results in 3 columns on desktop and 1 column on mobile.
  - [ ] Use table-safe markup with `role="presentation"`; keep styles inline to preserve cross-client behavior.
  - [ ] Validate no clipping/overlap in above-the-fold block and first row of persona cards.

- [ ] Add interpretive disclaimer block for AI simulation transparency (AC: 5)
  - [ ] Add dedicated disclaimer copy under `messages.email.result` (or reuse shared legal copy if already defined) in Hungarian.
  - [ ] Render disclaimer at bottom of email with secondary visual weight, without competing with the primary insight block.

- [ ] Expand automated and manual verification coverage (AC: 1-5)
  - [ ] Frontend email tests (`frontend/emails/result-email.test.tsx`) for ordering, consensus block visibility/absence, role attribute, aggregate score block, full persona fields, and disclaimer presence.
  - [ ] Backend tests (`backend/tests/services/test_run_processor.py`) for aggregate-score counts, consensus threshold behavior, and edge cases (`15/15`, `15/18`, `14/18`, all-conditional).
  - [ ] Keep/refresh compatibility evidence document for Gmail web/mobile, Apple Mail, and Outlook 2019.

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

### Completion Notes List

- Ultimate context analysis completed for Story 5.2 with implementation guardrails focused on consensus-first email hierarchy and full persona argument rendering.
- Previous-story learnings and recent git patterns were incorporated to reduce regression risk during implementation.

### File List

- _bmad-output/implementation-artifacts/5-2-result-email-content-structure-and-persona-cards.md
