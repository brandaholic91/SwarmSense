# Story 3.1: Email Capture with GDPR Consent & DB Check

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a visitor,
I want to enter my email address after submitting my research query and give consent to data processing,
so that the system can deliver my results and I know exactly what I'm agreeing to.

## Acceptance Criteria

1. Given a visitor has submitted the research form, when the email capture field appears inline, then an email input field is visible with the label "Email cím" and microcopy "Az eredményed erre az emailre érkezik".
2. Given the email capture step is visible, when the visitor views the form, then a GDPR consent checkbox is visible — never pre-checked — with an explicit label containing inline links to the Privacy Policy and Terms of Service (FR9, FR31, FR32).
3. Given the email capture form is visible, when the visitor has not filled the email field or checked the consent checkbox, then the Submit button is disabled with `aria-disabled="true"` until the email field is filled and the checkbox is checked.
4. Given the Privacy Policy or Terms of Service links are present, when the visitor clicks either link, then the link opens in a new tab.
5. Given a visitor submits a valid email with consent checked, when the Server Action calls `POST /api/v1/auth/check-email`, then the email is normalized (`.lower().strip()`) at the FastAPI input boundary before any DB operation.
6. Given the email DB check returns a result, when the email is new (not in `users` table or no completed run), then the frontend receives a success signal to continue to magic link generation (Story 3.2).
7. Given the email DB check returns a result, when the email is already in the `users` table with a completed run, then the frontend redirects to `/blocked`.
8. Given migration `20260319_002_magic_link_tokens.sql` is applied, when the schema is checked, then the `magic_link_tokens` table exists with: `token` (UUID PK), `user_id` (FK → users.id), `expires_at` (timestamptz), `used_at` (timestamptz null), `created_at` (timestamptz default now()), and RLS is active on `magic_link_tokens` (service role only).

## Tasks / Subtasks

- [ ] Create Supabase migration `supabase/migrations/20260319_002_magic_link_tokens.sql` (AC: 8)
  - [ ] Define `magic_link_tokens` table with: `token` UUID PK, `user_id` FK → users.id, `expires_at` timestamptz, `used_at` timestamptz null, `created_at` timestamptz default now()
  - [ ] Enable RLS on `magic_link_tokens` with policy allowing service role only
  - [ ] Push migration to local Supabase via `supabase db push`
- [ ] Implement `POST /api/v1/auth/check-email` FastAPI endpoint (AC: 5, 6, 7)
  - [ ] Add `backend/app/routers/auth.py` router with `EmailCheckRequest` Pydantic model
  - [ ] Normalize email at input boundary: `.lower().strip()`
  - [ ] Query `users` table for existing email; check if any completed run exists (via `runs` table with `status IN ('completed', 'partial')`)
  - [ ] Return `{"status": "new"}` for new users or `{"status": "returning", "redirect_to": "/blocked"}` for users with completed runs
  - [ ] Register router in `backend/app/main.py` under `/api/v1/auth` prefix
- [ ] Wire Server Action in `frontend/app/actions/submit-run.ts` (AC: 5, 6, 7)
  - [ ] After research form submit, call `POST /api/v1/auth/check-email` with the email and consent data
  - [ ] Handle `status: "new"` → continue to Story 3.2 magic link flow
  - [ ] Handle `status: "returning"` → redirect to `/blocked` via `redirect("/blocked")`
  - [ ] Pass `has_consent=true` and `consent_timestamp=now()` with the email check (consent stored in Story 3.2)
- [ ] Wire GDPR checkbox and submit button behavior in the existing email capture scaffold (AC: 1, 2, 3, 4)
  - [ ] Ensure GDPR checkbox is never pre-checked
  - [ ] Ensure Submit button is disabled until email field is non-empty AND checkbox is checked
  - [ ] Privacy Policy and Terms of Service links open in new tab (`target="_blank" rel="noopener"`)
  - [ ] All Hungarian strings sourced from `frontend/lib/messages.ts` (no hardcoded strings)
