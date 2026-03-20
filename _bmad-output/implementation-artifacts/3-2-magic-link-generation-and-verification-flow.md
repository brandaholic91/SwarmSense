# Story 3.2: Magic Link Generation & Verification Flow

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a first-time user,
I want to receive a magic link in my email and click it to verify my identity,
so that I can proceed to the analysis without creating a password.

## Acceptance Criteria

1. Given a new user's email has passed the DB check, when `POST /api/v1/auth/magic-link` is called, then a UUID v4 token is generated and stored in `magic_link_tokens` with `expires_at = now() + 24 hours`.
2. Given a new user's email has passed the DB check, when `POST /api/v1/auth/magic-link` is called, then a new record is created in `users` with normalized email, `has_consent = true`, and `consent_timestamp = now()`.
3. Given `POST /api/v1/auth/magic-link` succeeds, when the email provider call is executed, then a magic link email is sent via Resend within 60 seconds containing `https://[domain]/verify?token=[UUID]` (NFR3).
4. Given a magic link email is sent, when sender metadata is checked, then it uses a real identified sender address and a real reply-to address.
5. Given a user clicks the magic link, when `/verify` calls `POST /api/v1/auth/verify`, then if token exists, is not expired, and `used_at IS NULL`, mark token used (`used_at = now()`) and redirect to `/qualifier` with `user_id` in session/URL parameter.
6. Given a user clicks an expired token, when `/api/v1/auth/verify` validates it, then endpoint returns 401 with `code: "TOKEN_EXPIRED"` and frontend shows a full-screen Hungarian error with "Új link kérése" CTA (NFR8).
7. Given a user clicks a used or invalid token, when `/api/v1/auth/verify` validates it, then endpoint returns 401 with `code: "TOKEN_INVALID"` and frontend shows the same Hungarian full-screen error state.
8. Given this flow stores identity data, when schema and writes are reviewed, then only email address is stored as PII (no name, phone, payment data) (NFR11).

## Tasks / Subtasks

- [ ] Implement `POST /api/v1/auth/magic-link` endpoint in `backend/app/routers/auth.py` (AC: 1, 2, 3, 4, 8)
  - [ ] Add request/response models in `backend/app/models/auth.py` for magic-link generation
  - [ ] Normalize email at FastAPI boundary (`.lower().strip()`) before lookup/create
  - [ ] Upsert/create `users` record with `has_consent=true` and `consent_timestamp` from validated request flow
  - [ ] Generate UUID v4 token, insert into `magic_link_tokens` with 24h expiry and `used_at=NULL`
  - [ ] Build verification URL using server-side base URL config and append token query param
  - [ ] Call `email_service`/Resend client with real `from` and `reply_to` values from config
  - [ ] Return success payload without exposing sensitive internals

- [ ] Implement `POST /api/v1/auth/verify` endpoint in `backend/app/routers/auth.py` (AC: 5, 6, 7, 8)
  - [ ] Validate token existence, single-use (`used_at IS NULL`), and expiry (`expires_at > now()`)
  - [ ] Mark valid token as used atomically (`used_at = now()`) before returning success
  - [ ] Return 401 + `TOKEN_EXPIRED` for expired tokens and 401 + `TOKEN_INVALID` for used/unknown tokens
  - [ ] Return response including `user_id` required by qualifier entry flow (URL param or server action contract)

- [ ] Add frontend `/verify` integration for token handling and UX states (AC: 5, 6, 7)
  - [ ] Wire Server Action in `frontend/app/actions/verify-token.ts` to call backend verify endpoint
  - [ ] Parse `token` from `/verify?token=...` on `frontend/app/verify/page.tsx`
  - [ ] On success, redirect to `/qualifier` with agreed `user_id` handoff contract
  - [ ] On `TOKEN_EXPIRED` or `TOKEN_INVALID`, render full-screen Hungarian error and "Új link kérése" CTA
  - [ ] Keep all user-facing strings in `frontend/lib/messages.ts` and error-code mapping in `frontend/lib/errors.ts`

- [ ] Add magic-link email template and dispatch path (AC: 3, 4)
  - [ ] Implement or finalize `frontend/emails/magic-link-email.tsx` with inline CSS and tokenized styling
  - [ ] Ensure email contains direct verification link (`/verify?token=...`) and clear Hungarian copy
  - [ ] Verify sender identity/reply-to setup in backend env and sending code paths

- [ ] Add/extend automated tests (AC: 1-8)
  - [ ] Backend tests in `backend/tests/routers/test_auth.py` for: token creation, expiry window, single-use behavior, error codes
  - [ ] Backend test asserting user creation/consent fields for new user path
  - [ ] Frontend tests for `/verify` success redirect and full-screen error rendering for expired/invalid tokens
  - [ ] Contract tests for error payload shape `{detail, code}` and Hungarian error mapping behavior

