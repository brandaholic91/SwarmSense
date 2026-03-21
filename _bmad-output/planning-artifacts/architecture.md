---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-03-19'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/prd-validation-report.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
workflowType: 'architecture'
project_name: 'SwarmSense'
user_name: 'Balazs'
date: '2026-03-19'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
36 functional requirements across 8 categories: query submission (FR1–3),
identity verification & access control (FR4–9, FR35–36), persona engine
(FR10–13), result delivery (FR14–20), user communication (FR21–24),
processing status (FR25), operator & administration (FR26–30), legal &
compliance (FR31–34).

Architecturally, the FRs define three distinct processing paths:
1. New user path: form → email capture → magic link → qualifier → async persona engine → result email delivery
2. Returning user path: form → email check → blocking screen → waitlist CTA
3. Operator path: direct Supabase/Resend/Sentry monitoring access

**Non-Functional Requirements:**
21 NFRs across performance (NFR1–5), security (NFR6–11), reliability (NFR12–15), scalability/cost control (NFR16–19), accessibility (NFR20–21).

Critical NFRs driving architectural decisions:
- NFR2: p95 form→processing-started <2s → async job queue required
- NFR4: p95 result email <120s → parallel execution with timeout handling
- NFR16/17: $50/month hard cap, 80% alert → real-time cost tracking layer
- NFR6: TLS 1.2+ everywhere → Vercel/Railway handle this automatically
- NFR11: Only email stored as PII → minimal data model in MVP

**Scale & Complexity:**
- Primary domain: Full-stack web + async background processing
- Complexity level: Medium
- Estimated architectural components: 8–10 distinct modules
- External service integrations: 7 (MVP), 8 (V2 with Stripe)

### Technical Constraints & Dependencies

- OpenRouter as LLM gateway; Kimi K2 (Moonshot AI) as primary routed model, Claude as optional fallback/premium route
- Supabase EU region (eu-central-1) — non-negotiable for GDPR compliance
- Next.js on Vercel (frontend); FastAPI on Railway (backend)
- Resend for transactional email (magic link + result + follow-up sequences)
- API cost hard cap: $50/month — enforced at FastAPI application layer
- Magic link tokens: 24h expiry, single-use
- OpenRouter and routed model T&C review required pre-launch (prompt training policy disclosure)

### Cross-Cutting Concerns Identified

1. **API cost enforcement**: All run-initiating code paths must check and decrement against the monthly spend counter before dispatching LLM calls
2. **GDPR data isolation**: Zero cross-user data access; email is the only PII stored; consent captured and stored at email submission
3. **Email/browser visual continuity**: Result email shares design tokens (zinc/amber color system) with browser UI; inline CSS required for email client compatibility
4. **Graceful degradation**: Partial results (≥12 personas) must be handled transparently with count disclosure; <12 personas = failed run
5. **Hungarian cultural context**: All LLM prompts and user-facing copy in Hungarian; cultural context embedded in persona generation framework
6. **Token lifecycle management**: Magic link tokens (MVP) → session tokens (V2); data model must accommodate both without migration pain

## Starter Template Evaluation

### Primary Technology Domain

Full-stack web + async background processing — two distinct applications: Next.js frontend and FastAPI backend, deployed separately on Vercel and Railway respectively.

### Starter Options Considered

The PRD explicitly specifies the technology stack, making starter selection straightforward. The key decision is repository structure: monorepo (single repo with `/frontend` and `/backend` directories) vs. separate repositories. For a solo founder with a 1–2 week build, a monorepo minimises context-switching and keeps deployment configuration in one place.

### Selected Starter: Monorepo — create-next-app + FastAPI

**Rationale for Selection:**
- PRD mandates Next.js (Vercel) + FastAPI (Railway) + Supabase; no stack decision required
- Monorepo structure optimizes for solo founder workflow and single git history
- Next.js App Router + Turbopack is the current default and aligns with shadcn/ui component strategy defined in UX spec
- FastAPI file-type structure suits a microservice-scale backend (routers / models / services)

**Initialization Commands:**

```bash
# Repository root
mkdir swarmsense && cd swarmsense && git init

# Frontend
pnpm create next-app@latest frontend
# Select: TypeScript ✓  Tailwind ✓  App Router ✓  Turbopack ✓  ESLint ✓  import alias @/* ✓

cd frontend && pnpm dlx shadcn@latest init
# Select: zinc color theme, dark mode: class-based

# Backend
mkdir ../backend && cd ../backend
python -m venv .venv && source .venv/bin/activate
pip install "fastapi[standard]==0.135.1" supabase resend
```

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**
TypeScript (strict mode) for frontend; Python 3.12+ for backend. Pydantic v2 for request/response validation.

**Styling Solution:**
Tailwind CSS utility-first + shadcn/ui CLI v4 (components copied into `/components/ui/`). Zinc color scale, amber accent, class-based dark mode — matching UX spec direction 4 (High Contrast Impact).