- [ ] Add tests for auth check-email endpoint (AC: 5, 6, 7)
  - [ ] Create `backend/tests/routers/test_auth.py` with pytest cases
  - [ ] Test: normalized email stored correctly (lowercase, trimmed)
  - [ ] Test: new email returns `status: "new"`
  - [ ] Test: returning user with completed run returns `status: "returning"` with redirect signal
  - [ ] Test: invalid email format returns 422 validation error
- [ ] Accessibility and UX validation (AC: 1, 2, 3, 4)
  - [ ] Verify email input has visible `<label>` element
  - [ ] Verify checkbox is keyboard accessible and not pre-checked
  - [ ] Verify external links have `rel="noopener"` for security
  - [ ] Verify submit button disabled state uses `aria-disabled="true"`

## Dev Notes

- **UI scaffold already exists:** Story 2.2 created an inline email capture scaffold in `frontend/app/page.tsx`. This story wires it up with Server Action calls and GDPR compliance. Do NOT rebuild the UI — extend the existing scaffold.
- **GDPR consent storage deferred:** Consent (`has_consent=true`, `consent_timestamp`) is stored when the user record is created in Story 3.2 (magic link generation). This story only captures and validates consent at the frontend; backend consent persistence is Story 3.2's responsibility.
- **Email normalization rule:** `.lower().strip()` at FastAPI input boundary — never in frontend. Normalize before any DB query or comparison.
- **Returning user definition:** A user is "returning with completed run" if their email exists in `users` AND there is at least one run with `status IN ('completed', 'partial')` associated with that `user_id`. Users who submitted but never completed a run are treated as new.
- **RLS on magic_link_tokens:** Service role only. No user-facing access to token table. Token validation in Story 3.2 uses the Supabase service role key server-side.
- **Error handling:** 422 for validation errors (Pydantic), 500 for server errors. No custom error codes needed at this endpoint — the response shape is `{status: "new"}` or `{status: "returning", redirect_to: "/blocked"}`.
- **No magic link sent yet:** Story 3.1 is the DB check only. Magic link email generation is Story 3.2.
- **Privacy Policy and Terms of Service:** FR31 and FR32 require these links at the email capture step. Placeholder pages at `/privacy` and `/terms` can be simple static pages — actual content is out of scope for MVP.

### Project Structure Notes

- Migration file: `supabase/migrations/20260319_002_magic_link_tokens.sql`
- Backend router: `backend/app/routers/auth.py` (new file; register in `main.py`)
- Backend models: `backend/app/models/auth.py` (EmailCheckRequest, EmailCheckResponse)
- Server Action update: `frontend/app/actions/submit-run.ts` (extend existing)
- Email capture UI extension: `frontend/app/page.tsx` (extend existing scaffold from Story 2.2)
- Privacy/Terms pages: `frontend/app/privacy/page.tsx`, `frontend/app/terms/page.tsx`
- Tests: `backend/tests/routers/test_auth.py`

### References

- Epic 3 Story 3.1 acceptance criteria: `_bmad-output/planning-artifacts/epics.md#Story 3.1`
- FR coverage: FR4 (email capture), FR5 (email DB check), FR9 (GDPR consent), FR31 (Privacy Policy link), FR32 (Terms of Service link)
- UI scaffold exists from: `_bmad-output/implementation-artifacts/2-2-research-query-submission-form.md`
- Architecture: `_bmad-output/planning-artifacts/architecture.md#API & Communication Patterns` (Server Actions), `_bmad-output/planning-artifacts/architecture.md#Data Architecture` (token storage)
- UX patterns: `_bmad-output/planning-artifacts/ux-design-specification.md#GDPR checkbox` and `_bmad-output/planning-artifacts/ux-design-specification.md#Microcopy Patterns`
- Previous story (form scaffold): `_bmad-output/implementation-artifacts/2-2-research-query-submission-form.md` — Story 2.2 created the email capture scaffold; this story wires it up.
- Next story context: Story 3.2 builds on this — `POST /api/v1/auth/check-email` returns `status: "new"` and the frontend calls `POST /api/v1/auth/magic-link` to generate and email the token.

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

