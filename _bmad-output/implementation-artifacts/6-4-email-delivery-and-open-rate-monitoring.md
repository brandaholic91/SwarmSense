# Story 6.4: Email Delivery & Open Rate Monitoring

Status: done

## Story

As an operator,  
I want visibility into result email delivery rates and open rates,  
so that I can monitor whether users are actually receiving and engaging with their analysis results.

## Acceptance Criteria

1. Given result and follow-up emails are sent via Resend, when operator monitoring is performed, then delivery success rates are available by email type (result, magic link, follow-up day 1/3/7).  
2. Open rates are visible for result emails and follow-up sequences. Open rate is defined as `opens / delivered` (not `opens / sent`) — undelivered emails cannot be opened, so the delivered count is the correct denominator. When `delivered == 0`, open rate returns `0.0`.  
3. `GET /api/v1/operator/email-stats` (Bearer protected) returns a summary payload (e.g. `result_emails_sent`, `result_delivery_rate`, `followup_day1_sent`) sourced from Resend API and/or webhook-backed persistence.  
4. If 7-day rolling delivery success rate drops below 95%, a Sentry alert is emitted (NFR12). The rate is computed over **result and follow-up emails only** (`result + followup_day1 + followup_day3 + followup_day7`). Magic link emails are transactional and excluded from this threshold — they have a different expected delivery profile and must not skew the operational alert. Additionally, the alert must not fire when `total_sent == 0` (empty window or provider API outage produces zeroed metrics, not a false degradation alert).

## Tasks / Subtasks

- [x] Define monitoring data source strategy (AC: 1, 2, 3, 4)
  - [x] Decide source of truth per metric: direct Resend API fetch vs internal webhook-backed table
  - [x] Keep one canonical aggregation path to avoid conflicting metrics
- [x] Implement/extend email stats service layer (AC: 1, 2, 3)
  - [x] Add or extend a dedicated service module (e.g. `backend/app/services/email_metrics.py` or equivalent)
  - [x] Normalize per-email-type metrics: sent, delivered, opened, delivery_rate
  - [x] Apply robust defaults for missing data (return zeros, never crash endpoint)
- [x] Implement operator endpoint `GET /api/v1/operator/email-stats` (AC: 3)
  - [x] Add route in `backend/app/routers/operator.py`
  - [x] Reuse hardened operator auth pattern from stories `6.1–6.3`
  - [x] Return stable, documented JSON contract in snake_case
- [x] Implement 7-day delivery health check and alerting (AC: 4)
  - [x] Compute rolling 7-day delivery success rate from chosen data source
  - [x] Trigger Sentry alert when rate drops below `0.95`
  - [x] Add anti-spam guardrail (dedupe/throttle) to prevent repeated alerts for unchanged degraded state
- [x] Add backend tests for endpoint + alerting behavior (AC: 1, 2, 3, 4)
  - [x] Operator auth tests: missing/invalid token -> 403
  - [x] Response contract tests for happy path and empty-data path
  - [x] Delivery/open metric aggregation tests
  - [x] 7-day threshold alert trigger + dedupe tests

## Dev Notes

### Story Foundation and Scope

- This story finalizes Epic 6 operator observability by adding email deliverability + engagement metrics.
- Keep implementation backend-only; operator consumes protected endpoint plus existing external dashboards.
- Align with FR30 and NFR12 without introducing unnecessary UI complexity.

### Existing Patterns to Reuse (Do Not Reinvent)

- Reuse operator auth and response-hardening conventions from `6.1`, `6.2`, and `6.3`.
- Keep endpoint under existing operator router and preserve same Forbidden behavior for auth failures.
- Follow established snake_case API boundary and defensive parsing style.

### Architecture Compliance Requirements

- Resend remains email provider and primary telemetry source for email events.
- Sentry remains alert channel for reliability threshold breaches.
- Do not expose secrets or provider internals through endpoint payload.
- Keep endpoint shape operational and compact (dashboard-friendly).

### Data Contract Requirements