**Build Tooling:**
Turbopack for local development (fast HMR); Next.js production build for Vercel deployment. FastAPI served via Uvicorn inside Docker container on Hetzner VPS.

**Testing Framework:**
Not included in starter — to be added: Vitest + React Testing Library (frontend), pytest (backend). Axe-core accessibility CI integration required by NFR20.

**Code Organization:**

```
swarmsense/
  frontend/
    app/                   # Next.js App Router pages and layouts
    components/
      ui/                  # shadcn/ui + custom components
    lib/                   # utilities, API client
    emails/                # React Email templates (inline CSS)
  backend/
    app/
      main.py
      routers/             # run, auth, operator endpoints
      models/              # Pydantic schemas
      services/            # persona engine, email, cost tracker
      core/                # config, database client, cost enforcement
```

**Development Experience:**
Hot reloading via Turbopack (frontend) and `fastapi dev` (backend). Environment variables: `.env.local` (frontend, gitignored) + `.env` (backend, gitignored); Vercel injects frontend prod env vars; Hetzner VPS uses `.env` file managed via SSH or GitHub Actions secrets.

**Note:** Project initialization using the above commands should be the first implementation story.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Async run processing approach (FastAPI BackgroundTasks)
- Token storage and auth strategy (UUID magic link, RLS-protected)
- Backend deployment target (Hetzner VPS, Docker)
- Frontend ↔ Backend communication pattern

**Important Decisions (Shape Architecture):**
- Email templating (React Email + Resend)
- Frontend state management (TanStack Query)
- DB migration tooling (Supabase CLI)
- Reverse proxy and SSL (Caddy)

**Deferred Decisions (Post-MVP):**
- Caching layer — not required at MVP run volumes
- Job queue (ARQ/Celery) — migrate from BackgroundTasks if job persistence becomes necessary
- Supabase Auth for V2 account system — magic link architecture anticipates this upgrade

### Data Architecture

**Database:** Supabase PostgreSQL, EU region (eu-central-1). Non-negotiable for GDPR compliance.

**Migration strategy:** Supabase CLI (`supabase db push`). SQL migration files committed to repository under `supabase/migrations/`. Enables diff-based schema tracking and CI integration without an additional Python migration tool.

**Core tables (MVP):**
- `users` — verified email, consent flag, consent timestamp, created_at
- `magic_link_tokens` — token (UUID), user_id FK, expires_at, used_at (single-use enforcement)
- `runs` — user_id FK, topic, audience, status, persona_count, cost_usd, created_at, completed_at
- `qualifier_responses` — run_id FK, user_id FK, role_answer, use_case_answer
- `waitlist` — email, created_at
- `cost_tracking` — month (YYYY-MM), total_usd (running counter for hard cap enforcement)

**Token storage:** UUID v4 token stored as plain text in `magic_link_tokens` table, protected by Supabase Row Level Security. Single-use enforced via `used_at` timestamp. 24h expiry via `expires_at`. No bcrypt hashing required given RLS protection and the token's low-value nature (unlocks one free run only).

**Caching:** None in MVP. All reads are single-record lookups by email or run ID — no list views, no aggregations requiring cache.

### Authentication & Security

**MVP auth model:** Stateless magic link. No sessions, no JWTs, no cookies.

Flow: email submitted → UUID token generated → stored in `magic_link_tokens` → token emailed via Resend → user clicks link → FastAPI validates token (exists + not expired + not used) → marks as used → proceeds to qualifier.

**V2 upgrade path:** Supabase Auth (built-in JWT + session management) integrates natively with the existing Supabase schema. Magic link flow in MVP is intentionally compatible — `users` table structure anticipates Supabase Auth's `auth.users` relationship.

**API security:**
- TLS 1.2+ handled by Caddy (automatic HTTPS, NFR6 satisfied)
- Supabase service role key never exposed to frontend — all DB writes go through FastAPI
- CORS: FastAPI `CORSMiddleware` restricted to Vercel frontend domain
- No rate limiting in MVP (volume too low) — add if abuse occurs

**Data isolation:** Supabase RLS policies enforce per-user data access. Non-operator users have no direct DB access — all access via FastAPI endpoints.

### API & Communication Patterns

**API design:** REST. FastAPI auto-generates OpenAPI docs at `/docs` (disabled in production).

**Async run processing:** FastAPI `BackgroundTasks`. Run initiation is synchronous (token validation + DB write + job dispatch), persona engine execution is async background. Rationale: zero infrastructure overhead; at MVP volumes (10–30 runs/day) Railway restart risk is negligible and Sentry captures any failures.

**Upgrade trigger:** If run loss from process restart becomes observable (Sentry alerts), migrate dispatch to ARQ (async Redis queue) — data model is unchanged, only the dispatch call changes.

**Status polling:** `GET /runs/{run_id}/status` endpoint returns current run state. Frontend polls every 5 seconds via TanStack Query `refetchInterval`. No WebSocket or SSE required.

