# Story 6.1: Operator Run Log Endpoint

Status: ready-for-dev

## Story

As an operator,  
I want to view a log of all submitted runs with their status, persona counts, and costs via a protected API endpoint,  
so that I can monitor daily activity, identify failed runs, and verify the system is working as expected.

## Acceptance Criteria

1. Given the operator calls `GET /api/v1/operator/runs` with a valid Bearer token, when the endpoint processes the request, then it returns a paginated list with: `run_id`, `user_email`, `topic`, `audience`, `status`, `persona_count`, `cost_usd`, `created_at`, `completed_at`; runs are ordered by `created_at` descending; missing/invalid token returns HTTP 403.  
2. Given the operator calls `GET /api/v1/operator/runs?status=failed`, when the endpoint filters, then only failed runs are returned and each failed run includes error code and error timestamp metadata.  
3. Given a run has `status=failed` or `status=partial`, when the run is logged, then 100% of failed/partial runs contain error code and timestamp metadata.

## Tasks / Subtasks

- [ ] Define operator run-log response models (AC: 1, 2, 3)
  - [ ] Add Pydantic models in `backend/app/models/operator.py` for paginated response and run row schema
  - [ ] Keep snake_case field names at API boundary (no camelCase aliases)
- [ ] Implement protected endpoint `GET /api/v1/operator/runs` (AC: 1, 2)
  - [ ] Extend `backend/app/routers/operator.py` with new GET route
  - [ ] Reuse existing HTTP Bearer auth pattern (`Security(HTTPBearer(auto_error=False))`)
  - [ ] Return HTTP 403 `detail="Forbidden"` for missing/invalid token (same behavior as existing operator route)
- [ ] Implement query + filtering + ordering + pagination (AC: 1, 2)
  - [ ] Query `runs` with newest-first ordering by `created_at`
  - [ ] Support `status` filter via query param
  - [ ] Add pagination controls (`page`, `page_size`), with sane defaults and max page size guardrail
- [ ] Include failure metadata for failed/partial runs (AC: 2, 3)
  - [ ] Read error fields from `runs` table (existing metadata columns if available)
  - [ ] If schema mismatch appears, align with existing DB columns before coding fallback logic
- [ ] Add backend tests for auth, ordering, filtering, and pagination (AC: 1, 2, 3)
  - [ ] Create `backend/tests/routers/test_operator.py`
  - [ ] Cover 403 auth failure, success response shape, failed filter, and descending ordering
  - [ ] Add tests ensuring failed/partial records include error metadata

## Dev Notes

### Story Foundation and Scope

- Epic 6 introduces operator monitoring capabilities; this story is the first operator visibility endpoint.  
- Endpoint must be operator-only and must not expose non-required data fields.
- This story is backend-only; no new frontend UI is required (operator uses protected API + existing external dashboards).

### Existing Patterns to Reuse (Do Not Reinvent)

- Operator auth already exists in `backend/app/routers/operator.py` for `POST /api/v1/operator/send-followups`.  
- Keep identical auth style and status code behavior for consistency and lower regression risk.
- Follow existing router structure and global prefix conventions (`/api/v1`, plural nouns, lowercase paths).

### Architecture Compliance Requirements

- Keep endpoint under operator router: `APIRouter(prefix="/api/v1/operator", tags=["operator"])`.
- Use FastAPI + Pydantic v2 style (`ConfigDict`, strict model fields).
- Keep error response format consistent with existing backend conventions.
- Preserve stateless operator API key auth via `SWARMSENSE_OPERATOR_API_KEY`.

### Data Contract Requirements

- Required response item fields:
  - `run_id`
  - `user_email`
  - `topic`
  - `audience`
  - `status`
  - `persona_count`
  - `cost_usd`
  - `created_at`
  - `completed_at`
- For failed/partial runs also include:
  - `error_code`
  - `error_at`
- Pagination response should include metadata (minimum: `page`, `page_size`, `total`, `items`).

### File Structure Requirements

- Modify:
  - `backend/app/routers/operator.py`
  - `backend/app/models/operator.py`
- Add:
  - `backend/tests/routers/test_operator.py`
- Do not introduce frontend changes in this story.

### Testing Requirements

- Use pytest patterns already used in backend tests.
- Test cases required:
  - Missing bearer token -> 403
  - Invalid bearer token -> 403
  - Valid token -> 200 + paginated payload
  - Default sort order: `created_at DESC`
  - `status=failed` filter returns only failed rows
  - Failed/partial rows include error metadata
- Include boundary tests for pagination (`page_size` limits, empty page behavior).

### Previous Story Intelligence (5.6)

- Keep existing behavior untouched; previous story touched email flow and run persistence.
- Do not alter follow-up dispatch endpoint auth or signature while adding the new run-log route.
- Maintain conservative change scope to avoid regressions in recently stabilized email functionality.

### Git Intelligence Summary

- Recent commits are frontend-heavy; backend operator monitoring remains mostly open for implementation.
- This story should establish clear backend conventions for upcoming Epic 6 stories (6.2, 6.3, 6.4).
- Keep implementation minimal, explicit, and well-tested to serve as a baseline for later operator endpoints.

### Latest Technical Notes

- FastAPI `HTTPBearer(auto_error=False)` + explicit credential check is already in active use in this codebase and should remain the pattern for operator routes.
- Continue using Python 3.12 union syntax and Pydantic v2 models for consistency.

### References

- Epic definition: `_bmad-output/planning-artifacts/epics.md` (Epic 6, Story 6.1).
- Product requirements: `_bmad-output/planning-artifacts/prd.md` (FR26, NFR13, Journey 4 context).
- Architecture constraints: `_bmad-output/planning-artifacts/architecture.md` (operator endpoints, auth, structure).
- Project guardrails: `_bmad-output/project-context.md`.
- Existing endpoint pattern: `backend/app/routers/operator.py`.

## Dev Agent Record

### Agent Model Used

gpt-5.3-codex-low

### Debug Log References

- Story context built from epics, PRD, architecture, project-context, sprint status, and previous story 5.6.

### Completion Notes List

- Story prepared with implementation guardrails and explicit anti-regression constraints.
- Scope constrained to backend operator run log endpoint and tests only.
- Status set to `ready-for-dev`.

### File List

- `_bmad-output/implementation-artifacts/6-1-operator-run-log-endpoint.md` (created)