## Dev Notes

- Reuse existing Story 3.1 foundations; do not rebuild check-email behavior:
  - `POST /api/v1/auth/check-email` already exists and returns new/returning status.
  - `magic_link_tokens` migration is already present with required columns and RLS.
  - Consent gating and legal link UX are already implemented on the research page.

- Auth flow boundaries to preserve:
  - Frontend never touches Supabase directly; all DB/token operations stay in FastAPI.
  - JSON fields remain `snake_case` across frontend/backend boundary.
  - Error response format remains `{ "detail": "...", "code": "..." }`.

- Token lifecycle requirements:
  - UUID v4 token, 24-hour expiry, single-use enforced via `used_at`.
  - Expired token must map to `TOKEN_EXPIRED`; used/unknown token maps to `TOKEN_INVALID`.
  - Valid token verification must set `used_at` immediately to prevent replay.

- UX and copy constraints:
  - Full-screen error state on verify failures with single recovery CTA: "Új link kérése".
  - Hungarian user-visible text must come from `frontend/lib/messages.ts` only.
  - Keep verification experience single-focus; avoid adding alternate CTAs.

- Security/compliance constraints:
  - Store only email as PII in this flow.
  - Use backend env vars (`SWARMSENSE_` prefix) for Resend/API configuration.
  - Use real sender + reply-to email identity in outbound magic-link emails.

- Performance target:
  - Magic link dispatch path must satisfy NFR3 (>=95% delivery within 60 seconds).
  - Keep endpoint operations lean: normalize, write token/user, dispatch email, return.

### Project Structure Notes

- Backend API/auth files:
  - `backend/app/routers/auth.py`
  - `backend/app/models/auth.py`
  - `backend/app/core/errors.py`
  - `backend/app/main.py` (router registration already present; adjust only if needed)

- Frontend verification flow:
  - `frontend/app/verify/page.tsx`
  - `frontend/app/actions/verify-token.ts`
  - `frontend/lib/errors.ts`
  - `frontend/lib/messages.ts`

- Email template + sending:
  - `frontend/emails/magic-link-email.tsx`
  - `backend/app/services/email_service.py`

- Tests:
  - `backend/tests/routers/test_auth.py`
  - `frontend/app/verify/page.test.tsx` (or co-located verify flow test file)

### Previous Story Intelligence (3.1)

- Keep the consent contract strict end-to-end: Story 3.1 patch added backend rejection for missing consent and timezone-safe consent timestamp validation.
- Preserve redirect semantics in Server Actions: Story 3.1 fixed redirect propagation (`isRedirectError`) and this pattern should be reused in verify action handling.
- Reuse environment precedence pattern from Story 3.1 (`API_URL` server-side with safe fallback), avoid leaking internal URLs to browser.
- Continue using shared error message mappings instead of static inline fallback text.

### Git Intelligence Summary

- Recent implementation concentrated in:
  - `backend/app/routers/auth.py`, `backend/app/models/auth.py`, `backend/tests/routers/test_auth.py`
  - `frontend/app/actions/submit-run.ts`, `frontend/app/research/page.tsx`
  - `supabase/migrations/20260319_002_magic_link_tokens.sql`
- Recommended path: extend these same modules for 3.2 to maintain continuity and avoid duplicate auth flow logic.

### Latest Tech Information

- Project-pinned stack is already current for this codebase context and should be followed as-is:
  - Next.js 16.2.0, React 19.2.4, FastAPI 0.135.1, Pydantic v2, Supabase Python 2.28.2, Resend 2.25.0.
- Do not introduce alternative auth/session libraries in MVP; magic-link remains stateless with DB token validation.

### References

- Epic story source: `_bmad-output/planning-artifacts/epics.md` (Epic 3, Story 3.2)
- Architecture auth/token decisions: `_bmad-output/planning-artifacts/architecture.md` (Data Architecture, Authentication & Security, API & Communication Patterns)
- PRD requirements: `_bmad-output/planning-artifacts/prd.md` (FR6, FR21, NFR3, NFR8, NFR11)
- UX verification/error expectations: `_bmad-output/planning-artifacts/ux-design-specification.md` (User Journey Flows, Microcopy Patterns, Feedback Patterns)
- Prior implementation context: `_bmad-output/implementation-artifacts/3-1-email-capture-with-gdpr-consent-and-db-check.md`
- Project-wide rules: `_bmad-output/project-context.md`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- Create-story context generation only (no implementation commands executed).

### Completion Notes List

- Story context assembled from epics, architecture, PRD, UX spec, project context, previous story learnings, and recent git history.
- Implementation guardrails added for token lifecycle, error semantics, UX behavior, and file-level integration points.
- Story prepared for direct handoff to `dev-story` workflow.

### File List

- _bmad-output/implementation-artifacts/3-2-magic-link-generation-and-verification-flow.md