**Frontend ↔ Backend communication:**
- Form submission and status polling: direct HTTPS calls from Next.js client to FastAPI (public endpoints, no secrets involved)
- Email check and magic link generation: Next.js Server Actions call FastAPI with server-side API key — Supabase service role key and LLM API keys never reach the browser
- Result email delivery: FastAPI calls Resend directly (server-to-server)

**Error handling standard:** FastAPI returns structured JSON errors `{ "detail": "...", "code": "..." }`. Frontend maps error codes to Hungarian user-facing messages.

### Frontend Architecture

**State management:** TanStack Query (React Query) for all server state. Rationale: `refetchInterval` handles run status polling natively; loading/error/success states managed automatically; no custom polling logic required.

Local UI state (form inputs, qualifier selections): React `useState` — no global client state store needed.

**Email templating:** React Email. Components (`PersonaCard`, `ConsensusFlag`) are written as React components in `frontend/emails/` and compiled to HTML by React Email's renderer before sending via Resend SDK. Shares zinc/amber color tokens with browser UI via a shared `tokens.ts` constants file. Inline CSS generated automatically for email client compatibility.

**Form handling:** Native React controlled components + shadcn/ui `Input`/`Textarea`/`RadioGroup`. No React Hook Form — the 2-field submission form and 2-question qualifier do not justify the dependency.

**Routing:** Next.js App Router file-based routing. Pages: `/` (landing + form), `/verify` (magic link landing), `/qualifier`, `/waiting/[runId]`, `/blocked` (already-used screen).

### Infrastructure & Deployment

**Backend hosting:** Hetzner VPS, EU region. Docker + docker-compose. Rationale: EU data residency (GDPR-compatible with Supabase EU), cost-effective for solo founder, full control over environment.

**Reverse proxy + SSL:** Caddy. Automatic HTTPS via Let's Encrypt (zero SSL configuration). `Caddyfile` proxies HTTPS traffic to FastAPI container on internal port. Satisfies NFR6 (TLS 1.2+) automatically.

**Container setup:**
```
docker-compose.yml
  services:
    api:        # FastAPI + Uvicorn
    caddy:      # Reverse proxy + SSL termination
```

**Frontend hosting:** Vercel. Next.js native deployment, automatic preview deployments on PRs, zero configuration.

**CI/CD:** GitHub Actions.
- On PR: lint + type-check (frontend), pytest (backend)
- On merge to main: build Docker image → push to GitHub Container Registry (ghcr.io) → SSH to Hetzner → `docker compose pull && docker compose up -d`
- Vercel auto-deploys frontend on main merge independently

**Environment configuration:**
- Frontend: Vercel environment variables (injected at build time / runtime)
- Backend: `.env` file on Hetzner VPS, managed via SSH; secrets also stored as GitHub Actions secrets for CI deploy

**Monitoring:** Sentry (error tracking, API timeout alerts — NFR15). Plausible Analytics (privacy-first, GDPR-compliant, no cookie consent — NFR per PRD). Resend dashboard for email delivery/open rates (FR30).

### Decision Impact Analysis

**Implementation Sequence:**
1. Monorepo init + Docker + Caddy setup (infra foundation)
2. Supabase schema + RLS policies (data layer)
3. FastAPI core: config, DB client, cost enforcement middleware
4. Magic link auth flow: token generation + email + validation
5. Persona engine: parallel LLM calls + BackgroundTasks dispatch
6. Result email: React Email templates + Resend integration
7. Next.js frontend: landing → form → qualifier → waiting → blocked screens
8. Operator monitoring: run log views, cost alert wiring

**Cross-Component Dependencies:**
- Cost enforcement middleware must be in place before persona engine is wired up
- Magic link token validation is a prerequisite for qualifier and run initiation
- React Email token file must be defined before both browser UI and email templates are built
- Supabase RLS policies must be tested before any user-facing endpoint goes to production

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:** 9 areas where AI agents could make different choices without explicit guidance.

### Naming Patterns

**Database Naming Conventions:**
- Tables: `snake_case`, lowercase, plural (`users`, `magic_link_tokens`, `qualifier_responses`, `cost_tracking`)
- Columns: `snake_case` (`user_id`, `created_at`, `expires_at`, `used_at`)
- Foreign keys: `{referenced_table_singular}_id` (`user_id`, `run_id`)
- Indexes: `idx_{table}_{column}` (`idx_users_email`, `idx_runs_user_id`)
- Boolean columns: `is_` or `has_` prefix (`is_used`, `has_consent`)

**API Naming Conventions:**
- Endpoints: plural nouns, lowercase, kebab-case (`/runs`, `/magic-link`, `/qualifier-responses`)
- Route parameters: `{snake_case_id}` (`{run_id}`, `{token}`)
- Query parameters: `snake_case` (`?user_id=...`)
- Global API prefix: `/api/v1`
- Custom headers: `X-Swarmsense-*`

