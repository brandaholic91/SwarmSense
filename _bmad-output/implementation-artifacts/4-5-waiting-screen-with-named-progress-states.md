# Story 4.5: Waiting Screen with Named Progress States

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user waiting for my analysis,
I want to see specific, named progress states and a persona counter during the 90-second wait,
so that I feel anticipation rather than anxiety and understand that my result will arrive by email.

## Acceptance Criteria

1. Given a user arrives at `/waiting/[run_id]`, when the waiting UI renders, then TanStack Query polls `GET /api/v1/runs/{run_id}/status` every 5 seconds (FR25).
2. Given status polling is active, when backend statuses change, then the UI maps states to Hungarian labels: `queued` -> "Sorban...", `running` -> "Futtatas: [N]/[total] persona", `composing` -> "Eredmeny osszeallitasa...", `completed|partial` -> completion state.
3. Given the screen is mounted before first meaningful progress payload, when UI is waiting for first `running`/`composing` response, then a transient frontend-only `generating` state ("Personak generalasa...") may be shown and must never be persisted or returned by API.
4. Given status is `running`, when progress is displayed, then a large numeric persona counter is visually dominant and reflects live progress values from status payload.
5. Given waiting screen is visible, when user reads contextual copy, then email delivery notice is shown: "Az eredmenyed erre az emailre erkezik: [email]".
6. Given progress messaging updates, when assistive technology is used, then progress label uses `aria-live="polite"` and visual progress indicator uses `role="progressbar"` with valid `aria-valuenow`.
7. Given processing exceeds 120 seconds without final status, when elapsed time crosses threshold, then delayed Hungarian notice appears indicating processing is still running (FR25).
8. Given run reaches `completed`, `partial`, or `failed`, when final status is received, then polling stops automatically; and for `failed`, a Hungarian error with retry suggestion is shown.

## Tasks / Subtasks

- [x] Add run status read endpoint with polling-safe response contract (AC: 1, 2, 4, 8)
  - [x] Add `GET /api/v1/runs/{run_id}/status` in `backend/app/routers/runs.py` using canonical status values only.
  - [x] Add response model(s) in `backend/app/models/run.py` (or a dedicated model file) including `run_id`, `status`, `persona_count`, `total_personas`, and timestamp field if needed.
  - [x] Return `total_personas` from backend consistently (current engine default is 18) so frontend can render `[N]/[total]` without hardcoding.
  - [x] Keep response/error shape aligned with project conventions (`snake_case`, structured errors).

- [x] Expose live persona progress during `running` state (AC: 2, 4)
  - [x] Extend persona execution flow to surface per-persona completion counts while status is `running`.
  - [x] Update `runs.persona_count` incrementally during `running` to support real progress display (without introducing non-canonical run statuses).
  - [x] Preserve existing finalization semantics from Story 4.4 (`queued -> running -> composing -> completed|partial|failed`).

- [x] Implement waiting route and screen component (AC: 1, 2, 3, 4, 6, 7, 8)
  - [x] Create `frontend/app/waiting/[run_id]/page.tsx` and `frontend/components/waiting-screen.tsx`.
  - [x] Add TanStack Query dependency and local/provider setup needed for polling every 5000ms.
  - [x] Implement deterministic state mapping from backend run status + transient UI-only `generating` state.
  - [x] Render dominant numeric counter for `running` and handle final states (`completed`, `partial`, `failed`).
  - [x] Stop polling automatically on final status (`completed|partial|failed`) per architecture rule.

- [x] Add email notice and accessibility semantics (AC: 5, 6)
  - [x] Reuse Hungarian strings from `frontend/lib/messages.ts` only; no hardcoded user-facing copy in component.
  - [x] Ensure waiting UI has `aria-live="polite"` progress text and `role="progressbar"` with bounded `aria-valuenow`.
  - [x] Source user email for notice from safe existing flow context (cookie/session-derived), not by introducing unnecessary PII exposure in public status API.

- [x] Implement delayed-notice and failed-state UX handling (AC: 7, 8)
  - [x] Trigger delayed notice client-side when elapsed waiting time exceeds 120s and run not final.
  - [x] On `failed`, show Hungarian failure message with retry guidance and keep one primary action pattern.

- [x] Add tests for backend + frontend waiting flow (AC: 1-8)
  - [x] Backend router tests for status endpoint shape and canonical status handling.
  - [x] Backend service tests validating `running` progress updates do not break Story 4.4 completion/cost logic.
  - [x] Frontend tests for state mapping, polling-stop behavior on final status, delayed notice timing, and accessibility attributes.

## Dev Notes

- Story 4.4 already finalized run lifecycle and cost bookkeeping. Story 4.5 must build on that flow without introducing new backend status strings.
- `generating` is UI-only and must never appear in DB/API payloads. Canonical backend statuses remain: `queued`, `running`, `composing`, `completed`, `partial`, `failed`.
- The waiting route does not exist yet in `frontend/app/`; this story introduces it.
- Current frontend dependencies do not include TanStack Query; add it deliberately and keep usage narrow to waiting/status polling.

### Architecture Compliance

- Keep global API prefix `/api/v1` and `snake_case` payload fields.
- Keep polling implementation with TanStack Query `refetchInterval: 5000`; do not introduce custom polling loops.
- Keep all user-facing Hungarian strings in `frontend/lib/messages.ts`.
- Keep Supabase access backend-only; frontend communicates through API endpoints/Server Actions.