- `/api/v1/operator/email-stats` must return exactly:
  - `window_days` (expected `7`)
  - `result_emails_sent`
  - `result_delivery_rate`
  - `result_open_rate` — computed as `result_opened / result_delivered` (see AC2)
  - `magic_link_sent`
  - `magic_link_delivery_rate`
  - `followup_day1_sent`
  - `followup_day3_sent`
  - `followup_day7_sent`
  - `followup_delivery_rate`
  - `followup_open_rate` — computed as `followup_opened / followup_delivered` (see AC2)
  - `overall_delivery_rate` — computed over result + followup emails only (excludes magic_link; see AC4)
- Magic link emails are included in the payload as observability data (`magic_link_sent`, `magic_link_delivery_rate`) but are **not** included in `overall_delivery_rate` and do not contribute to the AC4 threshold alert. `magic_link_open_rate` is intentionally omitted (magic links are not marketing emails and open rate is not a meaningful metric for them).
- All rate fields are normalized decimals in `[0, 1]`. When the denominator is zero, return `0.0`.
- Empty data must return valid zeroed metrics, not 500 errors.

### File Structure Requirements

- Likely modify:
  - `backend/app/routers/operator.py`
  - `backend/app/models/operator.py`
  - `backend/app/services/email_service.py` (if metrics helpers live here)
  - `backend/app/services/*email*metrics*.py` (if introduced)
  - `backend/tests/routers/test_operator.py`
  - `backend/tests/services/test_email*_metrics*.py` (or existing email service tests)
- Optional migration only if webhook event persistence needs new schema support.

### Testing Requirements

- Required test categories:
  - Auth guard behavior (missing/invalid token)
  - Endpoint success payload contract (all fields, correct types, `[0,1]` range)
  - Empty/partial provider data resilience — both full provider failure AND partial/malformed rows (missing `created_at`, empty `tags`, missing `last_event`)
  - Correct 7-day rolling delivery rate calculation with mixed email types
  - Open rate calculation: `opens / delivered`, not `opens / sent` — verify with explicit test where delivery rate < 100%
  - Alert threshold behavior: `<95%` triggers alert (from cold state); `>=95%` does NOT trigger alert (from cold state); `total_sent == 0` does NOT trigger alert (empty-window guard)
  - Alert dedupe/throttle behavior: same rate bucket → dedupe; rate recovery then re-degradation → re-fires
  - `overall_delivery_rate` excludes magic_link emails — verify by including magic_link rows in fixture and asserting they don't influence the alert-triggering rate
  - `followup_day1`, `followup_day3`, `followup_day7` tag emission verified in `test_email_service.py` (all three types, not just day3)

### Previous Story Intelligence (6.3)

- `6.3` introduced hardened operational metrics patterns (threshold semantics, once-per-period alerting, robust endpoint responses).
- Apply the same reliability mindset: deterministic calculations, anti-spam alert logic, and strong test coverage.
- Preserve non-run feature stability and avoid regressions in completed operator endpoints.

### Git Intelligence Summary

- Epic 6 has mature operator endpoint patterns; 6.4 should extend, not reshape, that structure.
- Prefer incremental extension with explicit contracts and conservative side effects.

### Latest Technical Notes

- Use FastAPI + Pydantic v2 patterns already present in operator routes/models.
- Keep provider failures isolated: metric-fetch failures should degrade gracefully and be observable via Sentry.

### References

- Epic definition: `_bmad-output/planning-artifacts/epics.md` (Story 6.4).
- PRD references: `_bmad-output/planning-artifacts/prd.md` (FR30, NFR12).
- Architecture references: `_bmad-output/planning-artifacts/architecture.md` (Resend integration, operator endpoints, monitoring).
- Prior stories: `_bmad-output/implementation-artifacts/6-1-operator-run-log-endpoint.md`, `_bmad-output/implementation-artifacts/6-2-qualifier-response-log-endpoint.md`, `_bmad-output/implementation-artifacts/6-3-api-cost-tracking-80-percent-alert-and-hard-cap-enforcement.md`.
- Project rules: `_bmad-output/project-context.md`.

## Dev Agent Record

### Agent Model Used

gpt-5.3-codex-low

### Debug Log References