**Frontend Code Naming:**
- Components: `PascalCase` filename and export (`ConsensusFlag.tsx`, `PersonaCard.tsx`)
- App Router pages/folders: `kebab-case` (`/waiting/[run-id]/page.tsx`)
- Utility functions: `camelCase` (`formatPersonaCount`, `buildEmailHtml`)
- Custom hooks: `use` prefix, `camelCase` (`useRunStatus`, `usePollInterval`)
- Constants: `UPPER_SNAKE_CASE` (`MAX_POLL_INTERVAL_MS`)

**Backend Code Naming:**
- Files and modules: `snake_case` (`persona_engine.py`, `cost_tracker.py`)
- Functions and variables: `snake_case` (PEP8)
- Pydantic models: `PascalCase` (`RunCreate`, `PersonaResponse`, `MagicLinkToken`)
- Constants: `UPPER_SNAKE_CASE` (`MAX_PERSONAS`, `MONTHLY_COST_LIMIT_USD`)
- Environment variables: `SWARMSENSE_` prefix (`SWARMSENSE_SUPABASE_URL`, `SWARMSENSE_OPENROUTER_API_KEY`)

**JSON Field Naming (API boundary):**
`snake_case` throughout — backend and frontend both use `snake_case` in JSON. No camelCase transformation at the boundary. Rationale: eliminates serialization middleware and reduces conflict surface.

### Structure Patterns

**Test File Location:**
- Frontend: co-located alongside source files (`ConsensusFlag.test.tsx` next to `ConsensusFlag.tsx`)
- Backend: `backend/tests/` directory mirroring `app/` structure (`tests/routers/test_runs.py`, `tests/services/test_persona_engine.py`)

**Shared Constants:**
- Design tokens (colors, spacing values): `frontend/lib/tokens.ts` — imported by both browser UI components AND React Email templates. Single source of truth.
- API error codes: `backend/app/core/errors.py` (Python Enum) + `frontend/lib/errors.ts` (TypeScript object) — must be kept in sync manually; document sync requirement in both files.

**Environment Variable Naming:**
- Frontend (Vercel): `NEXT_PUBLIC_` prefix only for values that must be accessible in the browser (e.g. `NEXT_PUBLIC_API_URL`). All secrets stay server-side — no `NEXT_PUBLIC_` for API keys.
- Backend (Hetzner VPS `.env`): `SWARMSENSE_` prefix for all project-specific variables.

### Format Patterns

**API Response Formats:**

Success — direct response body, no envelope wrapper:
```json
{ "run_id": "abc123", "status": "queued", "created_at": "2026-03-19T14:30:00Z" }
```

Error — FastAPI default with added `code` field:
```json
{ "detail": "Token lejárt vagy érvénytelen.", "code": "TOKEN_EXPIRED" }
```

**Run Status Enum — canonical values (DB, API, and frontend must use exactly these strings):**
- `queued` → job accepted, not yet started
- `running` → persona API calls in progress
- `composing` → aggregating results
- `completed` → result email sent successfully
- `partial` → ≥12 personas completed, result sent with count noted
- `failed` → <12 personas completed, no result sent

**Date/Time Format:** ISO 8601 strings everywhere (`2026-03-19T14:30:00Z`). No Unix timestamps in API responses. No locale-formatted dates in JSON.

**Email Address Normalization:** Always `.lower().strip()` before DB storage or comparison. Normalization applied at the FastAPI input boundary — never in the frontend.

**Persona Count Display Format:** `"{completed}/{total} persona"` (e.g. `"17/18 persona"`). Used consistently in waiting screen, result email, and operator run log.

### Communication Patterns

**No event system in MVP.** FastAPI BackgroundTasks handles async dispatch. No message queue, no pub/sub, no inter-service events. If ARQ is introduced in a future phase, event naming will follow `verb.noun` pattern (`run.completed`, `email.sent`).

**State Management (TanStack Query):**
- Use `isLoading` for initial load, `isFetching` for background refetch (polling)
- Use `isError` for error state — never introduce parallel custom `loading: boolean` state
- Run status polling: `useQuery` with `refetchInterval: 5000`, stops when `status === 'completed' || status === 'failed' || status === 'partial'`
- No Zustand or other global client state store — server state via TanStack Query, local UI state via `useState`

### Process Patterns

**Error Handling by Layer:**

| Error Type | Backend | Frontend |
|---|---|---|
| Validation error | 422 + Pydantic `detail` array | Inline field error below input |
| Business logic error | 400 + `code` field | Hungarian message from `errors.ts` mapping |
| Auth error | 401 + `TOKEN_EXPIRED` or `TOKEN_INVALID` | Full-screen error + "Új link kérése" CTA |
| Server error | 500 + Sentry capture | "Valami hiba történt" + retry option |
| Cost limit reached | 402 + `COST_LIMIT_REACHED` | Hungarian message: monthly capacity reached |

