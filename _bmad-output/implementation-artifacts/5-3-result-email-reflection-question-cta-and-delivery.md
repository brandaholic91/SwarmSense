# Story 5.3: Result Email - Reflection Question, CTA & Delivery

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want to receive my result email within 120 seconds and find a closing reflection question that invites me to act on the insight,
so that the product experience ends with a concrete prompt rather than just information delivery.

## Acceptance Criteria

1. Given a run has reached `completed` or `partial` status, when `email_service.py` sends the result email via Resend, then the result email is sent within 120 seconds of successful magic link verification for p95 runs (NFR4), and transactional email delivery success rate is >=95% per rolling 7-day window (NFR12).
2. Given a result email is rendered, when the user reaches the bottom section, then the closing reflection question "Mit tennel maskepp ennek alapjan?" is present and a single CTA directly below it links to the Pro tier waitlist (FR19).
3. Given result email delivery is configured, when the email is sent, then `reply_to` is a real monitored operator address and the subject line is exactly "A SwarmSense elemzesed elkeszult" (FR20).
4. Given a partial result (12-19 personas), when the result email is sent, then the header displays `"{completed}/{total} persona valaszolt"` (FR12).
5. Given Resend delivery fails, when the provider returns an error, then failure is logged with error code and timestamp metadata while run status remains `completed` or `partial` (NFR13).

## Tasks / Subtasks

- [ ] Replace placeholder result email payload dump with production template rendering path (AC: 1, 4)
  - [ ] In `backend/app/services/email_service.py`, replace compact `<pre>` payload HTML with React Email-rendered HTML generated from `frontend/emails/result-email.tsx` output contract.
  - [ ] Introduce a deterministic payload-to-template mapper in backend (or shared contract module) that maps `run_processor` payload keys (`persona_count_label`, `aggregate_score_display`, `consensus_flag_display`, `personas`, `topic`, `audience`, `recipient_email`) to `ResultEmailProps`.
  - [ ] For partial results, format header copy as `"{completed}/{total} persona valaszolt"` (not generic count text) while preserving existing `run_processor` machine fields.

- [ ] Implement reflection-question closing block with single CTA in result email template (AC: 2)
  - [ ] Extend `messages.email.result` with explicit keys for `reflectionQuestion`, `reflectionCtaLabel`, and optional helper text.
  - [ ] Update `frontend/emails/result-email.tsx` to render the reflection question near the footer and one CTA element directly below it.
  - [ ] Keep exactly one actionable CTA in the result email body (no secondary upsell or cross-sell links).

- [ ] Finalize subject and reply-to semantics in backend dispatch (AC: 3)
  - [ ] In `backend/app/services/email_service.py`, set subject from `messages.email.result.subject` semantics to the required Hungarian line: `"A SwarmSense elemzesed elkeszult"`.
  - [ ] Keep `reply_to` sourced from `settings.email_reply_to`; ensure non-empty value and document fallback behavior in `.env.example`.
  - [ ] Preserve sender identity via `settings.email_from` and avoid hard-coded addresses in code.

- [ ] Harden delivery-failure observability without mutating final run status (AC: 5)
  - [ ] In `backend/app/services/run_processor.py` and/or `email_service.py`, keep `completed`/`partial` status unchanged after send attempt.
  - [ ] Capture Resend error metadata (provider error code/message) with timestamp and `run_id` in Sentry context.
  - [ ] Add explicit regression test asserting email send exception does not revert run status to `failed`.

- [ ] Add focused automated coverage for Story 5.3 contract (AC: 1-5)
  - [ ] Backend tests in `backend/tests/services/test_run_processor.py` and new `backend/tests/services/test_email_service.py` for: subject line, reply-to propagation, partial-count text, and failure logging behavior.
  - [ ] Frontend email tests in `frontend/emails/result-email.test.tsx` for reflection question + single CTA presence and no duplicate action links.
  - [ ] Add/update a compatibility evidence note in `frontend/emails/result-email-compatibility-evidence.md` verifying bottom-of-email reflection block rendering across Gmail web/mobile, Apple Mail, and Outlook 2019.

## Dev Notes

- Story 5.1 and 5.2 already implemented the React Email structure, consensus-first ordering, full persona card content, and disclaimer. Story 5.3 should extend those artifacts, not rework them.
- Current blocker is backend delivery path: `send_run_result_email` still sends a JSON payload dump with an outdated subject (`SwarmSense run result (...)`) instead of the production template.
- `run_processor.py` already assembles core aggregates and consensus fields and intentionally keeps run status finalized before email dispatch. Preserve this behavior to satisfy AC5/NFR13.
- Keep Hungarian user-visible strings in `frontend/lib/messages.ts` (project rule), and avoid introducing hard-coded Hungarian text in backend where practical. If backend must set subject, keep a single canonical source and document it.

### Architecture Compliance

