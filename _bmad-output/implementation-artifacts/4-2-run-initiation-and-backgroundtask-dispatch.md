# Story 4.2: Run Initiation & BackgroundTask Dispatch

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a verified user who has completed the qualifier,
I want my analysis to start immediately after I submit the qualifier,
so that I reach the waiting screen within 2 seconds and the persona engine begins processing.

## Acceptance Criteria

1. Given a user submits the qualifier survey, when the Server Action completes the `POST /api/v1/runs` + `POST /api/v1/qualifier` sequence, then qualifier responses are stored in `qualifier_responses` linked to the `user_id`.
2. Given a user submits the qualifier survey, when run creation is requested, then cost enforcement confirms monthly spend is below $50 before the run is created.
3. Given run creation is allowed, when persistence executes, then a new record is created in `runs` with `status: "queued"` and the submitted research `topic` + `audience`.
4. Given a run record exists, when dispatch logic executes, then a FastAPI `BackgroundTask` is enqueued for persona processing.
5. Given qualifier submission succeeds, when frontend navigation occurs, then user is redirected to `/waiting/[run_id]` within 2 seconds of submission (NFR2).
6. Given monthly cost cap is reached, when run creation is attempted, then endpoint returns HTTP 402 with `code: "COST_LIMIT_REACHED"`, user sees mapped Hungarian error, and no run record is created.

## Tasks / Subtasks

- [x] Implement backend run-creation contract with explicit payload and DB persistence (AC: 2, 3, 6)
  - [x] Add run request/response models in `backend/app/models/run.py` with `snake_case` fields (`user_id`, `topic`, `audience`) and strict validation (trimmed non-empty topic/audience).
  - [x] Expand `POST /api/v1/runs` in `backend/app/routers/runs.py` to accept payload and insert into `runs` table using service-role Supabase client.
  - [x] Return response including `run_id`, `status`, and `created_at` (ISO 8601), preserving existing error envelope rules.
  - [x] Keep all cost-cap behavior middleware-driven in `cost_enforcement.py`; do not duplicate cap checks in route logic.

- [x] Implement qualifier persistence endpoint aligned to existing schema constraints (AC: 1)
  - [x] Add qualifier request/response model in `backend/app/models/qualifier.py` using `run_id`, `user_id`, `role_answer`, `use_case_answer`.
  - [x] Add `POST /api/v1/qualifier` in `backend/app/routers/qualifier.py` that inserts into `qualifier_responses` (note `run_id` is NOT NULL).
  - [x] Register `qualifier.router` in `backend/app/main.py` and keep API prefix/version conventions.
  - [x] Reject malformed payloads with 422/Pydantic validation and keep business errors in `{ detail, code }` format.

- [x] Add BackgroundTask dispatch seam for persona engine kickoff (AC: 4)
  - [x] Introduce orchestration entrypoint (for example `backend/app/services/run_processor.py`) with callable invoked by FastAPI `BackgroundTasks`.
  - [x] Enqueue dispatch immediately after successful run creation; pass `run_id` and immutable run context only.
  - [x] Keep Story 4.2 scope to dispatch + status transition handoff; heavy persona execution logic remains Story 4.3.

- [x] Wire frontend qualifier submission to real backend flow and waiting route (AC: 1, 5, 6)
  - [x] Add Server Action (for example `frontend/app/actions/start-run.ts`) that calls `POST /api/v1/runs` then `POST /api/v1/qualifier` in a deterministic sequence.
  - [x] Update `frontend/app/qualifier/page.tsx` submit handler to call the new Server Action and navigate to `/waiting/[run_id]` on success (replace temporary `router.push("/waiting")`).
  - [x] Map `COST_LIMIT_REACHED` to `frontend/lib/errors.ts` message and display inline/full-screen per existing funnel pattern.
  - [x] Preserve strict `snake_case` API payloads and avoid exposing secrets in client components.

- [x] Preserve and pass submission context (`topic`, `audience`, `user_id`) end-to-end without reinvention (AC: 1, 3, 5)
  - [x] Reuse existing query-capture flow from `frontend/app/research/page.tsx`; do not synthesize placeholder topic/audience at qualifier step.
  - [x] Ensure qualifier screen receives/retains the original run context after magic-link verification (server-side handoff only).
  - [x] Document chosen handoff mechanism in code comments or story completion notes (cookie/session/token-bound payload), including anti-tampering rationale.

- [x] Add automated tests for run initiation, qualifier persistence, and redirect timing contract (AC: 1-6)
  - [x] Backend router tests: successful run insert, 402 cap block, no-row-created assertion on cap reached, qualifier insert with valid `run_id`, validation failures.
  - [x] Frontend tests: qualifier submit triggers action, error mapping on 402, successful navigation to `/waiting/[run_id]`.
  - [x] Keep tests in established locations (`backend/tests/routers/`, co-located frontend tests) and run full project checks.

## Dev Notes

- Story 4.1 intentionally stopped at UI + schema readiness. This story is the first end-to-end bridge from qualifier submission to actual run lifecycle.
- `qualifier_responses.run_id` is `NOT NULL` (`supabase/migrations/20260319004_qualifier_responses.sql`), so creation order is critical: create run first, then insert qualifier response.
- Current backend `POST /api/v1/runs` is a minimal stub returning only `{ "status": "queued" }`; this story upgrades it to production contract while preserving middleware-based cost enforcement.
- Current qualifier page redirects to `/waiting` without `run_id`; this must be replaced by canonical route `/waiting/[run_id]`.
- Keep user-visible text Hungarian via `frontend/lib/messages.ts`; do not hardcode new Hungarian strings in components.

