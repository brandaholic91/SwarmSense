# Story 6.2: Qualifier Response Log Endpoint

Status: ready-for-dev

## Story

As an operator,  
I want to view qualifier survey responses associated with each verified email address,  
so that I can analyse what roles and use cases are most common among early users and inform product decisions.

## Acceptance Criteria

1. Given the operator calls `GET /api/v1/operator/qualifier-responses` with a valid Bearer token, when the endpoint processes the request, then it returns qualifier response records with: `user_email`, `role_answer`, `use_case_answer`, `created_at`; records are ordered by `created_at` descending; missing/invalid token returns HTTP 403.  
2. No cross-user data is exposed: each returned row must represent only a valid user/run-linked qualifier response record (NFR9).

## Tasks / Subtasks

- [ ] Define response models for qualifier log endpoint (AC: 1, 2)
  - [ ] Extend `backend/app/models/operator.py` with qualifier log row + paginated/list response
  - [ ] Keep API boundary keys in `snake_case`
- [ ] Implement protected endpoint `GET /api/v1/operator/qualifier-responses` (AC: 1, 2)
  - [ ] Add route in `backend/app/routers/operator.py` under existing operator router
  - [ ] Reuse existing `HTTPBearer(auto_error=False)` + explicit key check pattern
  - [ ] Return HTTP 403 with `detail="Forbidden"` for missing/invalid token
- [ ] Implement data retrieval and ordering (AC: 1)
  - [ ] Read `qualifier_responses` joined with `users` (email) and optional `runs` integrity fields as needed
  - [ ] Ensure sort is `created_at DESC`
  - [ ] Apply optional pagination guardrails for consistency with `6.1` endpoint style
- [ ] Enforce data isolation and safe exposure (AC: 2)
  - [ ] Return only required fields (`user_email`, `role_answer`, `use_case_answer`, `created_at`)
  - [ ] Exclude internal identifiers and sensitive columns from response payload
- [ ] Add backend tests (AC: 1, 2)
  - [ ] Extend `backend/tests/routers/test_operator.py` (or add dedicated qualifier endpoint tests)
  - [ ] Cover token auth failures and successful response schema
  - [ ] Validate descending ordering and cross-user leakage prevention expectations

## Dev Notes

### Story Foundation and Scope

- Epic 6 expands operator observability; this story adds operator visibility into qualifier answers.
- This is a backend API story; no frontend page/component work is required.
- Keep endpoint minimal, operational, and consistent with established operator patterns.

### Existing Patterns to Reuse (Do Not Reinvent)

- `6.1` established the operator endpoint baseline in `backend/app/routers/operator.py` and `backend/app/models/operator.py`.
- Reuse the same auth, error, and response style decisions from `6.1` unless AC explicitly demands otherwise.
- Follow existing naming and routing conventions (`/api/v1/operator/*`, plural nouns, lowercase, kebab-case path).

### Architecture Compliance Requirements

- `qualifier_responses` table exists and is part of core flow; use it as primary source.
- Operator routes stay behind static Bearer key (`SWARMSENSE_OPERATOR_API_KEY`).
- Do not introduce new auth model, new middleware, or frontend data access.

### Data Contract Requirements

- Required output fields per record:
  - `user_email`
  - `role_answer`
  - `use_case_answer`
  - `created_at`
- Keep timestamps ISO 8601 compatible.
- Keep payload focused: no user IDs, run IDs, internal metadata unless explicitly required by AC.

### File Structure Requirements

- Modify:
  - `backend/app/routers/operator.py`
  - `backend/app/models/operator.py`
  - `backend/tests/routers/test_operator.py` (or equivalent operator router test file)
- No frontend file changes.

### Testing Requirements

- Required tests:
  - Missing bearer token -> 403
  - Invalid bearer token -> 403
  - Valid bearer token -> 200 + expected fields only
  - Sort order is `created_at DESC`
  - No leakage of non-required cross-user/internal fields
- Run focused test module first, then broader backend regression if feasible.

### Previous Story Intelligence (6.1)

- `6.1` is done and already hardened via code review with security/data-integrity fixes.
- Preserve those hardened patterns (constant-time key compare, robust parsing, constrained payloads) when adding `6.2`.
- Avoid touching unrelated routes to keep regression risk low.

### Git Intelligence Summary

- Epic 6 backend operator surface is now active; consistency across `6.1` and `6.2` is more important than adding new abstractions.
- Prefer incremental extension in existing operator router/model modules.

### Latest Technical Notes

- Keep FastAPI + Pydantic v2 idioms already used in codebase.
- Keep Python 3.12 typing style (`str | None`, `list[...]`).

### References

- Epic source: `_bmad-output/planning-artifacts/epics.md` (Story 6.2).
- PRD context: `_bmad-output/planning-artifacts/prd.md` (FR27, NFR9, Journey 4).
- Architecture constraints: `_bmad-output/planning-artifacts/architecture.md`.
- Previous story: `_bmad-output/implementation-artifacts/6-1-operator-run-log-endpoint.md`.
- Project rules: `_bmad-output/project-context.md`.

## Dev Agent Record

### Agent Model Used

gpt-5.3-codex-low

### Debug Log References

- Story context built from sprint status, epic section, architecture references, and previous story 6.1 implementation notes.

### Completion Notes List

- Story prepared with backend-first implementation guardrails.
- Scope limited to operator qualifier response endpoint + tests.
- Status set to `ready-for-dev`.

### File List

- `_bmad-output/implementation-artifacts/6-2-qualifier-response-log-endpoint.md` (created)