**Hungarian User-Facing Text Rule:** All user-visible Hungarian strings are defined in `frontend/lib/messages.ts`. AI agents must never hard-code Hungarian text inside React components or email templates — always import from `messages.ts`.

**Form Validation Timing:** On blur, not on keystroke. Error text appears below the field (never as a toast). Submit button is `disabled` until all required fields are filled and GDPR checkbox is checked.

**Graceful Degradation — Partial Results:**
- ≥12 personas completed → `status: "partial"`, result email sent, `persona_count` noted in email and run log
- <12 personas completed → `status: "failed"`, Sentry alert fired, no email sent, run logged with error metadata

### Enforcement Guidelines

**All AI Agents MUST:**
- Use `snake_case` for all JSON field names in API requests and responses
- Use only the canonical run status enum values — never invent new status strings
- Import Hungarian user-facing text from `frontend/lib/messages.ts` — never hard-code strings in components
- Normalize email addresses (`.lower().strip()`) at the FastAPI input boundary only
- Place tests in the designated locations (co-located frontend, `tests/` backend)
- Use `NEXT_PUBLIC_` prefix only for genuinely browser-accessible frontend variables
- Use `SWARMSENSE_` prefix for all backend environment variables

**All AI Agents MUST NOT:**
- Access Supabase directly from the browser (no Supabase client in frontend code) — all DB operations go through FastAPI
- Transform `snake_case` to `camelCase` at the API boundary
- Introduce custom polling logic when TanStack Query `refetchInterval` satisfies the requirement
- Add new run status values without updating the canonical enum in both backend and frontend
- Hard-code Hungarian text in any component, hook, or email template

## Project Structure & Boundaries

### Complete Project Directory Structure

