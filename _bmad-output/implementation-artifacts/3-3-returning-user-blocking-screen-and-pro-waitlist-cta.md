# Story 3.3: Returning User Blocking Screen & Pro Waitlist CTA

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a returning user who has already used the free analysis,
I want to see a clear, informative message explaining why I cannot run another free analysis,
so that I understand my options and can join the Pro waitlist if I'm interested in continued access.

## Acceptance Criteria

1. Given a returning user submits their email and the DB check confirms their free run has been used, when they are redirected to `/blocked`, then the `BlockingScreen` component is displayed with `role="main"` and the heading: "Ez az emailcim mar igenybe vette az ingyenes probat".
2. Given a returning user is on `/blocked`, when they view available actions, then a single primary CTA button is visible: "Iratkozz fel az ertesitore" (a `<button>` element, not a link), and no competing actions are shown.
3. Given a returning user clicks the waitlist CTA, when the Server Action calls `POST /api/v1/waitlist`, then migration `20260319_005_waitlist.sql` has created `waitlist` with columns `id` (UUID PK), `email` (text unique not null), `created_at` (timestamptz default now()).
4. Given the waitlist submit API is called, when the email is processed, then the email and timestamp are stored in `waitlist` (FR35).
5. Given the email is already present in `waitlist`, when the submit API is called again, then no duplicate is created and the frontend still transitions to `waitlist-submitted` confirmation state in Hungarian.

## Tasks / Subtasks

- [x] Build blocked-state UX with dedicated component and single CTA (AC: 1, 2)
  - [x] Create `frontend/components/blocking-screen.tsx` with two explicit states: `default` and `waitlist-submitted`
  - [x] Ensure root element uses `role="main"` and heading/description copy is sourced from `frontend/lib/messages.ts`
  - [x] Keep exactly one primary CTA button in `default` state; replace button with confirmation copy in `waitlist-submitted`
  - [x] Remove/replace current "back to homepage" behavior in `frontend/app/blocked/page.tsx` so screen is conversion-focused

- [x] Carry returning-user email into blocked flow without exposing new client-side DB access (AC: 1, 2, 4)
  - [x] Update `frontend/app/actions/submit-run.ts` returning branch to redirect with deterministic handoff contract (recommended: `/blocked?email=...`)
  - [x] Parse and validate email on `frontend/app/blocked/page.tsx`; if missing/invalid, render safe error state and disable waitlist submit
  - [x] Do not introduce frontend Supabase client usage; all persistence remains backend API only

- [x] Implement waitlist submission endpoint and schema (AC: 3, 4, 5)
  - [x] Add migration `supabase/migrations/20260319_005_waitlist.sql` with `waitlist` table (`id`, `email`, `created_at`) and unique email constraint
  - [x] Add backend model(s) in `backend/app/models/waitlist.py` (`WaitlistSignupRequest`, `WaitlistSignupResponse`) with input-boundary email normalization
  - [x] Add `POST /api/v1/waitlist` in `backend/app/routers/waitlist.py` using service-role Supabase client
  - [x] Ensure duplicate emails are idempotent success (`status: "already_joined"` or equivalent stable success contract) instead of 500
  - [x] Register waitlist router in `backend/app/main.py` under global `/api/v1` convention

- [x] Implement server action and blocked page integration (AC: 2, 4, 5)
  - [x] Add `frontend/app/actions/join-waitlist.ts` to call `POST /api/v1/waitlist` with `cache: "no-store"`
  - [x] Keep API payload and response fields in `snake_case`
  - [x] On successful submit (new or duplicate), transition UI to `waitlist-submitted` state and keep single-focus screen
  - [x] Map backend errors to Hungarian user copy through existing error/message patterns (`frontend/lib/errors.ts`, `frontend/lib/messages.ts`)

- [x] Update copy and message catalog with no hardcoded Hungarian strings (AC: 1, 2, 5)
  - [x] Add `blockingScreen` message group in `frontend/lib/messages.ts` for heading, body, CTA label, and submitted confirmation text
  - [x] Keep wording aligned with UX requirement: informative tone ("mar igenybe vette"), not punitive ("nem jogosult")

