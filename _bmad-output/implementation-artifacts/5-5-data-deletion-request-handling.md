# Story 5.5: Data Deletion Request Handling

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want to be able to request deletion of my personal data by email and receive confirmation within defined SLAs,
so that I can exercise my GDPR right to erasure.

## Acceptance Criteria

1. Given a user sends a data deletion request email to the operator's designated address, when the operator receives the request, then the Privacy Policy documents the deletion contact email address and the expected response timeline.
2. Given a deletion request is received, when inbox automation evaluates inbound mail, then an automated acknowledgement email is sent to the requester within 15 minutes (FR33), implemented as an inbox auto-responder (Resend inbound, Gmail filter, or equivalent) without introducing a custom FastAPI endpoint for MVP.
3. Given a valid deletion request is confirmed, when the operator executes the deletion workflow, then the user's records are deleted from `users`, `runs`, `qualifier_responses`, `magic_link_tokens`, and `waitlist` within 7 calendar days (FR33), leaving no orphaned PII in any table.
4. Given deletion is completed, when closure communication is sent, then the user receives a deletion completion confirmation email within 7 calendar days.
5. Given deletion has completed, when the same email address is later submitted in the product flow, then the system treats it as a new first-time user with no blocking and no prior run history.

## Tasks / Subtasks

- [x] Implement deletion request operations runbook and SLA guardrails (AC: 1, 2, 3, 4)
  - [x] Add a dedicated operations document in `docs/` describing: intake mailbox, validation checklist, 15-minute acknowledgement SLA, 7-day completion SLA, and operator accountability.
  - [x] Define the exact acknowledgement and completion message templates (Hungarian user-facing copy in `frontend/lib/messages.ts` if reused by app/email render paths; otherwise documented as operator mailbox templates).
  - [x] Document escalation path for weekends/holidays and logging expectations (timestamped receipt, acknowledgement sent timestamp, completion timestamp).

- [x] Add Privacy Policy content required by FR33 (AC: 1)
  - [x] Replace placeholder content in `frontend/app/privacy/page.tsx` with production Privacy Policy sections that include the deletion contact channel and SLA commitments.
  - [x] Ensure legal page copy references only email-based deletion for MVP (no self-service portal claims).
  - [x] Add/align legal strings in `frontend/lib/messages.ts` and keep user-facing text Hungarian per project rules.

- [x] Implement safe backend deletion workflow (no public deletion endpoint) (AC: 3, 5)
  - [x] Create a backend-only deletion workflow module (service/helper) that deletes by normalized email and removes dependent records in deterministic order.
  - [x] Ensure deletion flow removes associated `runs` and `qualifier_responses` linked to the user and leaves no orphaned records.
  - [x] Add dry-run mode and explicit confirmation guard (`--confirm`) for operator execution safety.
  - [x] Keep this workflow inaccessible from public/browser routes; trigger only via controlled operator process.

- [x] Add operator execution interface for deletion workflow (AC: 3, 5)
  - [x] Provide a script/CLI entry point under `backend/` to execute deletion by email with structured output.
  - [x] Enforce input normalization at backend boundary (`.lower().strip()`) and validate email format before deletion.
  - [x] Return/report counts of deleted rows per table to support completion audit trail.

- [x] Validate first-time-user behavior post-deletion (AC: 5)
  - [x] Add regression tests proving `POST /api/v1/auth/check-email` returns the new-user path after deletion.
  - [x] Add tests proving waitlist and unsubscribe artifacts tied to deleted user do not recreate blocked-user behavior.

- [x] Add comprehensive automated coverage and verification steps (AC: 1-5)
  - [x] Backend tests for deletion workflow success, idempotency, missing-user handling, and dependent-row cleanup.
  - [x] Backend tests for the operator execution wrapper (input validation, dry-run output, confirm guard behavior).
  - [x] Manual verification checklist in docs for SLA timestamps and email templates.

## Dev Notes

- Story 5.4 established operations-first compliance workflows (cron + protected operator endpoint + unsubscribe tokenization). Story 5.5 should follow the same principle: operationally safe, auditable, and minimal public attack surface.
- Epic requirement explicitly states no custom FastAPI endpoint is required for the deletion-request intake in MVP; keep request intake email-based.
- Because FR33 includes hard SLA guarantees (15 minutes acknowledgement, 7 days completion), implementation must include measurable timestamps and a repeatable operator playbook.
- Deletion must preserve existing behavior guarantees: after erase, the same email must pass through first-time-user flow without returning-user blocking.

### Architecture Compliance

- Keep public API surface unchanged for deletion intake; no browser-accessible deletion route.
- Backend logic should live in `backend/app/services/` (or adjacent internal module) and be invoked only from operator-controlled execution.
- Preserve `snake_case` contracts, Pydantic settings usage, and `SWARMSENSE_` env var conventions.
- Do not introduce frontend Supabase access; all data mutations remain backend-side.

### Library / Framework Requirements

- Backend: FastAPI 0.135.1, Supabase Python client 2.28.2, Python 3.12+.
- Frontend legal page: Next.js 16.2 App Router with Hungarian strings sourced from `frontend/lib/messages.ts`.
- Testing: pytest for backend workflow and route regressions; frontend tests only if legal-page rendering logic adds behavior.

### File Structure Requirements