```
swarmsense/
├── .github/
│   └── workflows/
│       ├── ci.yml                     # PR: lint, typecheck, pytest
│       └── deploy.yml                 # main merge: Docker build → ghcr.io → Hetzner SSH
├── .gitignore
├── README.md
│
├── supabase/                          # Supabase CLI project
│   ├── config.toml
│   ├── migrations/
│   │   ├── 20260319_001_users.sql
│   │   ├── 20260319002_magic_link_tokens.sql
│   │   ├── 20260319003_runs.sql
│   │   ├── 20260319004_qualifier_responses.sql
│   │   ├── 20260319005_waitlist.sql
│   │   └── 20260319_006_cost_tracking.sql
│   └── seed.sql
│
├── frontend/                          # Next.js 16.2 — Vercel
│   ├── package.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── .env.local                     # gitignored
│   ├── .env.example
│   │
│   ├── app/
│   │   ├── globals.css                # Tailwind @layer base + CSS custom properties
│   │   ├── layout.tsx                 # root layout, <html lang="hu">
│   │   ├── page.tsx                   # / — landing + 2-field form (FR1-3)
│   │   ├── verify/
│   │   │   └── page.tsx               # /verify — magic link token validation (FR6)
│   │   ├── qualifier/
│   │   │   └── page.tsx               # /qualifier — 2-question survey (FR36)
│   │   ├── waiting/
│   │   │   └── [run_id]/
│   │   │       └── page.tsx           # /waiting/[run_id] — status polling (FR25)
│   │   ├── blocked/
│   │   │   └── page.tsx               # /blocked — already-used + waitlist CTA (FR7-8, FR35)
│   │   └── actions/                   # Next.js Server Actions (sensitive API calls)
│   │       ├── submit-run.ts          # form submission → FastAPI (FR1-4)
│   │       ├── verify-token.ts        # magic link validation → FastAPI (FR6)
│   │       └── join-waitlist.ts       # waitlist signup → FastAPI (FR35)
│   │
│   ├── components/
│   │   ├── ui/                        # shadcn/ui components (copied into project)
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── textarea.tsx
│   │   │   ├── select.tsx
│   │   │   ├── radio-group.tsx
│   │   │   ├── progress.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── checkbox.tsx
│   │   │   └── separator.tsx
│   │   ├── consensus-flag.tsx         # ConsensusFlag — strong-reject/support/split states (FR17)
│   │   ├── persona-card.tsx           # PersonaCard — compact + full variants (FR16)
│   │   ├── waiting-screen.tsx         # WaitingScreen — named progress states (FR25)
│   │   ├── rotating-placeholder.tsx   # RotatingPlaceholder — form field examples (FR2)
│   │   └── blocking-screen.tsx        # BlockingScreen — already-used state (FR7-8)
│   │
│   ├── emails/                        # React Email templates
│   │   ├── magic-link-email.tsx       # Magic link verification email (FR21)
│   │   ├── result-email.tsx           # Analysis result email (FR14-20)
│   │   ├── follow-up-day1.tsx         # Day 1 follow-up (FR22)
│   │   ├── follow-up-day3.tsx         # Day 3 follow-up (FR22)
│   │   └── follow-up-day7.tsx         # Day 7 follow-up (FR22)
│   │
│   └── lib/
│       ├── tokens.ts                  # Design tokens — shared by browser UI AND email templates
│       ├── messages.ts                # ALL Hungarian user-facing strings (single source of truth)
│       ├── errors.ts                  # API error code → Hungarian message mapping
│       ├── api-client.ts              # FastAPI HTTP client (public endpoints)
│       └── utils.ts                   # cn() and shared utilities
│
├── backend/                           # FastAPI 0.135.1 — Hetzner VPS (Docker)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── .env                           # gitignored — managed on VPS via SSH
│   ├── .env.example
│   │
│   ├── app/
│   │   ├── main.py                    # FastAPI app init, CORS, middleware, router registration
│   │   │
│   │   ├── core/
│   │   │   ├── config.py              # Pydantic Settings — all env var parsing
│   │   │   ├── database.py            # Supabase client singleton
│   │   │   ├── cost_enforcement.py    # $50/month hard cap middleware (FR29, NFR16-17)
│   │   │   └── errors.py              # Error code Enum + HTTPException helpers
│   │   │
│   │   ├── routers/
│   │   │   ├── runs.py                # POST /api/v1/runs, GET /api/v1/runs/{run_id}/status
│   │   │   ├── auth.py                # POST /api/v1/auth/check-email, /magic-link, /verify
│   │   │   ├── qualifier.py           # POST /api/v1/qualifier
│   │   │   ├── waitlist.py            # POST /api/v1/waitlist
│   │   │   └── operator.py            # GET /api/v1/operator/runs, /cost, /email-stats
│   │   │
│   │   ├── models/                    # Pydantic v2 request/response schemas
│   │   │   ├── run.py                 # RunCreate, RunStatus, RunResponse
│   │   │   ├── auth.py                # EmailCheckRequest, MagicLinkRequest, TokenVerifyRequest
│   │   │   ├── qualifier.py           # QualifierSubmit, QualifierResponse
│   │   │   ├── waitlist.py            # WaitlistSignup
│   │   │   └── persona.py             # PersonaResponse, PersonaStance (Enum: support/reject/conditional)
│   │   │
│   │   └── services/
│   │       ├── persona_engine.py      # 15–20 parallel LLM calls, attitudinal framework (FR10-13)
│   │       ├── run_processor.py       # BackgroundTask orchestrator: engine → aggregate → email
│   │       ├── email_service.py       # Resend integration: all outbound email (FR14-24)
│   │       ├── cost_tracker.py        # Real-time spend tracking, 80% alert, cap enforcement
│   │       └── llm_client.py          # OpenRouter gateway abstraction; Kimi K2 primary routed model
│   │
│   └── tests/
│       ├── conftest.py                # pytest fixtures, test Supabase setup
│       ├── routers/
│       │   ├── test_runs.py
│       │   ├── test_auth.py
│       │   └── test_qualifier.py
│       └── services/
│           ├── test_persona_engine.py
│           └── test_cost_tracker.py
│
├── docker-compose.yml                 # Hetzner VPS: api + caddy services
└── Caddyfile                          # HTTPS reverse proxy + auto SSL
```

### Architectural Boundaries

**API Boundaries:**

| Boundary | Direction | Auth | Notes |
|---|---|---|---|
| Browser → FastAPI (public) | Client → Server | None | Status polling only (`GET /runs/{run_id}/status`) |
| Browser → Server Action → FastAPI | Client → Next.js server → FastAPI | Server-side API key | Email check, token verify, run submit, waitlist |
| FastAPI → Supabase | Server → Managed DB | Service role key | Never exposed to browser |
| FastAPI → OpenRouter | Server → External API | API key | Via `llm_client.py`, routed model selection handled server-side |
| FastAPI → Resend | Server → External API | API key | All outbound email via `email_service.py` |
| Caddy → FastAPI | VPS internal | None (loopback) | TLS termination at Caddy, HTTP internally |

**Data Flow — Primary User Journey:**
```
Browser form submit
  → Server Action (submit-run.ts)
    → POST /api/v1/auth/check-email  → new: continue | returning: redirect /blocked
    → POST /api/v1/auth/magic-link   → Resend (magic link email)

Magic link click → /verify
  → Server Action (verify-token.ts)
    → POST /api/v1/auth/verify       → token validate + mark used
    → redirect /qualifier

Qualifier submit
  → Server Action
    → POST /api/v1/qualifier         → DB store (linked to run)
    → POST /api/v1/runs              → BackgroundTask dispatched
    → redirect /waiting/{run_id}

BackgroundTask (server-side, async)
  → persona_engine.py               → 15–20 parallel OpenRouter-routed calls
  → run_processor.py                → aggregate results, update run status
  → email_service.py                → Resend (result email)
  → cost_tracker.py                 → update monthly spend counter

Browser polling (/waiting/{run_id})
  → GET /api/v1/runs/{run_id}/status  (every 5s via TanStack Query)
  → stops when status ∈ {completed, partial, failed}
```

