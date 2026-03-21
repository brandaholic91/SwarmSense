# Story 4.3: Persona Engine - Parallel LLM Execution

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As the system,
I want to run 15-20 attitudinally distinct AI personas against the user's research query in parallel,
so that the analysis reflects genuine diversity of market perspectives rather than a single LLM response.

## Acceptance Criteria

1. Given a run has been dispatched as a BackgroundTask, when `persona_engine.py` executes, then 15-20 distinct personas are generated based on the five required dimensions: risk appetite, decision-making style, organizational role, price sensitivity, and technology adoption curve (FR10).
2. Given persona execution starts, when LLM calls are launched, then persona calls run in parallel via `asyncio.gather` and are capped with `asyncio.Semaphore` to control per-run concurrency (NFR19).
3. Given a persona LLM call executes, when provider routing is resolved, then calls are sent through OpenRouter via `llm_client.py`, using Kimi K2 (Moonshot AI) as the primary routed model.
4. Given a persona response completes successfully, when the payload is normalized, then each response includes: persona name, role, stance (`support`/`reject`/`conditional`), primary argument, and condition for changing mind.
5. Given persona prompts are built and dispatched, when request payloads are created, then prompts and instructions are Hungarian and explicitly enforce Hungarian market context (FR13).
6. Given persona dispatch begins, when the first persona call is launched, then run status transitions to `running`.
7. Given an OpenRouter call returns rate-limit (`429`) or transient upstream failure, when `llm_client.py` handles the failure, then exponential backoff retries up to 3 attempts before marking that persona as failed.
8. Given persona execution completes with fewer than 12 successful personas, when run finalization occurs for this story scope, then run status is `failed`, no result email is sent, and failure is captured in Sentry with error code + timestamp metadata (NFR13, NFR15).

## Tasks / Subtasks

- [x] Build the persona domain model and deterministic persona generation strategy (AC: 1, 4, 5)
  - [x] Create `backend/app/models/persona.py` with strict Pydantic v2 models for persona input/output and a `Literal` stance enum (`support`, `reject`, `conditional`).
  - [x] Implement deterministic persona blueprint generation in `backend/app/services/persona_engine.py` covering all five attitudinal dimensions and producing 15-20 unique persona profiles.
  - [x] Enforce output contract fields (`name`, `role`, `stance`, `primary_argument`, `change_condition`) and reject malformed provider output.
  - [x] Keep all prompt templates and Hungarian copy centralized (module constants/helpers), with explicit Hungarian cultural grounding instructions.

- [x] Implement LLM client abstraction with OpenRouter gateway and retry policy (AC: 3, 7)
  - [x] Add `backend/app/services/llm_client.py` with async call API used by persona engine.
  - [x] Route persona inference through OpenRouter Chat Completions (or Responses) API and set Kimi K2 as the default routed model.
  - [x] Read provider credentials only from `SWARMSENSE_` settings in `backend/app/core/config.py`; no direct `os.environ` usage (including `SWARMSENSE_OPENROUTER_API_KEY`).
  - [x] Add/update backend `.env.example` entries for OpenRouter configuration (`SWARMSENSE_OPENROUTER_API_KEY`, routed model id, optional base URL override if needed).
  - [x] Add provider-level handling for `429` with exponential backoff (max 3 attempts), classify final failures with machine-readable error codes.
  - [x] Structure client to allow future fallback provider wiring without changing persona engine orchestration contract.

- [x] Implement parallel persona execution orchestration and run state handoff (AC: 2, 6, 8)
  - [x] Replace Story 4.2 placeholder in `backend/app/services/run_processor.py` with orchestration that invokes persona engine.
  - [x] Update run to `running` before first dispatched persona call, preserving canonical status enum only.
  - [x] Execute persona calls with `asyncio.gather` and per-run `asyncio.Semaphore` cap; collect successes and structured failures.
  - [x] If successful persona count is `< 12`, update run to `failed`, persist failure metadata, and capture exception context in Sentry; do not send email.
  - [x] If successful persona count is `>= 12`, hand off normalized outputs to the next step boundary for Story 4.4 (partial/completed aggregation logic intentionally deferred).

