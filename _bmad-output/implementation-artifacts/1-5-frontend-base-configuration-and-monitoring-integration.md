# Story 1.5: Frontend Base Configuration & Monitoring Integration

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want shared design tokens, Hungarian string constants, error mappings, and monitoring configured across both frontend and backend,
so that all subsequent components have a single source of truth for visual tokens, copy, and error handling and production errors are captured automatically.

## Acceptance Criteria

1. Given the Next.js frontend project, when the base configuration files are in place, then `frontend/lib/tokens.ts` exports color constants for: `background` (zinc-950), `surface` (zinc-900), `border` (zinc-800), `textPrimary` (zinc-50), `textSecondary` (zinc-400), `accent` (amber-400), `stanceReject` (rose-400), `stanceSupport` (emerald-400), `stanceConditional` (amber-400).
2. `frontend/lib/messages.ts` exports a `messages` object with keys for all user-visible Hungarian strings (at minimum: email capture, waiting screen, blocking screen, error states, PII warning).
3. `frontend/lib/errors.ts` exports an `errorMessages` mapping from API error codes (`COST_LIMIT_REACHED`, `TOKEN_EXPIRED`, `TOKEN_INVALID`) to Hungarian user-facing strings.
4. `frontend/app/globals.css` defines CSS custom properties for all tokens via `@layer base`.
5. `frontend/app/layout.tsx` has `<html lang="hu">` on the root element.
6. Sentry is initialized in `frontend/app/layout.tsx` with the DSN from `NEXT_PUBLIC_SENTRY_DSN`.
7. Sentry is initialized in `backend/app/main.py` with the DSN from `SWARMSENSE_SENTRY_DSN`.
8. The Plausible Analytics script tag is present in `frontend/app/layout.tsx`.
9. Both `.env.example` files list every required variable with placeholder values.

## Tasks / Subtasks

- [x] Create shared design tokens (AC: 1, 4)
  - [x] Add `frontend/lib/tokens.ts` exporting the required color constants; use Tailwind color values (e.g., `tailwindcss/colors`) so the tokens resolve to actual hex values for React Email.
  - [x] Add matching CSS custom properties in `frontend/app/globals.css` under `@layer base :root { ... }` with stable names (e.g., `--background`, `--surface`, `--border`, `--text-primary`, `--text-secondary`, `--accent`, `--stance-reject`, `--stance-support`, `--stance-conditional`).
  - [x] Ensure all tokens are usable by both browser UI and React Email templates (no CSS-only values without TS constants).
- [x] Centralize Hungarian copy (AC: 2)
  - [x] Create `frontend/lib/messages.ts` with a `messages` object that includes required microcopy: email capture notice, waiting screen state labels, blocking screen headline, PII warning, reflection question, and other funnel copy defined in UX patterns.
  - [x] Keep Hungarian text only in `messages.ts` (no hard-coded UI strings in components).
- [x] Centralize API error mappings (AC: 3)
  - [x] Create `frontend/lib/errors.ts` exporting `errorMessages` for `COST_LIMIT_REACHED`, `TOKEN_EXPIRED`, `TOKEN_INVALID`.
  - [x] Use the exact Hungarian cost-limit message from Story 1.3 for `COST_LIMIT_REACHED`.
- [x] Monitoring + analytics wiring (AC: 5, 6, 7, 8)
  - [x] Update `frontend/app/layout.tsx` to include `<html lang="hu">`, initialize Sentry with `NEXT_PUBLIC_SENTRY_DSN`, and include the Plausible script tag (use env-driven `data-domain` rather than hard-coding a domain).
  - [x] Initialize Sentry in `backend/app/main.py` using `SWARMSENSE_SENTRY_DSN` from backend settings; keep init minimal (no performance tracing requirements in MVP).
- [x] Environment variable examples (AC: 9)
  - [x] Update `frontend/.env.example` to include `NEXT_PUBLIC_SENTRY_DSN`, `NEXT_PUBLIC_PLAUSIBLE_DOMAIN`, and any existing frontend runtime variables (e.g., `NEXT_PUBLIC_API_URL`).
  - [x] Update `backend/.env.example` to include `SWARMSENSE_SENTRY_DSN` alongside existing required variables (`SWARMSENSE_SUPABASE_URL`, `SWARMSENSE_SUPABASE_SERVICE_KEY`, `SWARMSENSE_KIMI_API_KEY`, `SWARMSENSE_OPERATOR_API_KEY`, `SWARMSENSE_FRONTEND_ORIGIN`).

