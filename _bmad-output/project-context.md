---
project_name: 'SwarmSense'
user_name: 'Balazs'
date: '2026-03-20'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'quality_rules', 'workflow_rules', 'anti_patterns']
status: 'complete'
rule_count: 53
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

**Frontend:** Next.js 16.2.0 (App Router), React 19.2.4, TypeScript strict, Tailwind CSS ^4, shadcn/ui ^4.1.0, Vitest ^2.1.8

**Backend:** FastAPI 0.135.1, Pydantic-settings 2.10.1, Supabase 2.28.2, Resend 2.25.0, Sentry SDK 2.20.0, Python 3.12+, pytest 8.4.2

**Critical:** Tailwind v4 uses PostCSS plugin — NO tailwind.config.js class list. Next.js 16.2 has breaking changes vs training data — read `node_modules/next/dist/docs/` before writing any Next.js code.

---

## Critical Implementation Rules

### Language-Specific Rules

**TypeScript:**
- Strict mode enabled — no `any`, no implicit `any`, no non-null assertions without justification
- Path alias `@/*` maps to `frontend/` root — always use `@/` imports, never relative `../`
- `moduleResolution: "bundler"` — do NOT use `.js` extension in imports
- Vitest globals enabled — no need to import `describe`/`it`/`expect` in test files
- Component exports are named (not default) — except Next.js App Router pages (MUST be default exports)
- Use `import type { Foo }` for type-only imports
- Inline style objects with dynamic values require `CSSProperties` type from React

**Python:**
- Python 3.12+ — use `list[str]` not `List[str]`, `str | None` not `Optional[str]`
- Pydantic v2 syntax — `model_config = ConfigDict(...)` not inner class `Config`
- All settings via `pydantic-settings` `BaseSettings` in `core/config.py` — never `os.environ` directly
- All backend env vars prefixed with `SWARMSENSE_`
- Email addresses normalized at FastAPI input boundary only: `.lower().strip()`
- `snake_case` for all functions, variables, file names (PEP8)
- Async endpoints: `async def`; sync endpoints: `def` — do not mix arbitrarily

### Framework-Specific Rules

**Next.js / React:**
- App Router pages in `app/` — `page.tsx` (default export), `layout.tsx`; route folders use `kebab-case` / `[snake_case]` params
- Server Actions in `app/actions/` — required for all calls involving API keys (never expose secrets to browser)
- Status polling: TanStack Query `useQuery` with `refetchInterval: 5000` — no custom polling loops
- TanStack state: use `isLoading` (initial load), `isFetching` (background refetch), `isError` — never add parallel custom `loading: boolean` state
- Stop polling when `status === 'completed' || status === 'partial' || status === 'failed'`
- Local UI state only via React `useState` — no Zustand or other global client state store
- No Supabase client in frontend — all DB operations via FastAPI
- Form validation fires on blur, not on keystroke — errors appear below field, never as toast
- Submit button `disabled` until all required fields filled and GDPR checkbox checked

**FastAPI:**
- Global API prefix: `/api/v1`
- Endpoints: plural nouns, lowercase, kebab-case (`/runs`, `/magic-link`, `/qualifier-responses`)
- Error format: `{ "detail": "...", "code": "ERROR_CODE" }` — codes defined in `core/errors.py`
- CORS restricted to Vercel frontend domain only
- Operator routes use `Security(HTTPBearer())` dependency
- BackgroundTasks for async run processing — no job queue in MVP
- OpenAPI docs (`/docs`) disabled in production
- Cost enforcement middleware must execute before any LLM call dispatch

### Testing Rules

**Frontend (Vitest + React Testing Library):**
- Test files co-located next to source: `ComponentName.test.tsx` alongside `ComponentName.tsx`
- Test setup file: `frontend/test/setup.ts` — auto-imported via vitest.config.ts
- Vitest globals enabled — no explicit imports for `describe`/`it`/`expect`
- Query components via `screen.getByLabelText` — components MUST expose `aria-label` props
- Assert inline CSS using `toHaveStyle()` with token constants from `@/lib/tokens` — never hard-code hex values in tests
- `jest-axe` available for accessibility assertions on page-level components
- jsdom environment — mock any browser APIs not available in jsdom

**Backend (pytest):**
- Tests in `backend/tests/` mirroring `app/` structure: `tests/routers/`, `tests/services/`
- Shared fixtures in `tests/conftest.py` (test Supabase setup, etc.)
- Test files named `test_{module}.py`
- Run from `backend/` directory: `pytest`

**General:**
- No snapshot tests — assert specific behavior, not rendered markup
- All tests must pass before a story is marked complete