### Requirements to Structure Mapping

| FR Category | Backend Location | Frontend Location |
|---|---|---|
| Query submission (FR1–3) | `routers/runs.py` | `app/page.tsx`, `components/rotating-placeholder.tsx` |
| Identity verification (FR4–9, FR35–36) | `routers/auth.py`, `routers/qualifier.py`, `routers/waitlist.py` | `app/verify/`, `app/qualifier/`, `app/blocked/`, `app/actions/` |
| Persona engine (FR10–13) | `services/persona_engine.py`, `services/llm_client.py` | — |
| Result delivery (FR14–20) | `services/email_service.py` | `emails/result-email.tsx` |
| User communication (FR21–24) | `services/email_service.py` | `emails/magic-link-email.tsx`, `emails/follow-up-*.tsx` |
| Processing status (FR25) | `routers/runs.py` (status endpoint) | `app/waiting/[run_id]/`, `components/waiting-screen.tsx` |
| Operator & admin (FR26–30) | `routers/operator.py`, `services/cost_tracker.py` | Supabase dashboard + Sentry + Resend (no custom UI) |
| Legal & compliance (FR31–34) | `core/errors.py` (PII warning), DB consent columns | `lib/messages.ts`, GDPR checkbox in form |

### Integration Points

**External Service Integration:**

| Service | Integration Point | Purpose |
|---|---|---|
| Supabase | `backend/app/core/database.py` | All DB reads/writes |
| OpenRouter API | `backend/app/services/llm_client.py` | LLM gateway for persona generation requests |
| Routed models (Kimi/Claude) | `backend/app/services/llm_client.py` | Primary and fallback model selection behind OpenRouter |
| Resend | `backend/app/services/email_service.py` | All transactional email |
| Sentry | `backend/app/main.py` (init) + frontend `layout.tsx` | Error tracking both sides |
| Plausible | `frontend/app/layout.tsx` (script tag) | Analytics — no backend involvement |

### Development Workflow Integration

**Local development:**
```bash
# Frontend
cd frontend && pnpm dev          # Turbopack, http://localhost:3000

# Backend
cd backend && fastapi dev app/main.py   # Uvicorn reload, http://localhost:8000

# Supabase local
supabase start                   # local Postgres + Studio
```

**CI pipeline (GitHub Actions):**
- `ci.yml`: ESLint + TypeScript check (frontend), pytest (backend) — runs on every PR
- `deploy.yml`: Docker build → push ghcr.io → SSH to Hetzner → `docker compose pull && docker compose up -d` — runs on main merge

**Deployment structure:**
- Frontend: Vercel auto-deploy on main merge (zero config)
- Backend: Docker image built in CI, deployed to Hetzner via SSH; Caddy handles HTTPS automatically

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
All technology choices are mutually compatible. Next.js 16.2 + TanStack Query + shadcn/ui + React Email integrate without conflicts. FastAPI 0.135.1 + Pydantic v2 + Supabase Python client + Resend SDK are all Python 3.12 compatible. Docker + Caddy on Hetzner is a proven production combination. No version conflicts identified.

**Pattern Consistency:**
`snake_case` JSON throughout is native to both Python and PostgreSQL — no transformation layer required. `lib/tokens.ts` and `lib/messages.ts` as single sources of truth satisfy the UX spec's browser↔inbox continuity requirement. TanStack Query `refetchInterval` aligns precisely with the named progress states pattern in the UX spec.

**Structure Alignment:**
Server Actions correctly isolate API keys from browser execution. `emails/` folder alongside `lib/tokens.ts` provides the shared design token layer required for email/browser visual consistency. `lib/messages.ts` enforces the Hungarian-only UI text rule structurally.

### Requirements Coverage Validation ✅

**Functional Requirements Coverage:**
All 36 FRs are architecturally supported and mapped to specific files in the project structure. Cross-cutting concerns (GDPR consent, cost enforcement, error handling) are addressed via dedicated modules (`cost_enforcement.py`, `errors.py`, `messages.ts`).

**Non-Functional Requirements Coverage:**
- NFR1 (landing <3s): Vercel static rendering ✅
- NFR2 (form→started <2s): Server Action + BackgroundTask dispatch ✅
- NFR4 (result <120s p95): Async parallel LLM + BackgroundTasks ✅
- NFR6 (TLS 1.2+): Caddy automatic HTTPS ✅
- NFR8 (magic link 24h): `magic_link_tokens.expires_at` + validation ✅
- NFR9 (zero cross-user access): Supabase RLS policies ✅
- NFR11 (email only as PII): DB schema enforces this ✅
- NFR16/17 ($50 cap + 80% alert): `cost_enforcement.py` + `cost_tracker.py` ✅
- NFR20 (WCAG 2.1 AA): shadcn/ui Radix primitives + axe-core CI ✅
- NFR21 (Hungarian content): `lib/messages.ts` single source ✅

