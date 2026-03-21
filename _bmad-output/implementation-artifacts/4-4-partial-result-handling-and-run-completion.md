# Story 4.4: Partial Result Handling & Run Completion

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As the system,
I want to deliver results gracefully when some personas time out,
so that users receive value even when the full 15-20 persona set is not available.

## Acceptance Criteria

1. Given the persona engine has completed execution, when between 12 and 19 personas responded successfully (1-8 failed), then the run status is set to `partial` and `persona_count` is updated with the actual completed count.
2. Given the persona engine has completed execution with partial success, when finalization runs, then the result is passed to `run_processor.py` aggregation with the actual count preserved.
3. Given partial completion, when the result email is prepared for dispatch, then the email includes persona count in `"{completed}/{total} persona"` format in the header (FR12).
4. Given all 15-20 personas responded successfully, when run processor aggregation completes, then the run status is set to `completed` and `persona_count` is updated.
5. Given a run reaches `completed` from full success, when finalization is written to storage, then `completed_at` is set to current timestamp and result email delivery starts.
6. Given any run reaches a final status (`completed`/`partial`/`failed`), when final bookkeeping executes, then `cost_usd` is recorded with actual LLM API cost for that run.
7. Given `cost_usd` is recorded for a finalized run, when monthly accounting updates, then `cost_tracking.total_usd` for current month is incremented by the run cost.

## Tasks / Subtasks

- [x] Implement run finalization state machine in `run_processor.py` (AC: 1, 2, 4, 5)
  - [x] Extend the current `process_run` composing handoff to branch: `partial` for 12-19 successes, `completed` for full success, `failed` remains unchanged for `<12`.
  - [x] Persist `persona_count` on both `partial` and `completed` transitions using canonical run status values only.
  - [x] Set `completed_at` only when run reaches final status (`completed`, `partial`, or `failed`) and keep timestamp format ISO 8601.
  - [x] Keep current failure telemetry behavior (`PERSONA_SUCCESS_THRESHOLD_NOT_MET`, `RUN_PROCESSING_UNHANDLED`) intact; add only missing tags/metadata required for partial/completed observability.

- [x] Add deterministic result aggregation and payload contract for downstream email composition (AC: 2, 3)
  - [x] Add/extend aggregation logic to produce a normalized result payload from persona outputs (`support`/`reject`/`conditional` counts, top arguments, persona list for email).
  - [x] Ensure persona count string formatting is centralized and reused as `"{completed}/{total} persona"`.
  - [x] Keep all user-facing Hungarian strings out of backend business logic; only structural payload values belong in backend aggregation.

- [x] Wire run completion to email dispatch boundary without breaking Story 5 ownership (AC: 3, 5)
  - [x] Introduce a result-email dispatch seam in `email_service.py` (or dedicated helper) that accepts run-level payload from `run_processor.py`.
  - [x] Trigger dispatch for both `partial` and `completed`; do not dispatch for `failed`.
  - [x] Keep implementation compatible with current magic-link email path and existing Resend settings usage.
  - [x] If email dispatch fails at this stage, capture the error with Sentry and leave run final status unchanged (email retry sophistication belongs to Epic 5 stories).

- [x] Implement cost finalization and monthly counter update (AC: 6, 7)
  - [x] Add run-level cost computation output from persona execution path and persist into `runs.cost_usd` during finalization.
  - [x] Add monthly `cost_tracking` increment logic keyed by `YYYY-MM`, creating month row if absent before increment.
  - [x] Ensure cost update runs for all final states (`completed`, `partial`, `failed`) and is not skipped when partial results are delivered.
  - [x] Capture and surface bookkeeping failures in Sentry with machine-readable error codes; avoid silent failures.

- [x] Add/extend automated tests for partial/completed and cost bookkeeping semantics (AC: 1-7)
  - [x] Extend `backend/tests/services/test_run_processor.py` with cases for 12-19 success (`partial`) and full success (`completed`) transitions.
  - [x] Assert `completed_at`, `persona_count`, and `cost_usd` persistence behavior for final statuses.
  - [x] Add tests for monthly `cost_tracking` increment semantics, including missing-month row creation.
  - [x] Add dispatch-boundary tests that verify result email dispatch attempts for `partial` and `completed`, and no dispatch for `failed`.

## Dev Notes

- Story 4.3 already implemented persona orchestration, retry behavior, and `<12` hard failure threshold. Story 4.4 must start from the current `composing` boundary and complete finalization semantics without regressing 4.3 behavior.
- Keep architecture rule: canonical run status enum is fixed (`queued`, `running`, `composing`, `completed`, `partial`, `failed`), and waiting screen polling logic in Epic 4.5 depends on these exact values.
- Do not move DB access into frontend or Server Actions for this story; all finalization and accounting logic stays backend-side.
- Keep run completion idempotent where practical: avoid double-incrementing monthly cost if a background execution path retries after partial failure.

### Architecture Compliance

- Async execution remains FastAPI `BackgroundTasks` in MVP (no ARQ/Celery migration in this story).
- API contracts for run creation and qualifier submission remain unchanged; this story is service-layer completion logic.
- Error envelope convention remains `{ "detail": "...", "code": "..." }` for API-facing failures.
- Data isolation, `snake_case` payloads, and `SWARMSENSE_*` env-var discipline remain mandatory.