### Code Quality & Style Rules

**Naming Conventions:**
- Components: `PascalCase` filename and named export (`PersonaCard.tsx`) — pages are default exports
- App Router folders: `kebab-case`; route params: `[snake_case]` (`[run_id]`)
- Custom hooks: `use` prefix camelCase (`useRunStatus`)
- Utility functions: `camelCase`; constants: `UPPER_SNAKE_CASE`
- Frontend browser-accessible env vars: `NEXT_PUBLIC_` prefix only — never for API keys
- Backend files/functions/vars: `snake_case`; Pydantic models: `PascalCase` (`RunCreate`, `PersonaResponse`)
- DB tables: `snake_case` plural; columns: `snake_case`; FKs: `{table_singular}_id`
- Supabase migration files: `YYYYMMDDNNN_description.sql` (example: `20260319007_followup_tracking.sql`) — no underscore after date block

**Design Tokens:**
- All color values defined in `frontend/lib/tokens.ts` as hardcoded hex constants
- Always import token constants for colors — never Tailwind color classes for dynamic/conditional colors
- `tokens.ts` shared by browser components AND React Email templates — keeps inline CSS in sync
- Must stay in sync with CSS custom properties in `app/globals.css`

**Styling:**
- Tailwind utility classes for layout/spacing/typography
- Inline `style={{}}` with token constants for colors (required for React Email compatibility)
- Use `cn()` from `@/lib/utils` for conditional class merging

**Code Organization:**
- shadcn/ui components copied into `components/ui/` — do not modify generated shadcn files
- Custom components in `components/` (not `ui/`)
- All shared utilities in `lib/` — no utility functions inside component files

### Development Workflow Rules

**Local Development:**
- Frontend: `cd frontend && pnpm dev` (Turbopack, http://localhost:3000)
- Backend: `cd backend && fastapi dev app/main.py` (Uvicorn reload, http://localhost:8000)
- Supabase local: `supabase start`
- Package manager: `pnpm` for frontend — never `npm` or `yarn`

**Environment Variables:**
- Frontend: `.env.local` (gitignored) — copy from `.env.example`
- Backend: `.env` (gitignored, Hetzner VPS) — copy from `.env.example`
- Never commit `.env.local` or `.env`

**CI/CD:**
- `ci.yml` on every PR: ESLint + TypeScript check (frontend), pytest (backend)
- `deploy.yml` on main merge: Docker build → ghcr.io → SSH Hetzner → `docker compose pull && up -d`
- Vercel auto-deploys frontend on main merge

**Git:**
- Branch naming: `epic-{n}` for epic branches
- Stories implemented on epic branch, merged to `main` when epic complete
- PRs require CI pass before merge

### Critical Don't-Miss Rules

**MUST NOT do:**
- No Supabase client in any frontend file — all DB reads/writes via FastAPI
- No `camelCase` JSON field names at API boundary — `snake_case` throughout
- No hardcoded Hungarian text in components, hooks, or email templates — always import from `frontend/lib/messages.ts`
- No hardcoded color values — always import from `@/lib/tokens`
- No new run status strings — only canonical values: `queued`, `running`, `composing`, `completed`, `partial`, `failed`
- No `NEXT_PUBLIC_` prefix for API keys or secrets
- Do not modify files in `components/ui/` (shadcn-generated) — create new files in `components/`
- No custom polling logic when TanStack Query `refetchInterval` satisfies the requirement

**Run Status Enum (identical in DB, backend, and frontend):**
`queued` | `running` | `composing` | `completed` | `partial` | `failed`

**API Response Format:**
- Success: direct body, no envelope: `{ "run_id": "...", "status": "queued" }`
- Error: `{ "detail": "...", "code": "TOKEN_EXPIRED" }`
- Dates: ISO 8601 strings only (`2026-03-19T14:30:00Z`) — no Unix timestamps

**Security:**
- Supabase service role key only in FastAPI — never in frontend or exposed via Server Actions
- CORS restricted to Vercel frontend domain

**Persona Engine:**
- `asyncio.Semaphore` required in `persona_engine.py` to cap concurrent LLM calls per run
- `≥12 personas` → `status: partial`; `<12` → `status: failed` + Sentry alert
- Cost enforcement checked before every LLM call dispatch

**React Email:**
- Email templates in `frontend/emails/` use inline CSS only — no Tailwind, no CSS modules
- Import all colors from `@/lib/tokens` (hardcoded hex) for email client compatibility

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Update this file if new patterns emerge during implementation

**For Humans:**
- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Review periodically for outdated rules
- Remove rules that become obvious over time

Last Updated: 2026-03-21