- Result email rendering remains under `frontend/emails/`; backend dispatch logic remains in `backend/app/services/email_service.py`.
- All outbound email still flows through Resend (server-to-server) with `reply_to` and sender identity from `Settings` (`SWARMSENSE_` env namespace).
- Maintain canonical run statuses only: `queued`, `running`, `composing`, `completed`, `partial`, `failed`.
- Preserve `snake_case` payload keys at API/service boundaries.

### Library / Framework Requirements

- Frontend: React Email components + inline CSS only (existing pattern in `result-email.tsx`).
- Backend: FastAPI service layer + Resend Python SDK (`resend.Emails.send`) with structured exception capture.
- Keep TypeScript strict and Python 3.12 typing conventions from project context.

### File Structure Requirements

- Primary expected files to modify:
  - `backend/app/services/email_service.py`
  - `backend/app/services/run_processor.py`
  - `backend/tests/services/test_run_processor.py`
  - `frontend/emails/result-email.tsx`
  - `frontend/emails/result-email.test.tsx`
  - `frontend/lib/messages.ts`
  - `backend/.env.example`
- Optional new test/helper file:
  - `backend/tests/services/test_email_service.py`

### Testing Requirements

- Backend:
  - `cd backend && pytest`
  - Include explicit assertions for delivery-failure logging and status immutability after failed dispatch.
- Frontend:
  - `cd frontend && pnpm test -- --run`
  - Confirm reflection question block and single CTA output in rendered HTML.
- Quality gates:
  - `cd frontend && pnpm lint`
  - Ensure no regression in existing result-email semantics (consensus, aggregate score, persona cards, disclaimer).

### Previous Story Intelligence (5.2)

- Reuse existing `ConsensusFlagEmail`, `PersonaCardEmail`, and grid fallback behavior; do not introduce a parallel email template stack.
- Keep code-review learnings from 5.2:
  - defensive `.get(...)` access in payload builders,
  - tie-safe consensus logic (no consensus on equal-threshold ties),
  - avoid masking schema issues with unnecessary null fallbacks where contract is non-optional,
  - preserve Outlook-safe table structure.
- Deferred item from 5.2 (`P-3`) is directly relevant: centralized Hungarian display strings and final payload/template wiring should be completed here.

### Git Intelligence Summary

- Recent Epic 5 commit sequence is stable and repeatable: create story context -> implement -> apply code review patches -> close story.
- Adjacent code hotspots are `frontend/emails/*` and `backend/app/services/*`; keep changes localized to avoid regressions in prior stories.
- Commit history indicates strong test-first/patch cycle for email stories; maintain or improve coverage before marking done.

### Latest Tech Information

- Project pins React 19.2.4 + Next.js 16.2.0 + React Email for template rendering and FastAPI 0.135.1 + Resend 2.25.0 on backend.
- No new dependency is required for Story 5.3; prioritize contract completion and observability over introducing additional libraries.

### Project Context Reference

- `_bmad-output/project-context.md`

### References

- Epic source: `_bmad-output/planning-artifacts/epics.md` (Epic 5, Story 5.3)
- PRD source: `_bmad-output/planning-artifacts/prd.md` (FR12, FR19, FR20, NFR4, NFR12, NFR13)
- Architecture source: `_bmad-output/planning-artifacts/architecture.md` (Resend integration, email/browser continuity, backend service boundaries)
- UX source: `_bmad-output/planning-artifacts/ux-design-specification.md` (result-email flow completion, reflection action, single CTA principle)
- Prior stories:
  - `_bmad-output/implementation-artifacts/5-1-result-email-react-email-templates-and-design-tokens.md`
  - `_bmad-output/implementation-artifacts/5-2-result-email-content-structure-and-persona-cards.md`
- Current implementation anchors:
  - `backend/app/services/email_service.py`
  - `backend/app/services/run_processor.py`
  - `frontend/emails/result-email.tsx`
  - `frontend/emails/result-email.test.tsx`
  - `frontend/lib/messages.ts`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- `git log -5 --oneline`
- `backend/app/services/email_service.py`
- `backend/app/services/run_processor.py`
- `frontend/emails/result-email.tsx`
- `frontend/emails/result-email.test.tsx`
- `frontend/lib/messages.ts`

### Completion Notes List

- Ultimate context analysis completed for Story 5.3 with explicit guardrails for production-grade result email delivery.
- Story context preserves prior Epic 5 email architecture and focuses on closing the final delivery gap (template wiring, reflection CTA, subject/reply-to correctness, failure observability).
- Cross-story constraints, architecture boundaries, and regression risks are captured for deterministic dev-agent implementation.

### File List

- _bmad-output/implementation-artifacts/5-3-result-email-reflection-question-cta-and-delivery.md

### Change Log

- 2026-03-21: Created Story 5.3 ready-for-dev context with comprehensive implementation guidance, dependencies, and verification scope.