### Architecture Compliance

- API prefix remains `/api/v1`; endpoint naming remains lowercase and `snake_case` payload fields.
- Cost cap enforcement remains centralized in `backend/app/core/cost_enforcement.py` and must continue to protect `POST /api/v1/runs`.
- Run status values must remain canonical: `queued`, `running`, `composing`, `completed`, `partial`, `failed`.
- No direct Supabase usage from frontend; all persistence stays behind FastAPI routes.

### Library / Framework Requirements

- Backend: FastAPI 0.135.1, Pydantic v2, Supabase Python client, FastAPI `BackgroundTasks`.
- Frontend: Next.js 16.2 App Router, Server Actions for server-side API orchestration.
- Testing: pytest (backend), Vitest + React Testing Library (frontend).

### File Structure Requirements

- Backend routes/models:
  - `backend/app/routers/runs.py`
  - `backend/app/routers/qualifier.py` (new)
  - `backend/app/models/run.py` (new)
  - `backend/app/models/qualifier.py` (new)
  - `backend/app/main.py` (router registration)
- Backend service seam:
  - `backend/app/services/run_processor.py` (new dispatch entrypoint)
- Frontend wiring:
  - `frontend/app/qualifier/page.tsx`
  - `frontend/app/actions/start-run.ts` (new)
  - `frontend/lib/errors.ts` (if new API error codes are introduced)

### Testing Requirements

- Backend: `cd backend && pytest`
- Frontend: `cd frontend && pnpm test && pnpm lint && pnpm exec tsc --noEmit`
- Optional integration check (if local infra available): create run + qualifier flow against local Supabase with middleware enabled.

### Previous Story Intelligence (4.1)

- Keep the refined blur-validation behavior in qualifier UI (`setTimeout + document.activeElement` and ref-backed values); avoid regressions while wiring submit.
- Reuse existing qualifier option payload shape (`role_answer`, `use_case_answer`) exactly as already scaffolded in `frontend/app/qualifier/page.tsx`.
- Maintain single-action funnel behavior and deterministic redirect pattern from prior stories.

### Git Intelligence Summary

- Recent commits show strict story hygiene: implementation + test updates + sprint-status transitions in lockstep.
- Story 4.1 introduced qualifier UI and migrations, but backend qualifier route and run payload model are not yet implemented; Story 4.2 should fill this gap instead of refactoring unrelated flows.
- Recent review patches focused on edge-case robustness and cross-browser behavior; apply the same rigor to request ordering, idempotency, and error mapping here.

### Latest Tech Information

- Use project-pinned versions and rules from `_bmad-output/project-context.md`.
- FastAPI `BackgroundTasks` is acceptable for MVP dispatch; queue migration (ARQ/Celery) is explicitly deferred by architecture.
- Keep TanStack polling concerns out of this story except for redirect target correctness; polling UI belongs to Story 4.5.

### Project Context Reference

- Follow `_bmad-output/project-context.md` for strict TypeScript/Python rules, naming, API contracts, test layout, and anti-pattern bans.

### References

- Epic source and AC: `_bmad-output/planning-artifacts/epics.md` (Epic 4, Story 4.2)
- PRD requirements: `_bmad-output/planning-artifacts/prd.md` (FR11, FR25, NFR2, NFR16)
- Architecture async + middleware patterns: `_bmad-output/planning-artifacts/architecture.md`
- UX waiting-state and funnel continuity requirements: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Prior story and handoff notes: `_bmad-output/implementation-artifacts/4-1-qualifier-survey-screen.md`
- Project guardrails: `_bmad-output/project-context.md`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- `git log -5 --pretty=format:'%h %ad %s' --date=short`
- `git log -5 --name-only --pretty=format:'--- %h %s'`

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Implemented typed `POST /api/v1/runs` + `POST /api/v1/qualifier` persistence with strict validation and middleware-only cost-cap enforcement.
- Added Story 4.2 dispatch seam (`run_processor.dispatch_run_processing`) and validated BackgroundTask enqueue via router tests.
- Replaced qualifier stub submit with server action orchestration and dynamic redirect to `/waiting/[run_id]`.
- Introduced server-side handoff cookies for `topic`/`audience` and verified user identity (`swarmsense_run_context`, `swarmsense_verified_user`) so run context is not trusted from client payloads.
- Added backend and frontend automated tests for success path, 402 cost limit mapping, validation failures, deterministic call sequence, and qualifier redirect behavior.

### File List

- _bmad-output/implementation-artifacts/4-2-run-initiation-and-backgroundtask-dispatch.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/main.py
- backend/app/models/qualifier.py
- backend/app/models/run.py
- backend/app/routers/qualifier.py
- backend/app/routers/runs.py
- backend/app/services/run_processor.py
- backend/tests/routers/test_runs.py
- frontend/app/actions/start-run.test.ts
- frontend/app/actions/start-run.ts
- frontend/app/actions/submit-run.ts
- frontend/app/actions/verify-token.test.ts
- frontend/app/actions/verify-token.ts
- frontend/app/qualifier/page.test.tsx
- frontend/app/qualifier/page.tsx
- frontend/app/research/page.tsx
- frontend/app/verify/page.test.tsx
- frontend/app/verify/verify-client.tsx
- frontend/lib/errors.ts

### Change Log

- 2026-03-21: Implemented Story 4.2 end-to-end run initiation and qualifier persistence flow; added dispatch seam, server-side run context handoff, and test coverage updates for backend/frontend.