- [x] Preserve architecture boundaries and avoid regression on Story 4.2 seams (AC: 1-8)
  - [x] Keep `POST /api/v1/runs` and `POST /api/v1/run-sessions` contracts unchanged; this story is backend async processing internals.
  - [x] Do not introduce new run status values beyond `queued`, `running`, `composing`, `completed`, `partial`, `failed`.
  - [x] Keep `snake_case` API/data model fields and existing error envelope conventions.
  - [x] Ensure no direct frontend/Supabase coupling is introduced; all DB writes remain backend-only.

- [x] Add comprehensive automated tests for concurrency, retry, and failure thresholds (AC: 1-8)
  - [x] Add `backend/tests/services/test_llm_client.py` for provider request shaping, 429 retry/backoff behavior, and terminal failure classification.
  - [x] Add `backend/tests/services/test_persona_engine.py` for persona generation uniqueness, Hungarian prompt requirements, and response schema normalization.
  - [x] Add `backend/tests/services/test_run_processor.py` for run lifecycle transitions (`queued` -> `running` -> failure boundary), `<12` failure behavior, and no-email guarantee on failure.
  - [x] Add focused integration-style test(s) for dispatch seam from `run_sessions.py`/`runs.py` into real run processor execution path using mocks/stubs.

## Dev Notes

- Story 4.2 already established the dispatch seam (`dispatch_run_processing`) and run/session creation contracts. Story 4.3 must implement processing internals without changing those API boundaries.
- Story 4.4 owns partial/completed aggregation and result assembly semantics. Story 4.3 should produce normalized persona outputs and clear handoff artifacts, but must not overreach into email composition logic.
- NFR19 risk is explicit in architecture: per-run concurrency must be capped with `asyncio.Semaphore` from day one.
- Keep Hungarian cultural relevance explicit in prompts, not implicit via provider defaults.
- OpenRouter is the transport layer; model selection logic should remain explicit and testable in `llm_client.py`.

### Architecture Compliance

- Async processing mechanism remains FastAPI `BackgroundTasks` (no ARQ/Celery in MVP).
- API prefix and endpoint naming stay unchanged (`/api/v1`, plural/kebab-case routes).
- Canonical run status values only: `queued`, `running`, `composing`, `completed`, `partial`, `failed`.
- Error handling remains structured `{ "detail": "...", "code": "..." }` for business errors.

### Library / Framework Requirements

- Backend stack: FastAPI 0.135.1, Pydantic v2, Python 3.12+.
- Async execution: `asyncio.gather` + `asyncio.Semaphore`.
- Observability: Sentry capture for unhandled/threshold failures.
- LLM transport/provider gateway: OpenRouter via `llm_client.py` abstraction.
- Primary routed model: Kimi K2 (Moonshot AI) through OpenRouter.

### File Structure Requirements

- Implement or update:
  - `backend/app/services/persona_engine.py` (new)
  - `backend/app/services/llm_client.py` (new)
  - `backend/app/services/run_processor.py` (replace placeholder)
  - `backend/app/models/persona.py` (new)
- Add tests:
  - `backend/tests/services/test_persona_engine.py` (new)
  - `backend/tests/services/test_llm_client.py` (new)
  - `backend/tests/services/test_run_processor.py` (new)

### Testing Requirements

- Backend test suite: `cd backend && pytest`
- Focused service verification before full suite:
  - `cd backend && pytest tests/services/test_llm_client.py tests/services/test_persona_engine.py tests/services/test_run_processor.py`

### Previous Story Intelligence (4.2)

- Reuse existing run dispatch seam from `runs.py` and `run_sessions.py`; do not redesign run creation flow.
- Preserve internal write protection (`X-Internal-Secret`) behavior on run-initiating endpoints.
- Maintain strict `snake_case` payload discipline and run-context handoff pattern established in Story 4.2.