### Library / Framework Requirements

- Frontend: Next.js 16.2.0, React 19.2.4, TypeScript strict.
- Polling/state: `@tanstack/react-query` for waiting screen server-state polling.
- Backend: FastAPI 0.135.1, Pydantic v2 response models for run status payload.
- Continue using existing run processor/persona engine architecture; no queue-system migration in this story.

### File Structure Requirements

- Expected backend touch points:
  - `backend/app/routers/runs.py`
  - `backend/app/models/run.py` (or new status model file)
  - `backend/app/services/run_processor.py`
  - `backend/app/services/persona_engine.py`

- Expected frontend touch points:
  - `frontend/app/waiting/[run_id]/page.tsx` (new)
  - `frontend/components/waiting-screen.tsx` (new)
  - `frontend/lib/messages.ts`
  - `frontend/package.json`

- Expected tests:
  - `backend/tests/routers/test_runs.py`
  - `backend/tests/services/test_run_processor.py`
  - `frontend/components/waiting-screen.test.tsx` (new)

### Testing Requirements

- Backend targeted tests:
  - `cd backend && pytest tests/routers/test_runs.py`
  - `cd backend && pytest tests/services/test_run_processor.py`
- Frontend targeted tests:
  - `cd frontend && pnpm test`
- Regression confidence:
  - `cd backend && pytest`

### Previous Story Intelligence (4.4)

- Reuse Story 4.4 finalization contract and keep cost tracking idempotency guards intact.
- Do not regress result email dispatch behavior for `completed`/`partial` paths.
- Keep failure capture semantics and Sentry tagging style introduced in `run_processor.py`.

### Git Intelligence Summary

- Recent Epic 4 pattern: story context -> implementation -> code review hardening -> status to done.
- Files repeatedly touched in latest Epic 4 stories: `run_processor.py`, `persona_engine.py`, `email_service.py`, `test_run_processor.py`, and sprint status.
- Review trend: edge-case handling and defensive state transitions are scrutinized; include explicit tests for polling stop and state mapping boundaries.

### Latest Tech Information

- Project-pinned stack from `_bmad-output/project-context.md` remains authoritative for this story (Next.js 16.2.0, React 19.2.4, FastAPI 0.135.1).
- Introduce TanStack Query in current stable version compatible with React 19 and Next.js 16; keep API usage minimal (`useQuery`, `refetchInterval`, conditional polling stop).

### Project Context Reference

- Follow `_bmad-output/project-context.md` for strict naming, status enum, polling rules, and anti-pattern guardrails.

### References

- Epic source and AC: `_bmad-output/planning-artifacts/epics.md` (Epic 4, Story 4.5)
- FR source: `_bmad-output/planning-artifacts/prd.md` (FR25)
- Architecture polling/status rules: `_bmad-output/planning-artifacts/architecture.md`
- UX waiting-state and accessibility requirements: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Previous story context: `_bmad-output/implementation-artifacts/4-4-partial-result-handling-and-run-completion.md`
- Project guardrails: `_bmad-output/project-context.md`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- `git log --oneline -5`
- `git show --name-only --pretty=format:'%h %s' HEAD~4..HEAD`

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Story context includes backend status endpoint, live progress tracking strategy, waiting-screen UX mapping, accessibility constraints, and test coverage guardrails.
- Added `GET /api/v1/runs/{run_id}/status` with canonical status validation, snake_case payload, `total_personas`, and structured `RUN_NOT_FOUND` response code.
- Extended persona execution + run processing pipeline to publish incremental `running` progress updates (`persona_count`) while preserving Story 4.4 finalization + cost tracking semantics.
- Implemented waiting route and client UI with TanStack Query polling (`5000ms`), transient UI-only `generating` state, final-state polling stop, delayed-notice handling, and failed-state retry UX.
- Added secure email handoff via HTTP-only `swarmsense_result_email` cookie and rendered delivery notice from waiting page server context without exposing email in public status API.
- Added/updated backend and frontend tests; executed `pytest tests/routers/test_runs.py tests/services/test_run_processor.py`, full `pytest`, and full `pnpm test` (all green).

### File List

- _bmad-output/implementation-artifacts/4-5-waiting-screen-with-named-progress-states.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/core/errors.py
- backend/app/models/run.py
- backend/app/routers/runs.py
- backend/app/services/persona_engine.py
- backend/app/services/run_processor.py
- backend/tests/routers/test_runs.py
- backend/tests/services/test_run_processor.py
- frontend/app/actions/submit-run.ts
- frontend/app/waiting/[run_id]/page.tsx
- frontend/components/waiting-screen.tsx
- frontend/components/waiting-screen.test.tsx
- frontend/lib/messages.ts
- frontend/package.json
- frontend/pnpm-lock.yaml

### Change Log

- 2026-03-21: Implemented Story 4.5 waiting screen end-to-end (backend status endpoint, live progress updates, waiting UI polling/state mapping/accessibility, and test coverage).
- 2026-03-21: Code review (claude-sonnet-4-6) — applied 11 patches: persona_count float coercion fix, apiBaseUrl empty-string guard, asyncio.to_thread for blocking DB callback, buildUiState explicit branches, as_completed task cancellation cleanup, retry:1, normalizedApiBaseUrl in queryKey, run_id length validation, RUN_STATUSES derived from get_args, aria-label on progressbar, hasShownNoticeRef for delayed notice. All tests green (58 backend, 56 frontend).
