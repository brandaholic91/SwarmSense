# Story 5.4: Automated Follow-up Email Sequence

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As the system,
I want to send a 3-email follow-up sequence at day 1, day 3, and day 7 after result delivery,
so that verified users who have not joined the Pro waitlist are re-engaged with value-focused messaging.

## Acceptance Criteria

1. Given the FastAPI backend is running, when `POST /api/v1/operator/send-followups` is called with a valid `SWARMSENSE_OPERATOR_API_KEY` Bearer token, then the endpoint queries `runs` for records where `completed_at < now() - interval '1 day'` and `day1_sent = false` (and equivalent filters for day3/day7).
2. Given eligible runs are found, when follow-up dispatch is executed, then `email_service.py` sends the corresponding day-1/day-3/day-7 follow-up via Resend only for users where `unsubscribed_at IS NULL`.
3. Given a follow-up email send succeeds, when post-send persistence runs, then the corresponding `dayN_sent` boolean flag is updated to `true` exactly once.
4. Given the endpoint completes processing, when it returns, then response is HTTP 200 with payload `{"sent": N}` where `N` is the number of successfully dispatched emails.
5. Given the Bearer token is missing or invalid, when the endpoint is called, then response is HTTP 403.
6. Given pg_cron runs daily and calls `POST /api/v1/operator/send-followups` with valid auth, when a run crosses the day-1/day-3/day-7 threshold and the matching sent flag is still false, then the follow-up for that threshold is sent and tracked (FR22).
7. Given any follow-up email is delivered, when the user reads the footer, then a functional unsubscribe link is present (FR23).
8. Given a user activates unsubscribe, when `POST /api/v1/unsubscribe` processes the request, then `users.unsubscribed_at` is set and the user receives no further follow-up emails (FR24).

## Tasks / Subtasks

- [ ] Implement authenticated operator follow-up dispatcher endpoint (AC: 1, 4, 5, 6)
  - [ ] Add/confirm `POST /api/v1/operator/send-followups` in `backend/app/routers/operator.py` with `Security(HTTPBearer())` and static key validation against `SWARMSENSE_OPERATOR_API_KEY`.
  - [ ] Build deterministic threshold selection logic for day1/day3/day7 windows using canonical run fields: `completed_at`, `day1_sent`, `day3_sent`, `day7_sent`.
  - [ ] Return contract payload `{"sent": N}` in `snake_case` style and preserve FastAPI error envelope for auth failures.
  - [ ] Ensure idempotent behavior on repeated cron invocations (already-sent runs must not be resent).

- [ ] Implement follow-up candidate query + dispatch orchestration in service layer (AC: 1, 2, 3, 6)
  - [ ] Add/extend service logic in `backend/app/services/email_service.py` (or dedicated helper) to fetch eligible runs per day threshold from Supabase.
  - [ ] Resolve recipient user records and hard-gate sends with `unsubscribed_at IS NULL` before any Resend call.
  - [ ] Map threshold to the proper template contract (`follow-up-day1.tsx`, `follow-up-day3.tsx`, `follow-up-day7.tsx`) via the existing frontend render path used in Story 5.3.
  - [ ] Persist `dayN_sent = true` only after confirmed provider send success; keep failures unsent for next retry window.

- [ ] Implement unsubscribe processing endpoint and footer wiring checks (AC: 7, 8)
  - [ ] Add/confirm `POST /api/v1/unsubscribe` route (if missing) to set `users.unsubscribed_at = now()` by validated user identity payload.
  - [ ] Ensure follow-up email templates include one functional unsubscribe link pointing to the unsubscribe action flow.
  - [ ] Keep unsubscribe handling idempotent and safe for repeated clicks.

- [ ] Add cron integration guardrails and operational observability (AC: 6)
  - [ ] Document/verify Supabase `pg_cron` schedule and secured HTTP call configuration for daily execution.
  - [ ] Add structured logging/Sentry context for send attempts, successes, skips (unsubscribed), and provider failures with timestamps.
  - [ ] Ensure operator endpoint remains non-public without valid Bearer token.

- [ ] Add comprehensive automated coverage (AC: 1-8)
  - [ ] Backend router tests for `POST /api/v1/operator/send-followups`: valid token, invalid token (403), and response schema `{"sent": N}`.
  - [ ] Backend service tests for day-threshold eligibility, idempotency, `unsubscribed_at` suppression, and `dayN_sent` update-on-success only.
  - [ ] Backend tests for unsubscribe endpoint behavior and post-unsubscribe no-send guarantee.
  - [ ] Frontend email template tests ensuring unsubscribe link presence in all three follow-up templates.

## Dev Notes