### Library / Framework Requirements

- Backend: FastAPI 0.135.1, Python 3.12+, Pydantic v2.
- Persona execution: `asyncio.gather` + `asyncio.Semaphore` from Story 4.3 remains authoritative.
- Telemetry: Sentry for exception/error-code capture on finalization and bookkeeping failures.
- Email transport: Resend integration in `email_service.py`.

### File Structure Requirements

- Primary updates:
  - `backend/app/services/run_processor.py`
  - `backend/app/services/email_service.py`
  - `backend/app/models/run.py` (only if response/status typing needs extension)
- Potential new service helper (if required for clean separation):
  - `backend/app/services/cost_tracker.py`
- Test updates:
  - `backend/tests/services/test_run_processor.py`
  - `backend/tests/services/test_email_service.py` (if new result-dispatch seam is introduced)

### Testing Requirements

- Focused backend tests before full regression:
  - `cd backend && pytest tests/services/test_run_processor.py`
  - `cd backend && pytest tests/services/test_email_service.py` (if created)
- Full backend suite:
  - `cd backend && pytest`
- Validate no regression in status transitions expected by waiting UX flow (`queued` -> `running` -> `composing` -> `partial|completed|failed`).

### Previous Story Intelligence (4.3)

- Reuse the existing result handoff contract from `execute_persona_engine` (`responses`, `failures`, `handoff_payload`) rather than re-querying persona artifacts from storage.
- Preserve DB update helper patterns and Sentry tagging style already introduced in `run_processor.py`.
- Keep the separation of concerns: persona generation remains in `persona_engine.py`; run lifecycle, aggregation, email dispatch orchestration, and accounting belong in `run_processor.py` and supporting services.

### Git Intelligence Summary

- Recent commit pattern for Epic 4: implement service-layer core in one commit, apply code-review hardening in a follow-up commit, then mark story done.
- Files most likely to receive Story 4.4 changes based on Story 4.3 history: `run_processor.py`, `email_service.py`, service tests.
- Prior review emphasis was on edge-case handling and defensive error paths; this story should proactively include idempotency and bookkeeping-failure tests.

### Latest Tech Information

- Keep implementation aligned with project-pinned stack in `_bmad-output/project-context.md` (FastAPI 0.135.1, Python 3.12+, Resend 2.25.0, Sentry SDK 2.20.0).
- Continue using OpenRouter-routed execution path from Story 4.3; do not introduce provider-specific branching into finalization logic.
- Preserve token-efficient, unambiguous status naming and payload shape for downstream Epic 4.5 and Epic 5 stories.

### Project Context Reference

- Follow `_bmad-output/project-context.md` for strict naming, API boundary, env-var handling, and anti-pattern guardrails.

### References

- Epic source and AC: `_bmad-output/planning-artifacts/epics.md` (Epic 4, Story 4.4)
- FR/NFR source: `_bmad-output/planning-artifacts/prd.md` (FR12, FR14, NFR4, NFR5, NFR13)
- Architecture run-status + graceful degradation rules: `_bmad-output/planning-artifacts/architecture.md`
- UX waiting/result continuity + persona count format: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Prior handoff context: `_bmad-output/implementation-artifacts/4-3-persona-engine-parallel-llm-execution.md`
- Project-wide guardrails: `_bmad-output/project-context.md`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- `git log --oneline -5`
- `git show --name-only --pretty=format:'%h %s' 2dcdd47 13d1a70`
- `cd backend && pytest tests/services/test_run_processor.py tests/services/test_persona_engine.py tests/services/test_llm_client.py`
- `cd backend && pytest`

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Implemented story-complete run finalization in `backend/app/services/run_processor.py` with canonical transitions: `<12` -> `failed`, `12..(total-1)` -> `partial`, `total` -> `completed`, and ISO 8601 `completed_at` persisted only on final states.
- Added deterministic aggregation payload contract in `run_processor.py` (`stance_counts`, `top_arguments`, `personas`, `persona_count_label`) and centralized `"{completed}/{total} persona"` formatting.
- Introduced result email dispatch seam in `backend/app/services/email_service.py` (`send_run_result_email`) and wired dispatch attempts for `partial`/`completed` only, with Sentry error capture that preserves final run status on dispatch failure.
- Added cost finalization pipeline: propagated run-level `cost_usd` from persona execution (`backend/app/services/persona_engine.py`, `backend/app/services/llm_client.py`) into `runs.cost_usd`, plus monthly `cost_tracking` increment/create-by-month logic with Sentry failure telemetry.
- Extended `backend/tests/services/test_run_processor.py` to cover partial/completed transitions, final-state persistence (`completed_at`, `persona_count`, `cost_usd`), monthly bookkeeping (including missing month row), and dispatch boundary behavior.
- Full backend regression green: `52 passed`.

### File List

- _bmad-output/implementation-artifacts/4-4-partial-result-handling-and-run-completion.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/models/persona.py
- backend/app/services/email_service.py
- backend/app/services/llm_client.py
- backend/app/services/persona_engine.py
- backend/app/services/run_processor.py
- backend/tests/services/test_run_processor.py

### Change Log

- 2026-03-21: Implemented Story 4.4 run completion pipeline (partial/completed state machine, deterministic aggregation payload, result-email dispatch seam, run/monthly cost finalization, and comprehensive service tests); status moved to review.