- [x] Add automated tests across backend and frontend (AC: 1-5)
  - [x] Backend tests: `backend/tests/routers/test_waitlist.py` for create, duplicate idempotency, invalid email (422), and response shape
  - [x] Frontend tests: `frontend/app/blocked/page.test.tsx` and/or `frontend/components/blocking-screen.test.tsx` for CTA visibility, single-action state, and submitted confirmation transition
  - [x] Server action tests: `frontend/app/actions/join-waitlist.test.ts` for success, duplicate-success behavior, and failure mapping

## Dev Notes

- Reuse existing returning-user gate from Story 3.1/3.2 (`POST /api/v1/auth/check-email`), do not re-implement eligibility logic in Story 3.3.
- Current `frontend/app/blocked/page.tsx` is a static informational page with a back link; replace this with actionable waitlist conversion flow while preserving accessibility and Hungarian-only copy.
- Existing `submitRunAction` already detects returning users and redirects to `/blocked`; this story extends that redirect contract so the blocked page can submit the same email to waitlist without asking user to re-enter it.
- Keep all frontend user-facing text in `frontend/lib/messages.ts`; no inline literals in components.
- Keep backend API error format contract `{ "detail": "...", "code": "..." }` for failure paths.

### Architecture Compliance

- Frontend must not access Supabase directly; DB writes go through FastAPI only.
- API path must follow architecture route conventions (`/api/v1/waitlist`, lowercase/kebab-case).
- JSON field naming remains `snake_case` at boundary.
- Email normalization remains at FastAPI/Pydantic input boundary (`.lower().strip()`).
- Preserve single-action funnel behavior on `/blocked` (one primary CTA, no competing links/buttons).

### File Structure Requirements

- Frontend page integration: `frontend/app/blocked/page.tsx`
- Frontend component: `frontend/components/blocking-screen.tsx`
- Frontend server action: `frontend/app/actions/join-waitlist.ts`
- Backend router: `backend/app/routers/waitlist.py`
- Backend model: `backend/app/models/waitlist.py`
- Migration: `supabase/migrations/20260319_005_waitlist.sql`
- Tests: `backend/tests/routers/test_waitlist.py`, `frontend/app/blocked/page.test.tsx`, `frontend/app/actions/join-waitlist.test.ts`

### Testing Requirements

- Backend: `cd backend && pytest`
- Frontend unit/integration: `cd frontend && pnpm test`
- Frontend static checks: `cd frontend && pnpm lint`
- If migration is added: validate local schema with `supabase db push` and confirm unique-email behavior for duplicate inserts.

### Previous Story Intelligence (3.2)

- Reuse redirect propagation guard (`isRedirectError`) pattern in async action flows.
- Keep auth/waitlist handoff server-side and deterministic; avoid stateful client workarounds.
- Continue using shared error mapping and message catalog rather than inline fallback strings.
- Preserve recent auth hardening patterns (idempotency, defensive server errors, normalized email inputs).

### Git Intelligence Summary

- Recent commits concentrated around auth flow modules and `frontend/app/blocked/page.tsx`; Story 3.3 should extend these existing touchpoints instead of introducing parallel flow files.
- Most relevant changed files from last commits: `backend/app/routers/auth.py`, `backend/app/models/auth.py`, `frontend/app/actions/submit-run.ts`, `frontend/app/blocked/page.tsx`, `frontend/lib/messages.ts`, `backend/tests/routers/test_auth.py`.

### Latest Tech Information

- Use project-pinned stack and rules from `_bmad-output/project-context.md` (Next.js 16.2, React 19, FastAPI 0.135.1, Pydantic v2, Supabase Python 2.28.2).
- No additional framework/library introduction required for this story.

### References

- Epic source and AC: `_bmad-output/planning-artifacts/epics.md` (Epic 3, Story 3.3)
- Architecture API/data rules: `_bmad-output/planning-artifacts/architecture.md`
- UX blocking-screen behavior and microcopy: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Product requirements mapping: `_bmad-output/planning-artifacts/prd.md` (FR7, FR8, FR35)
- Prior implementation context: `_bmad-output/implementation-artifacts/3-1-email-capture-with-gdpr-consent-and-db-check.md`
- Prior implementation context: `_bmad-output/implementation-artifacts/3-2-magic-link-generation-and-verification-flow.md`
- Project-wide guardrails: `_bmad-output/project-context.md`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- `git log -5 --oneline`
- `git log -5 --name-only --pretty=format:'%h %s'`
- `pytest`
- `pnpm test`
- `pnpm lint`
- `supabase db push` (fails locally without linked project ref)