- Story 5.3 established the backend-to-frontend React Email rendering contract (`frontend/app/api/emails/render-result/route.ts`) and hardened provider error metadata extraction. Reuse this path; do not reintroduce ad-hoc HTML builders.
- Follow-up scheduling architecture is explicitly defined as Supabase `pg_cron` + protected operator endpoint, not FastAPI `BackgroundTasks` delayed jobs.
- Marketing-email compliance boundary is strict: every follow-up send must enforce `unsubscribed_at IS NULL` before dispatch.
- Keep all API contracts in `snake_case`, and preserve canonical run status values without adding new status strings.

### Architecture Compliance

- Backend ownership: follow-up dispatch logic in `backend/app/services/email_service.py` and operator route surface in `backend/app/routers/operator.py`.
- Email templates remain in `frontend/emails/` with inline CSS and shared tokens from `frontend/lib/tokens.ts`.
- Auth on operator routes uses HTTP Bearer with `SWARMSENSE_OPERATOR_API_KEY`; never expose this secret to browser code.
- DB update contract uses existing `runs` boolean tracking columns (`day1_sent`, `day3_sent`, `day7_sent`) and `users.unsubscribed_at`.

### Library / Framework Requirements

- Backend: FastAPI 0.135.1 + Supabase Python client + Resend SDK.
- Frontend email: React Email templates rendered via existing server-side route integration pattern.
- Testing: pytest for backend; Vitest + RTL for frontend email templates.

### File Structure Requirements

- Primary backend targets:
  - `backend/app/routers/operator.py`
  - `backend/app/routers/unsubscribe.py` (or existing router location)
  - `backend/app/services/email_service.py`
  - `backend/app/services/run_processor.py` (only if orchestration hooks require extension)
- Primary frontend targets:
  - `frontend/emails/follow-up-day1.tsx`
  - `frontend/emails/follow-up-day3.tsx`
  - `frontend/emails/follow-up-day7.tsx`
- Test targets:
  - `backend/tests/routers/test_operator.py`
  - `backend/tests/routers/test_unsubscribe.py` (or existing router test file)
  - `backend/tests/services/test_email_service.py`
  - `frontend/emails/follow-up-day1.test.tsx`
  - `frontend/emails/follow-up-day3.test.tsx`
  - `frontend/emails/follow-up-day7.test.tsx`

### Testing Requirements

- Backend:
  - `cd backend && pytest`
  - Validate auth gating, threshold eligibility, idempotency, unsubscribe suppression, and sent-flag persistence behavior.
- Frontend:
  - `cd frontend && pnpm test -- --run`
  - Validate unsubscribe link/footer content in all follow-up templates.
- Quality gates:
  - `cd frontend && pnpm lint`
  - Ensure no regression in Story 5.1-5.3 result-email behavior.

### Previous Story Intelligence (5.3)

- Reuse the frontend render API contract pattern introduced by Story 5.3 for email HTML generation.
- Keep provider failure telemetry explicit (`error_code` / `code` / `status_code`) and include timestamp + context to preserve debuggability.
- Preserve deterministic payload mapping and avoid drifting template contracts between backend and frontend.
- Account for deferred Story 5.3 item: CTA URL parameterization consistency should remain explicit when wiring follow-up links.

### Git Intelligence Summary

- Recent Epic 5 cadence is stable: story context -> implementation -> code review patching -> status transition. Keep this hygiene for 5.4.
- Recent hotspot files are concentrated in `backend/app/services/*`, `backend/tests/services/*`, `frontend/emails/*`, and sprint/story artifact files.
- Follow-up implementation should remain localized to operator routing, email service orchestration, and follow-up templates/tests to reduce regression risk.

### Latest Tech Information

- Project context pins: Next.js 16.2.0, React 19.2.4, FastAPI 0.135.1, Supabase 2.28.2, Resend 2.25.0.
- No new dependency is required for Story 5.4; prioritize contract correctness, idempotency, and compliance behavior.

### Project Context Reference

- `_bmad-output/project-context.md`

### References

- Epic source and AC: `_bmad-output/planning-artifacts/epics.md` (Epic 5, Story 5.4)
- Architecture scheduling/auth/compliance: `_bmad-output/planning-artifacts/architecture.md` (Gaps resolved: follow-up scheduling, operator endpoint auth, unsubscribe storage)
- UX lifecycle and communication constraints: `_bmad-output/planning-artifacts/ux-design-specification.md` (user communication continuity, single-CTA clarity)
- Prior story context: `_bmad-output/implementation-artifacts/5-3-result-email-reflection-question-cta-and-delivery.md`
- Sprint tracker source: `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- `git log --oneline -n 8`
- `git log --name-only --pretty=format:'%h %s' -n 5`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/implementation-artifacts/5-3-result-email-reflection-question-cta-and-delivery.md`

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

- _bmad-output/implementation-artifacts/5-4-automated-follow-up-email-sequence.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