- Story context synthesized from sprint status, Epic 6 ACs, PRD NFR/FR mappings, architecture monitoring patterns, and finished 6.1–6.3 intelligence.
- Implemented canonical Resend-driven aggregation path via `backend/app/services/email_metrics.py` with defensive parsing and zero-default fallback behavior.
- Added protected operator endpoint `GET /api/v1/operator/email-stats` with strict response model and existing operator bearer validation path.
- Added 7-day delivery-rate health alerting (<95%) with dedupe guardrail keyed by unchanged degraded rate bucket, plus recovery reset behavior.
- Executed targeted and full backend regression suites (`pytest tests/routers/test_operator.py tests/services/test_email_metrics.py tests/services/test_email_service.py` and full `pytest`).

### Completion Notes List

- Story prepared with concrete backend implementation guardrails for email metrics + threshold alerting.
- Scope constrained to operator endpoint, metrics aggregation, alerting reliability, and test coverage.
- Added `OperatorEmailStatsResponse` and `/api/v1/operator/email-stats` route with compact snake_case payload contract.
- Added `email_metrics` service for normalized sent/delivered/opened counters and delivery/open rates across result, magic link, and follow-up day 1/3/7 email types.
- Added resilient provider failure handling: metrics endpoint remains stable with zeroed payloads and Sentry exception capture.
- Added 7-day rolling delivery-rate Sentry warning (<95%) with anti-spam dedupe for unchanged degraded states.
- Added Resend email tagging on outbound sends (`result`, `magic_link`, `followup_dayX`) for reliable type attribution.
- **Code review completed and all 17 patch findings resolved:**
  - `_safe_int`: NaN/Inf float guard + `max(0,...)` for negatives
  - `_is_delivered`: `delivered_at` only counts as delivered if parseable as datetime
  - `_resolve_email_type`: `"24"` heuristic narrowed to `"24 óra/ora"`; `logger.warning` on unresolved type
  - `_open_rate`: denominator changed to `delivered` (industry standard, per AC2)
  - `_load_resend_emails`: cursor-based pagination (max 1 000 emails); thread-safe one-time `resend.api_key` init
  - `_emit_delivery_health_alert_if_needed`: `total_sent==0` false-alert guard; atomic lock (single block for check+set); bucket restored on Sentry failure; `round(rate,2)` anti-oscillation; dynamic `window_days` in message; `push_scope()` → `new_scope()`
  - `get_email_stats_summary`: `overall_delivery_rate` excludes magic_link (per AC4 + IG-2); main row loop wrapped in try/except; `new_scope()` throughout
  - Tests: open rate denominator test; magic_link exclusion test; partial/malformed row resilience; `total_sent==0` false-alert test; `>=95%` cold-state no-alert test; dynamic window_days message test; Sentry-failure bucket restore test; `followup_day1` + `followup_day7` tag tests; router contract tests use `OperatorEmailStatsResponse` instances
- All 127 backend tests pass. Story status: **done**.

### File List

- `_bmad-output/implementation-artifacts/6-4-email-delivery-and-open-rate-monitoring.md` (updated)
- `backend/app/models/operator.py` (updated)
- `backend/app/routers/operator.py` (updated)
- `backend/app/services/email_metrics.py` (added)
- `backend/app/services/email_service.py` (updated)
- `backend/tests/routers/test_operator.py` (updated)
- `backend/tests/services/test_email_metrics.py` (added)
- `backend/tests/services/test_email_service.py` (updated)

## Change Log

- 2026-03-23: Implemented email delivery/open monitoring endpoint, Resend-backed metrics aggregation service, 7-day <95% Sentry alerting with dedupe, and comprehensive router/service test coverage.
- 2026-03-23: Spec amended post code review — clarified: open rate denominator (`opens/delivered`), alert scope (result+followup only, magic_link excluded), `total_sent==0` false-alert guard, magic_link payload contract (sent+delivery_rate included, open_rate excluded), full testing requirements for all tag types and open rate semantics.
- 2026-03-23: Code review findings resolved (17 patches) — service hardened, tests expanded, story moved to `done`.