### Git Intelligence Summary

- Recent commits show stable story flow: context file creation -> implementation -> code review patches -> status transitions.
- Story 4.2 delivered the orchestration seam but left heavy execution intentionally blank; Story 4.3 should fill exactly that gap with targeted service-layer work.
- Recent review patterns emphasize edge-case coverage; apply same rigor to retry, timeout, and threshold boundaries.

### Latest Tech Information

- Keep implementation pinned to project-approved versions from `_bmad-output/project-context.md`.
- FastAPI BackgroundTasks remains accepted MVP strategy; queue migration is intentionally deferred.
- Maintain provider abstraction in `llm_client.py` so fallback model/provider additions remain non-breaking in future stories.
- Ensure OpenRouter-specific request headers/metadata are encapsulated in `llm_client.py` and not leaked into persona engine orchestration.

### Project Context Reference

- Follow `_bmad-output/project-context.md` for strict naming, API boundary, environment-variable, and testing rules.

### References

- Epic source and AC: `_bmad-output/planning-artifacts/epics.md` (Epic 4, Story 4.3)
- PRD requirements: `_bmad-output/planning-artifacts/prd.md` (FR10-13, NFR13, NFR15, NFR19)
- Architecture async/concurrency patterns: `_bmad-output/planning-artifacts/architecture.md`
- UX continuity and waiting-state language: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Prior story handoff: `_bmad-output/implementation-artifacts/4-2-run-initiation-and-backgroundtask-dispatch.md`
- Global agent guardrails: `_bmad-output/project-context.md`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- `git log --oneline -5`
- `cd backend && pytest tests/services/test_llm_client.py tests/services/test_persona_engine.py tests/services/test_run_processor.py`
- `cd backend && pytest`

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Story status set to ready-for-dev with explicit implementation guardrails for persona concurrency, retry handling, and failure thresholds.
- Implemented full persona execution pipeline: deterministic 18-persona generation across all five attitudinal dimensions, Hungarian prompt contracts, strict schema normalization, and per-persona structured failures.
- Added OpenRouter client abstraction with Kimi K2 default routing, async transport, machine-readable provider failure codes, and 429/5xx/network retry handling with exponential backoff (3 attempts).
- Replaced Story 4.2 placeholder dispatch processor with real async orchestration: `running` transition before persona dispatch, `failed` threshold handling for `<12`, Sentry failure capture with error metadata, and `composing` handoff boundary for `>=12`.
- Added service-level test suite for llm client, persona engine, and run processor, including endpoint seam integration check through `/api/v1/runs` into real run processor dispatch path.
- Full backend regression green: `50 passed`.

### File List

- _bmad-output/implementation-artifacts/4-3-persona-engine-parallel-llm-execution.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/.env.example
- backend/app/core/config.py
- backend/app/models/persona.py
- backend/app/services/llm_client.py
- backend/app/services/persona_engine.py
- backend/app/services/run_processor.py
- backend/tests/services/__init__.py
- backend/tests/services/test_llm_client.py
- backend/tests/services/test_persona_engine.py
- backend/tests/services/test_run_processor.py
- backend/tests/routers/test_auth.py
- backend/tests/routers/test_run_sessions.py
- backend/tests/routers/test_runs.py
- backend/tests/routers/test_waitlist.py
- backend/tests/test_sentry.py

### Change Log

- 2026-03-21: Created Story 4.3 ready-for-dev context with architecture-compliant implementation guidance, previous-story intelligence, and service-level testing scope.
- 2026-03-21: Implemented Story 4.3 persona engine backend internals (modeling, OpenRouter client, parallel orchestration, failure threshold handling, and comprehensive service tests); moved status to review.
- 2026-03-21: Applied code review patches (10 findings): asyncio.gather return_exceptions=True, TransportError MRO fix, _update_run_row DB error handling, openrouter_api_key required field, execute_persona_engine try/except, max_attempts guard, blueprint count validation, openrouter_base_url AnyHttpUrl, Sentry capture_message; moved status to done.