## Dev Notes

- Design tokens must be a single source of truth shared by browser UI and React Email templates (`frontend/lib/tokens.ts`). Use hex values, not class names, for email compatibility.
- All Hungarian user-facing copy must live in `frontend/lib/messages.ts` (do not hard-code strings in components or email templates).
- Error responses from FastAPI include a `code` field; map these in `frontend/lib/errors.ts` to Hungarian messages.
- Use the High Contrast Impact direction: zinc/amber base, stance colors (rose/emerald/amber) as specified in UX requirements.
- Respect the established project structure and naming conventions; do not introduce new directories for these files.

### Project Structure Notes

- Frontend shared constants live in `frontend/lib/` (`tokens.ts`, `messages.ts`, `errors.ts`).
- Global CSS tokens belong in `frontend/app/globals.css` under `@layer base`.
- Root layout updates are in `frontend/app/layout.tsx`.
- Backend monitoring init belongs in `backend/app/main.py` with settings loaded from `backend/app/core/config.py`.

### References

- `_bmad-output/planning-artifacts/epics.md#Story 1.5` (AC list, tokens/messages/errors, Sentry + Plausible, .env examples)
- `_bmad-output/planning-artifacts/epics.md#Additional Requirements` (tokens.ts, messages.ts, errors.ts single sources)
- `_bmad-output/planning-artifacts/epics.md#UX Design Requirements` (UX-DR1, UX-DR10, UX-DR11, UX-DR12)
- `_bmad-output/planning-artifacts/architecture.md#Monitoring` (Sentry + Plausible integration points)
- `_bmad-output/planning-artifacts/architecture.md#Implementation Patterns & Consistency Rules` (Hungarian text rule, shared tokens)
- `_bmad-output/planning-artifacts/architecture.md#Project Structure & Boundaries` (file paths for frontend/backend)
- `_bmad-output/implementation-artifacts/1-3-fastapi-core-application-and-api-cost-enforcement-middleware.md` (cost-limit error copy, env var list patterns)

## Dev Agent Record

### Agent Model Used

openai/gpt-5.2-codex

### Debug Log References

- 2026-03-20: `python -m pip install -r requirements.txt` (backend)
- 2026-03-20: `python -m pytest` (backend, 11 passed)

### Completion Notes List

- Added shared tokens/messages/errors constants, updated global CSS tokens, and wired frontend Sentry + Plausible.
- Added backend Sentry settings + init with tests, plus new .env example files for both apps.

### File List

- backend/.env.example
- backend/app/core/config.py
- backend/app/main.py
- backend/requirements.txt
- backend/tests/test_sentry.py
- frontend/.env.example
- frontend/app/globals.css
- frontend/app/layout.tsx
- frontend/lib/errors.ts
- frontend/lib/messages.ts
- frontend/lib/tokens.ts
- frontend/next.config.ts
- frontend/package.json
- frontend/sentry.client.config.ts
- frontend/sentry.server.config.ts
- _bmad-output/implementation-artifacts/sprint-status.yaml

### Change Log

- 2026-03-20: Added shared frontend tokens/messages/error mappings, wired Sentry + Plausible, added backend Sentry init + tests, and refreshed env examples; marked story ready for review.
- 2026-03-20: Code review patches applied (claude-sonnet-4-6):
  - P-1: Moved frontend Sentry init to sentry.client.config.ts + sentry.server.config.ts; wrapped next.config.ts with withSentryConfig; removed Sentry.init() from layout.tsx
  - P-2: Added sentry_sdk.is_initialized() guard to _init_sentry() helper extracted from create_app()
  - P-3: Changed sentry_dsn field type from str|None to AnyHttpUrl|None for startup validation
  - P-4: Removed duplicate @layer base :root token block from globals.css
  - P-5: Replaced tailwindcss/colors import in tokens.ts with hardcoded hex values (React Email + Tailwind v4 compatibility)
  - P-6: Rewrote test_sentry.py to test _init_sentry() directly, eliminating fragile importlib.reload pattern
  - P-7: Added JSDoc interpolation notices to template strings in messages.ts
  - P-8: Added genericError key to messages.ts
  - P-9: Added SWARMSENSE_ENVIRONMENT to backend/.env.example