**NFR19 Risk Note:** 30 concurrent runs × 20 personas = up to 600 parallel OpenRouter requests. `persona_engine.py` must implement `asyncio.Semaphore` to cap concurrent calls per run and include retry logic for 429 (rate limit) responses. At MVP volumes (10–30 runs/day) this is not a live risk, but must be implemented from the start.

### Gaps Identified and Resolved

**Gap 1 — Follow-up email scheduling (FR22) → RESOLVED**

FastAPI BackgroundTasks cannot schedule future-dated tasks. Resolution: Supabase pg_cron runs a daily job querying `runs` for records where `completed_at < now() - interval 'N days'` and `dayN_sent = false`. The cron job calls `POST /api/v1/operator/send-followups` (Bearer token protected). Three boolean tracking columns added to `runs` table: `day1_sent`, `day3_sent`, `day7_sent`. Migration `20260319_007_followup_tracking.sql` added to `supabase/migrations/`.

**Gap 2 — Operator endpoint authentication → RESOLVED**

`operator.py` router endpoints are protected by HTTP Bearer token authentication. `SWARMSENSE_OPERATOR_API_KEY` environment variable holds the static key. FastAPI `Security(HTTPBearer())` dependency applied to all operator routes. Key rotation via SSH `.env` update + container restart.

**Gap 3 — Unsubscribe storage (FR23-24, GDPR) → RESOLVED**

`users` table schema updated: `unsubscribed_at TIMESTAMPTZ NULL` column added. `email_service.py` checks `unsubscribed_at IS NULL` before dispatching any marketing email (follow-up sequence). Resend webhook or dedicated `POST /api/v1/unsubscribe` endpoint sets this field. Migration `20260319_008_unsubscribe.sql` added.

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Project context thoroughly analyzed (36 FRs, 21 NFRs)
- [x] Scale and complexity assessed (Medium, full-stack + async)
- [x] Technical constraints identified (GDPR, $50 cap, <120s p95)
- [x] Cross-cutting concerns mapped (cost enforcement, data isolation, email continuity)

**✅ Architectural Decisions**
- [x] Critical decisions documented with verified versions
- [x] Technology stack fully specified (Next.js 16.2, FastAPI 0.135.1, shadcn/ui CLI v4)
- [x] Integration patterns defined (Server Actions, BackgroundTasks, TanStack Query polling)
- [x] Performance and compliance considerations addressed

**✅ Implementation Patterns**
- [x] Naming conventions established (snake_case JSON, PascalCase components, etc.)
- [x] 9 conflict points identified and resolved
- [x] Communication patterns specified (no event system, TanStack Query state)
- [x] Process patterns documented (error handling, loading states, graceful degradation)

**✅ Project Structure**
- [x] Complete directory structure defined (all files and directories named)
- [x] Component boundaries established (browser UI / email / backend services / DB)
- [x] Integration points mapped (all 6 external services)
- [x] All 36 FRs mapped to specific files/directories

### Architecture Readiness Assessment

**Overall Status: READY FOR IMPLEMENTATION**

**Confidence Level: High** — stack is fully specified with verified versions, all requirements are covered, patterns prevent agent conflicts, and the three validation gaps have been resolved.

**Key Strengths:**
- Zero-ambiguity naming conventions prevent the most common multi-agent conflict type
- Single-source Hungarian text (`messages.ts`) and design tokens (`tokens.ts`) ensure consistency across the browser/email boundary
- Cost enforcement as middleware ensures the $50 cap cannot be bypassed regardless of which agent implements a run-initiating endpoint
- Data model anticipates V2 (Supabase Auth upgrade path) without requiring migration pain

**Areas for Future Enhancement (Post-MVP):**
- ARQ job queue to replace BackgroundTasks if run persistence becomes necessary
- Supabase Auth migration for V2 account system
- Rate limiting middleware on public endpoints if abuse is observed
- Result caching if persona engine outputs for identical queries become relevant

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented — rationale is provided for each decision
- Use implementation patterns from Section 5 consistently across all components
- Respect project structure boundaries — no Supabase client in frontend, no Hungarian strings hard-coded in components
- Refer to the Requirements to Structure Mapping table for any question about where a feature belongs

**First Implementation Story:**
```bash
# 1. Monorepo initialization
mkdir swarmsense && cd swarmsense && git init

# 2. Frontend
pnpm create next-app@latest frontend
cd frontend && pnpm dlx shadcn@latest init

# 3. Backend
mkdir ../backend && cd ../backend
python -m venv .venv && source .venv/bin/activate
pip install "fastapi[standard]==0.135.1" supabase resend

# 4. Supabase
cd .. && supabase init

# 5. Infrastructure files
# Create: docker-compose.yml, Caddyfile, .github/workflows/ci.yml, .github/workflows/deploy.yml
```