- Primary backend targets:
  - `backend/app/services/` (new deletion workflow module)
  - `backend/tests/services/` (deletion workflow tests)
  - `backend/tests/routers/test_auth_post_deletion.py` (post-deletion new-user regression)
- Primary frontend/legal targets:
  - `frontend/app/privacy/page.tsx`
  - `frontend/lib/messages.ts`
- Operations/docs targets:
  - `docs/` (new deletion-operations runbook)

### Testing Requirements

- Backend:
  - `cd backend && pytest`
  - Validate deletion row cleanup, idempotency, guardrails, and first-time-user behavior after deletion.
- Frontend (if modified behavior beyond static copy):
  - `cd frontend && pnpm test -- --run`
  - `cd frontend && pnpm lint`

### Previous Story Intelligence (5.4)

- Reuse the strict operations hygiene from Story 5.4: deterministic workflows, explicit guardrails, and test-backed edge-case handling.
- Maintain compliance-driven behavior as code plus docs, not docs-only assumptions.
- Keep user communication links and legal language explicit and verifiable.

### Git Intelligence Summary

- Recent Epic 5 pattern is stable: context story -> implementation -> code review patches -> status done.
- Email/compliance-related work recently concentrated in `backend/app/services/`, `backend/app/routers/`, and `docs/`.
- Story 5.5 should keep changes focused on compliance operations and safe data lifecycle handling to minimize regressions.

### Latest Tech Information

- Project context versions: Next.js 16.2.0, React 19.2.4, FastAPI 0.135.1, Supabase 2.28.2, Resend 2.25.0.
- No new dependency is required for Story 5.5; prioritize correctness, auditability, and GDPR SLA observability.

### Project Context Reference

- `_bmad-output/project-context.md`

### References

- Epic source and AC: `_bmad-output/planning-artifacts/epics.md` (Epic 5, Story 5.5)
- PRD FR33 and compliance constraints: `_bmad-output/planning-artifacts/prd.md`
- Architecture constraints and process patterns: `_bmad-output/planning-artifacts/architecture.md`
- UX/legal continuity context: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Previous story context and implementation learnings: `_bmad-output/implementation-artifacts/5-4-automated-follow-up-email-sequence.md`
- Sprint tracker source: `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- `git log -n 5 --oneline`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`
- `_bmad-output/implementation-artifacts/5-4-automated-follow-up-email-sequence.md`
- `_bmad-output/project-context.md`

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Story context prepared for FR33-compliant, operations-first deletion request handling with explicit SLA and audit requirements.
- Sprint status transitioned from `backlog` to `ready-for-dev` for story `5-5-data-deletion-request-handling`.
- Implemented backend-only deletion workflow in `backend/app/services/data_deletion_service.py` with normalized email handling, deterministic deletion order, dry-run support, and explicit confirmation guard.
- Implemented operator CLI `backend/delete_user_data.py` with JSON structured output, validation errors, and table-level deletion counts.
- Added deletion regression and coverage tests for workflow service, CLI wrapper, and post-deletion auth behavior in `backend/tests/services/` and `backend/tests/routers/`.
- Replaced privacy placeholder with complete MVP policy sections and FR33 deletion SLA details in `frontend/app/privacy/page.tsx` + `frontend/lib/messages.ts`.
- Added operations runbook `docs/data-deletion-operations.md` with SLA guardrails, escalation policy, timestamp logging requirements, and exact Hungarian templates.
- Validation completed: `cd backend && pytest` (88 passed), `cd frontend && pnpm lint` (pass).
- Code review completed (claude-sonnet-4-6): 3-layer adversarial review (Blind Hunter, Edge Case Hunter, Acceptance Auditor).
- Applied code review patches: atomicity/error handling wrappers (_count_by/_delete_by helpers), P-2 waitlist cleanup for user_found=False path, P-4 RLS silent-block detection, P-5/P-11 dry-run refactored to count queries, P-6 confirm=args.confirm passthrough, P-7 select("token") removed, P-8 all Hungarian diacritics fixed in messages.ts, P-9 distinct CLI exit codes (1/2/3), P-10 double normalize removed.
- Added 3 new backend tests (waitlist cleanup when user not found, RLS block detection, CLI exit-3 on RuntimeError).
- Spec amendments: AC3 updated to include magic_link_tokens and waitlist tables; File Structure Requirements updated to test_auth_post_deletion.py.
- Post-patch validation: `cd backend && pytest` (91 passed), `cd frontend && pnpm lint` (pass).

### File List

- _bmad-output/implementation-artifacts/5-5-data-deletion-request-handling.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/services/data_deletion_service.py
- backend/delete_user_data.py
- backend/tests/services/test_data_deletion_service.py
- backend/tests/services/test_delete_user_data_cli.py
- backend/tests/routers/test_auth_post_deletion.py
- frontend/app/privacy/page.tsx
- frontend/lib/messages.ts
- docs/data-deletion-operations.md

### Change Log

- 2026-03-21: Implemented FR33 deletion workflow, operator CLI execution path, policy/runbook updates, and full automated regression coverage for post-deletion first-time-user behavior.
- 2026-03-21: Applied code review patches (P-1–P-11): error handling, atomicity guards, waitlist PII cleanup, RLS detection, dry-run count refactor, CLI exit codes, Hungarian diacritics. Spec updated (AC3, file structure). 91 tests passing.
