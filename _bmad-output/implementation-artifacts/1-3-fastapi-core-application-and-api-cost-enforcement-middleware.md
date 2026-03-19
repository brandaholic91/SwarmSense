# Story 1.3: FastAPI Core Application & API Cost Enforcement Middleware

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As the system,
I want all run-initiating API paths to check the monthly API spend cap before proceeding,
so that the $50/month hard limit is enforced at the application layer and cannot be bypassed by any future endpoint.

## Acceptance Criteria

1. Given the FastAPI application is running, when a request arrives at any run-initiating endpoint, then `cost_enforcement.py` queries `cost_tracking` for the current month's `total_usd` before allowing the request to proceed.
2. If `total_usd >= 50.00`, the endpoint returns HTTP 402 with `{"detail": "A havi ingyenes kapacitás elérte a határát.", "code": "COST_LIMIT_REACHED"}`.
3. Non-run endpoints (auth, waitlist, operator, status polling) are unaffected when the monthly limit is reached.
4. All environment variables are parsed via Pydantic Settings from `SWARMSENSE_`-prefixed env vars: `SWARMSENSE_SUPABASE_URL`, `SWARMSENSE_SUPABASE_SERVICE_KEY`, `SWARMSENSE_KIMI_API_KEY`, `SWARMSENSE_OPERATOR_API_KEY`, `SWARMSENSE_FRONTEND_ORIGIN`.
5. CORS middleware is configured to allow requests only from the Vercel frontend domain.
6. FastAPI OpenAPI docs (`/docs` and `/redoc`) are disabled in production via env configuration.

## Tasks / Subtasks

- [x] Implement settings + app wiring for core backend config (AC: 4, 5, 6)
  - [x] Create/update `backend/app/core/config.py` with Pydantic Settings using `SWARMSENSE_` env prefix and a `ENVIRONMENT` or equivalent flag for prod toggles.
  - [x] Ensure `backend/app/main.py` reads settings and configures CORS allowed origins to the Vercel domain only.
  - [x] Disable OpenAPI docs in production (set `docs_url=None`, `redoc_url=None`) based on settings.
- [x] Implement cost enforcement middleware (AC: 1, 2, 3)
  - [x] Add `backend/app/core/cost_enforcement.py` middleware or dependency to guard run-initiating endpoints only (allowlist by path + method).
  - [x] Read the current month (`YYYY-MM`) and query `cost_tracking.total_usd` via Supabase client; treat missing rows as `0` (optionally insert on first use).
  - [x] Return HTTP 402 with `code: COST_LIMIT_REACHED` when total is >= 50.00.
- [x] Add error code constant for cost limit (AC: 2)
  - [x] Update `backend/app/core/errors.py` with `COST_LIMIT_REACHED` enum + helper for HTTP 402 responses.
- [x] Add tests for middleware guardrails (AC: 1, 2, 3)
  - [x] Create tests in `backend/tests/routers/test_runs.py` or `backend/tests/services/test_cost_tracker.py` using FastAPI TestClient with a mocked Supabase client.
  - [x] Verify run endpoints are blocked at cap and non-run endpoints still respond.

## Dev Notes

- Use architecture naming conventions: `snake_case` JSON, `SWARMSENSE_` env prefix, Pydantic v2 Settings in `backend/app/core/config.py`.
- Cost enforcement must wrap any run-initiating path (currently `POST /api/v1/runs`; keep allowlist extensible for future run endpoints).
- Error response must include Hungarian `detail` and a stable `code` for frontend mapping.
- CORS must restrict to the Vercel frontend domain only; avoid `*` in prod.
- OpenAPI docs disabled in production to reduce surface area.
- Use Pydantic Settings (`pydantic-settings`) for environment parsing with `env_prefix='SWARMSENSE_'`.
- Prior story 1.2 renamed Supabase migrations to unique versions; do not rely on old migration filenames.

### Project Structure Notes

- Backend core modules live under `backend/app/core/` (`config.py`, `database.py`, `cost_enforcement.py`, `errors.py`).
- Router modules live under `backend/app/routers/`; cost enforcement should gate run-initiating routes without affecting `auth`, `waitlist`, `operator`, or status polling.
- Tests belong under `backend/tests/` mirroring `app/` structure.

### References

- `_bmad-output/planning-artifacts/epics.md#Story 1.3` (acceptance criteria)
- `_bmad-output/planning-artifacts/epics.md#Additional Requirements` (cost enforcement middleware, env vars, CORS, docs disable)
- `_bmad-output/planning-artifacts/architecture.md#Core Architectural Decisions` (config, CORS, OpenAPI docs)
- `_bmad-output/planning-artifacts/architecture.md#Implementation Patterns & Consistency Rules` (naming conventions, env prefix)
- `_bmad-output/planning-artifacts/architecture.md#Project Structure & Boundaries` (file locations)
- `_bmad-output/planning-artifacts/architecture.md#Process Patterns` (error handling + code field)
- `_bmad-output/implementation-artifacts/1-2-database-foundation-users-and-cost-tracking-schema.md` (cost_tracking table availability)
- https://fastapi.tiangolo.com/ (FastAPI middleware/CORS/docs configuration reference)
- https://docs.pydantic.dev/latest/concepts/pydantic_settings/ (Pydantic Settings env parsing)

## Dev Agent Record

### Agent Model Used

openai/gpt-5.2-codex

### Debug Log References

- 2026-03-20: `python -m pytest` (4 passed)
- 2026-03-20: Code review (3-layer adversarial: Blind Hunter, Edge Case Hunter, Acceptance Auditor) — 10 patch, 1 bad_spec, 2 defer found; all patches applied, `python -m pytest` (9 passed)

### Completion Notes List

- Implemented settings-driven FastAPI app wiring with CORS restriction and production doc toggles.
- Added cost enforcement middleware with Supabase cost_tracking lookup and stable error response for cap breaches.
- Added error code helper and router tests validating run blocking and non-run passthrough.

### File List

- backend/app/__init__.py
- backend/app/core/__init__.py
- backend/app/core/config.py
- backend/app/core/cost_enforcement.py
- backend/app/core/database.py
- backend/app/core/errors.py
- backend/app/main.py
- backend/app/routers/__init__.py
- backend/app/routers/runs.py
- backend/app/routers/status.py
- backend/requirements.txt
- backend/tests/__init__.py
- backend/tests/routers/__init__.py
- backend/tests/routers/test_runs.py
- _bmad-output/implementation-artifacts/sprint-status.yaml

### Change Log

- 2026-03-20: Implemented core FastAPI configuration, cost enforcement middleware, error handling, and tests; updated sprint status to review.
- 2026-03-20: Code review patches applied — async I/O fix (asyncio.to_thread), fail-closed error handling (CostCheckError/503), trailing slash bypass fix, CORS middleware ordering fix (BaseHTTPMiddleware + add_middleware), Pydantic AnyHttpUrl trailing slash bug fix, get_supabase_client cache isolation in tests, limit(1) on DB query, _normalize_total raises on corrupt values, COST_CHECK_FAILED error code added, 5 new tests (trailing slash, 503 fail-closed, production docs, CORS allow/block), spec AC 4 updated with SWARMSENSE_FRONTEND_ORIGIN; story closed as done.