### Completion Notes List

- Story context created with implementation guardrails for frontend blocked conversion flow, backend waitlist API/schema, idempotent duplicate handling, and required tests.
- Status set to `ready-for-dev`.
- Replaced static blocked page with conversion-focused `BlockingScreen` that enforces single CTA in `default` state and confirmation-only `waitlist-submitted` state, with all user copy sourced from `messages.blockingScreen`.
- Extended returning-user handoff in `submitRunAction` to deterministic `/blocked?email=...` redirect, then validated/normalized query email on blocked page and disabled submit for invalid/missing handoff.
- Added waitlist persistence path end-to-end: Supabase migration `20260319_005_waitlist.sql`, FastAPI models/router, and `/api/v1/waitlist` idempotent duplicate handling (`already_joined`).
- Added frontend server action `joinWaitlistAction` with `snake_case` payload, `no-store` fetch policy, and backend error-code mapping to Hungarian copy via `frontend/lib/errors.ts`.
- Added tests: backend router coverage (`test_waitlist.py`), blocked page + component UX coverage, and server action behavior coverage (success, duplicate success, error mapping).
- Validation complete: `backend pytest`, `frontend pnpm test`, and `frontend pnpm lint` all pass; `supabase db push` could not run in this environment due missing `supabase link` project ref.

### File List

- _bmad-output/implementation-artifacts/3-3-returning-user-blocking-screen-and-pro-waitlist-cta.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/core/errors.py
- backend/app/main.py
- backend/app/models/waitlist.py
- backend/app/routers/waitlist.py
- backend/tests/routers/test_waitlist.py
- frontend/app/actions/join-waitlist.test.ts
- frontend/app/actions/join-waitlist.ts
- frontend/app/actions/submit-run.ts
- frontend/app/blocked/page.test.tsx
- frontend/app/blocked/page.tsx
- frontend/components/blocking-screen.test.tsx
- frontend/components/blocking-screen.tsx
- frontend/lib/errors.ts
- frontend/lib/messages.ts
- supabase/migrations/20260319_005_waitlist.sql

### Code Review Record

#### Reviewer
claude-sonnet-4-6 (3-layer: Blind Hunter, Edge Case Hunter, Acceptance Auditor)

#### Patches Applied (2026-03-21)
- P1: `backend/app/routers/waitlist.py` — `_is_unique_violation` fallback szűkítve: `"unique" in message` eltávolítva, csak `"duplicate key"` marad
- P2: `backend/app/routers/waitlist.py` — `# pragma: no cover` eltávolítva az except blokk fejlécéről
- P3: `frontend/lib/errors.ts` — `getErrorMessageByCode` fallback generikus üzenetre cserélve (TOKEN_INVALID helyett)
- P4: `frontend/lib/errors.ts` + `frontend/lib/messages.ts` — összes `blockingScreen` szöveg helyes magyar ékezetekkel javítva
- P5: `frontend/app/blocked/page.tsx` — `searchParams.email` tömb típus kezelése hozzáadva
- P6: `supabase/migrations/20260319_005_waitlist.sql` — `waitlist_email_maxlen check (length(email) <= 254)` constraint hozzáadva
- P7: `frontend/app/actions/join-waitlist.ts` — success ág JSON parse try/catch-be csomagolva
- P8: `frontend/app/actions/join-waitlist.ts` — trailing slash levágása az API_URL-ből
- P9: `frontend/components/blocking-screen.test.tsx` — `already_joined` → `waitlist-submitted` átmenet tesztesete hozzáadva (AC5)

#### Deferred Findings (nem javítva, jövőbeli sprint)
- D1: Nincs auth/rate-limiting a `/api/v1/waitlist` endpointon
- D2: `already_joined` válasz user-existence oráklumként működik (enumeration)
- D3: RLS engedélyezve, de nem definiált policy a `waitlist` táblán
- D4: Frontend email regex permisszív (backend validál, alacsony kockázat)

#### Validation After Patches
- `backend pytest`: 4/4 passed
- `frontend pnpm test`: 41/41 passed
- `frontend pnpm lint`: clean

## Change Log

- 2026-03-21: Implemented Story 3.3 blocked conversion flow with waitlist API, migration, deterministic email handoff, and backend/frontend test coverage.
- 2026-03-21: Code review complete. 9 patches applied. Story moved to done.
