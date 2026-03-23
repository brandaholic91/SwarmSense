# Story 6.3: API Cost Tracking, 80% Alert & Hard Cap Enforcement

Status: ready-for-dev

## Story

As an operator,  
I want to receive an automatic alert when monthly API spend reaches 80% of the $50 limit and see current cost via an endpoint,  
so that I can monitor burn rate and the system automatically protects against overruns.

## Acceptance Criteria

1. Given a run completes and `cost_tracker.py` increments monthly spend, when total reaches or exceeds `$40.00`, then an automated alert is sent within 60 seconds (Sentry alert or email), and the alert fires only once per threshold crossing per month.  
2. Given the operator calls `GET /api/v1/operator/cost` with valid Bearer token, then response includes: `month` (`YYYY-MM`), `total_usd`, `cap_usd` (`50.00`), `percentage`, `status` (`ok | warning | capped`).  
3. Given monthly `total_usd >= 50.00`, when a new run is attempted, then run initiation is blocked with HTTP `402` and `code: "COST_LIMIT_REACHED"`, and user-facing Hungarian message is shown while non-run features remain operational.

## Tasks / Subtasks

- [ ] Validate and align existing cost-tracking data model + service behavior (AC: 1, 3)
  - [ ] Confirm `cost_tracking` table fields used by current services are sufficient for threshold event tracking
  - [ ] Add/adjust monthly threshold marker fields only if strictly required for idempotent one-time 80% alert behavior
- [ ] Implement or finalize 80% threshold alert logic (AC: 1)
  - [ ] Extend `backend/app/services/cost_tracker.py` to detect threshold crossing (`<40` -> `>=40`) and emit alert
  - [ ] Ensure alert path is idempotent per month and does not spam on every run after threshold reached
  - [ ] Ensure alert includes current spend and cap in payload/message
- [ ] Implement operator cost endpoint `GET /api/v1/operator/cost` (AC: 2)
  - [ ] Add route in `backend/app/routers/operator.py`
  - [ ] Reuse hardened operator auth pattern from `6.1/6.2`
  - [ ] Return computed `percentage` and canonical status mapping:
    - [ ] `ok` when `<80%`
    - [ ] `warning` when `>=80% and <100%`
    - [ ] `capped` when `>=100%`
- [ ] Validate hard-cap enforcement on run initiation path (AC: 3)
  - [ ] Confirm `cost_enforcement` executes before any LLM-dispatch path
  - [ ] Ensure HTTP 402 + `COST_LIMIT_REACHED` response shape and Hungarian message mapping remain consistent
  - [ ] Verify auth/waitlist/status polling/operator endpoints stay functional when capped
- [ ] Add backend tests for threshold, endpoint, and cap behavior (AC: 1, 2, 3)
  - [ ] Add/extend tests in `backend/tests/services/test_cost_tracker.py` (threshold crossing + one-time alert)
  - [ ] Add/extend tests in `backend/tests/routers/test_operator.py` for `/operator/cost`
  - [ ] Add/extend tests around cap block behavior in middleware/router test scope

## Dev Notes

### Story Foundation and Scope

- Epic 6.3 combines three tightly linked concerns: monthly spend accounting, alerting at 80%, and hard-cap gating at 100%.
- This is backend-focused (service + operator endpoint + middleware behavior verification).
- Keep user-facing cap behavior explicit and non-silent (reject with clear message, not drop/ignore).

### Existing Patterns to Reuse (Do Not Reinvent)

- Operator auth and response hardening patterns are already stabilized in `6.1` and `6.2`.
- Cost cap architecture already exists (`core/cost_enforcement.py` + `services/cost_tracker.py`); extend safely instead of introducing parallel mechanisms.
- Keep API boundary keys snake_case, matching project conventions and existing endpoints.

### Architecture Compliance Requirements

- Cap value is fixed at `$50.00` in MVP.
- Alert threshold is fixed at `80%` (`$40.00`) with once-per-threshold-crossing semantics.
- Cost enforcement must remain in pre-dispatch path so cap cannot be bypassed.
- Alerting channel can be Sentry and/or operator email according to existing project integrations.

### Data Contract Requirements

- `/api/v1/operator/cost` response fields:
  - `month` (YYYY-MM)
  - `total_usd` (decimal, non-negative)
  - `cap_usd` (50.00)
  - `percentage` (`total_usd / cap_usd * 100`)
  - `status` (`ok` | `warning` | `capped`)
- Preserve existing error response conventions for unauthorized operator access and cap-reached run rejection.

### File Structure Requirements

- Likely modify:
  - `backend/app/services/cost_tracker.py`
  - `backend/app/core/cost_enforcement.py`
  - `backend/app/routers/operator.py`
  - `backend/app/models/operator.py`
  - `backend/tests/services/test_cost_tracker.py`
  - `backend/tests/routers/test_operator.py`
- Migration only if threshold-state persistence truly requires schema extension.

### Testing Requirements

- Required test categories:
  - 80% threshold crossing triggers alert once per month
  - Repeated post-threshold updates do not re-alert
  - Month rollover allows new threshold alert cycle
  - `/api/v1/operator/cost` auth behavior (missing/invalid token -> 403)
  - `/api/v1/operator/cost` payload correctness and status mapping
  - Cap reached -> run attempt blocked with 402 and `COST_LIMIT_REACHED`
  - Non-run endpoints still available when cap reached

### Previous Story Intelligence (6.2)

- `6.2` strengthened operator endpoint robustness (pagination semantics, malformed row handling, strict linkage checks).
- Reuse its defensive validation approach where cost endpoint consumes database rows.
- Keep conservative change footprint and avoid regressions in done operator endpoints.

### Git Intelligence Summary

- Epic 6 operator layer is in active build sequence; consistency and test depth are higher priority than abstraction expansion.
- Keep implementation incremental and colocated in existing operator/cost modules.

### Latest Technical Notes

- Maintain FastAPI + Pydantic v2 patterns and Python 3.12 typing.
- Use constant-time operator key compare pattern already introduced by 6.1 code-review fixes.

### References

- Epic definition: `_bmad-output/planning-artifacts/epics.md` (Story 6.3).
- PRD references: `_bmad-output/planning-artifacts/prd.md` (FR28, FR29, NFR16, NFR17).
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (`cost_enforcement.py`, `cost_tracker.py`, operator route constraints).
- Previous stories: `_bmad-output/implementation-artifacts/6-1-operator-run-log-endpoint.md`, `_bmad-output/implementation-artifacts/6-2-qualifier-response-log-endpoint.md`.
- Project context: `_bmad-output/project-context.md`.

## Dev Agent Record

### Agent Model Used

gpt-5.3-codex-low

### Debug Log References

- Story context derived from sprint status + Epic 6 AC set + PRD/architecture cost-governance requirements + completed 6.1/6.2 learnings.

### Completion Notes List

- Story prepared with strict implementation guardrails for cost alerting and cap enforcement.
- Scope constrained to backend services, operator endpoint, middleware behavior, and tests.
- Status set to `ready-for-dev`.

### File List

- `_bmad-output/implementation-artifacts/6-3-api-cost-tracking-80-percent-alert-and-hard-cap-enforcement.md` (created)
