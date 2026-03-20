---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
workflowStatus: complete
completedAt: '2026-03-19'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
---

# SwarmSense - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for SwarmSense, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Visitors can submit a research query by providing a research topic and a target audience description
FR2: Visitors can view rotating example queries on the submission form to understand the expected input format
FR3: Visitors can view a product value proposition and an example result preview above the primary submission CTA on desktop and mobile before submitting a query
FR4: Visitors can provide their email address to receive their analysis results
FR5: The system can determine whether an email address has previously been used for a free analysis
FR6: First-time users can receive a magic link to their email address to verify identity before analysis processing begins
FR7: Returning users whose email address has already been used for a free analysis can view a blocking message indicating the free run has already been used
FR8: Returning users can view a Pro tier waitlist signup option on the blocking screen
FR9: Users can provide explicit consent to data processing and marketing communications at the point of email capture
FR10: The system can generate 15–20 distinct AI personas for a given target audience based on five attitudinal dimensions: risk appetite, decision-making style, organizational role, price sensitivity, and technology adoption curve
FR11: The system can run a research query against all generated personas in parallel
FR12: The system can deliver a partial result when 1–8 personas fail to respond within the processing timeout, requiring at least 12 completed personas and displaying the delivered persona count in the result
FR13: The persona generation system produces persona responses that reflect Hungarian market context — including Hungarian consumer behaviors, local market references, and Hungarian-language idioms — confirmed by operator spot-check of the first 50 runs showing ≥90% culturally relevant output
FR14: Users can receive their analysis results via email after identity verification and processing completion
FR15: Result emails can include an aggregate sentiment score indicating how many personas support or reject the submitted hypothesis
FR16: Result emails can include individual persona cards, each showing the persona's stance, primary argument, and the condition under which they would change their mind
FR17: Result emails can display a top-of-email consensus alert when at least 15 of 20 personas align on support or rejection
FR18: Result emails can include an interpretive disclaimer clarifying that results are AI-generated synthetic simulations, not real human research
FR19: Result emails can include a closing reflection question ("Mit tennél másképp ennek alapján?") and a single next-step call-to-action
FR20: Users can reply to result emails to contact the operator directly
FR21: The system can send a magic link verification email to new users
FR22: The system can send a 3-email automated follow-up sequence at day 1, day 3, and day 7 after analysis delivery, each promoting the Pro tier waitlist signup
FR23: The system can include a functional unsubscribe option in all automated marketing emails
FR24: Users can unsubscribe from all marketing communications
FR25: Users can view processing states (Queued, Running Personas, Composing Result, Completed) with refresh at least every 5 seconds, and can view a delayed notice if processing exceeds 120 seconds
FR26: The operator can view a log of all submitted queries and their processing status
FR27: The operator can view qualifier question responses associated with each verified email address
FR28: The system can alert the operator when API spend reaches 80% of the monthly hard limit
FR29: The system can enforce a hard monthly API cost limit and reject or queue new runs when the limit is reached
FR30: The operator can monitor email delivery success rates and open rates
FR31: Visitors can access the Privacy Policy before submitting their email address
FR32: Visitors can access the Terms of Service before submitting their email address
FR33: Users can submit a personal data deletion request via email, receive an acknowledgement within 15 minutes, and receive completion confirmation within 7 calendar days
FR34: The system can display a form warning instructing users not to include personally identifiable information in their research topic or target audience description
FR35: Returning users can submit their email address to join the Pro tier waitlist, and the system stores the waitlist signup with a timestamp
FR36: After magic link verification, users can answer a 2-question qualifier survey (role and primary use case) before analysis processing begins; responses are stored linked to the verified email address

### NonFunctional Requirements

NFR1: The system shall render the landing page within 3 seconds for p95 visits on a 50 Mbps connection, as measured daily by synthetic web performance checks
NFR2: The system shall complete form submission to processing-started confirmation within 2 seconds for p95 submissions under normal load, as measured by backend request timing logs
NFR3: The system shall deliver magic link verification emails within 60 seconds for >=95% of requests, as measured by transactional email event timestamps
NFR4: The system shall deliver result emails within 120 seconds of successful verification for p95 completed runs, as measured by run lifecycle and email dispatch logs
NFR5: The system shall deliver partial results with at least 12 persona outputs when full completion exceeds 120 seconds, as measured by run output-count logs
NFR6: The system shall enforce TLS 1.2+ for 100% of user-facing and API traffic, as measured by weekly transport-security scans
NFR7: The system shall encrypt all stored user and run data at rest with provider-managed encryption, as verified by quarterly infrastructure configuration audits
NFR8: The system shall expire magic link tokens exactly 24 hours after issuance, as verified by automated authentication integration tests
NFR9: The system shall prevent cross-user access to query data and result data with 0 unauthorized-access incidents, as measured by access-control audit logs
NFR10: The system shall enforce per-user data isolation so users can access only their own records, as verified by authorization test suites on each release
NFR11: The system shall store only email address as PII during MVP, with 0 persisted names, phone numbers, or payment data, as measured by monthly schema and data-retention audits
NFR12: The system shall maintain a transactional email delivery success rate of >=95% per rolling 7-day window, as measured by provider delivery events
NFR13: The system shall log 100% of failed and partially failed runs with error code and timestamp metadata, as measured by weekly run-log completeness checks
NFR14: The system shall keep non-run features operational when the monthly API limit is reached, blocking only new run initiation, as verified by limit-reached scenario tests
NFR15: The system shall capture unhandled exceptions and API timeout events within 60 seconds of occurrence, as measured by error-monitoring ingest timestamps
NFR16: The system shall enforce a hard monthly API spend cap of $50 and reject new runs at cap with explicit user feedback, as measured by monthly spend and rejection logs
NFR17: The system shall send an automated operator alert within 60 seconds after spend reaches 80% of the monthly cap, as measured by alert event timestamps
NFR18: The system shall support doubling concurrent run throughput versus baseline without service interruption, as measured by controlled load-test execution each release cycle
NFR19: The system shall support at least 30 concurrent persona engine runs with p95 result delivery <=120 seconds per run, as measured by scheduled concurrency load tests
NFR20: The system shall meet WCAG 2.1 AA contrast and keyboard navigation requirements for landing, form, and processing screens, as measured by automated accessibility scans plus quarterly manual audit
NFR21: The system shall present 100% of user-facing content and user-visible error messages in Hungarian during MVP, as measured by release checklist localization review

### Additional Requirements

- **Starter template / monorepo init:** Architecture specifies a monorepo with `create-next-app` (Next.js 16.2, TypeScript, Tailwind, App Router, Turbopack, shadcn/ui zinc theme) + FastAPI 0.135.1 (Python 3.12+, Pydantic v2) + Supabase CLI init as the first implementation story (Epic 1 Story 1)
- **Backend hosting:** Hetzner VPS, Docker + docker-compose with Caddy reverse proxy for automatic HTTPS (satisfies NFR6 without manual SSL config)
- **Frontend hosting:** Vercel with automatic preview deployments on PRs
- **CI/CD pipeline:** GitHub Actions — ci.yml (lint + typecheck + pytest on PR) + deploy.yml (Docker build → ghcr.io → SSH Hetzner on main merge)
- **Supabase schema + RLS:** 8 migration files required (users, magic_link_tokens, runs, qualifier_responses, waitlist, cost_tracking, followup_tracking, unsubscribe); RLS policies must be tested before any user-facing endpoint goes to production
- **Cost enforcement middleware:** Must be implemented before persona engine is wired up — `cost_enforcement.py` checks monthly spend cap on all run-initiating paths
- **Follow-up email scheduling:** pg_cron daily job queries runs with completed_at < now() - N days and day1/3/7_sent = false; calls protected `POST /api/v1/operator/send-followups` endpoint (FR22 gap resolution)
- **Operator endpoint authentication:** HTTP Bearer token via `SWARMSENSE_OPERATOR_API_KEY` env var on all operator routes
- **Unsubscribe storage:** `unsubscribed_at TIMESTAMPTZ NULL` column in users table; email_service.py checks before dispatching any marketing email (FR23/24 GDPR gap resolution)
- **React Email tokens file:** `frontend/lib/tokens.ts` must be defined before both browser UI and email templates are built — single source of truth for zinc/amber color tokens
- **Hungarian strings:** All user-visible Hungarian strings in `frontend/lib/messages.ts` — never hard-coded in components or templates
- **asyncio.Semaphore in persona engine:** Required from the start to cap concurrent LLM calls per run and handle 429 rate-limit retries (NFR19 risk mitigation)
- **Sentry integration:** Both frontend (layout.tsx) and backend (main.py) for error tracking and API timeout monitoring

### UX Design Requirements

UX-DR1: Design token system — implement zinc/amber/rose/emerald semantic color palette as CSS custom properties in `globals.css` (@layer base) and shared `frontend/lib/tokens.ts` file; tokens used by both browser UI components AND React Email templates for visual continuity across browser/inbox contexts
UX-DR2: ConsensusFlag component — 3 states: `strong-reject` (rose-400), `strong-support` (emerald-400), `split` (component hidden); triggered when ≥15/20 personas align; `role="alert"`, `aria-live="assertive"`; used in both result email and waiting screen completion state
UX-DR3: PersonaCard component — 2 variants: `compact` (landing page preview, truncated) and `full` (result email, full argument); left-border 4px stance indicator (rose=reject, emerald=support, amber=conditional); aria-label on card container; 3-column grid on desktop, 1-column on mobile
UX-DR4: WaitingScreen component — 5 named states: `queued` → `generating` → `running` (with persona count "Running 14 of 18 personas…") → `composing` → `completed`; large numeric counter as dominant visual element; email delivery notice ("Az eredményed erre az emailre érkezik: [email]"); delayed notice if processing exceeds 120 seconds; `aria-live="polite"`, `role="progressbar"` with `aria-valuenow`
UX-DR5: RotatingPlaceholder component — placeholder text cycles every 4 seconds, stops on field focus, does not restart after user clears + blurs; respects `prefers-reduced-motion` (stops cycling); used on research topic textarea and target audience textarea
UX-DR6: BlockingScreen component — 2 states: `default` and `waitlist-submitted` (CTA replaced by confirmation message); `role="main"`; informative tone ("már igénybe vette" not "nem jogosult"); single CTA button (not link)
UX-DR7: Progressive email disclosure — email field appears inline after Submit (no page reload, no redirect); qualifier screen framing as "Segíts kalibrálni a personákat"; single-action screens throughout the funnel (one primary CTA per screen)
UX-DR8: Result email design — consensus flag above the fold (no scroll required to see key finding); persona cards with inline CSS for email client compatibility; aggregate score visible immediately; reflection question ("Mit tennél másképp ennek alapján?") as closing interaction; reply-to is a real monitored address
UX-DR9: Responsive layout implementation — `max-w-lg` (512px) for form/qualifier/waiting screens; `max-w-2xl` (672px) for landing; `mx-auto px-4 sm:px-6`; form textareas side-by-side on md+, stack on mobile; PersonaCard: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`; magic link email single-column mobile-first; qualifier RadioGroup full-width 48px height on mobile
UX-DR10: High Contrast Impact visual direction — pure black background (#000), landing headline 44px weight 800 letter-spacing -1px; CTA button amber-400 black text weight 800; oversized numeric stat block in example result preview; blockquote-style top objection callout; system font stack (no web font loading on conversion-critical screens); tabular-nums for persona counts and sentiment scores
UX-DR11: Accessibility implementation — axe-core CI gate (zero critical violations); Lighthouse accessibility ≥90 on landing page; all inputs have visible `<label>`; keyboard navigation full funnel; focus ring `focus-visible:ring-2 focus-visible:ring-amber-400`; `<html lang="hu">`; persona stance uses color AND text label (never color-only); GDPR checkbox never pre-checked with explicit label and inline PP/ToS links; email: `role="presentation"` on layout tables, all images have `alt`
UX-DR12: Microcopy standards — specific patterns defined: email capture: "Az eredményed erre az emailre érkezik" (not "Regisztrálj"); waiting: "Futtatás: 14/18 persona" (not "Betöltés…"); blocking: "Ez az emailcím már igénybe vette az ingyenes próbát" (not "Nem jogosult"); result CTA: "Mit tennél másképp ennek alapján?" (not "Kattints ide"); PII warning static below topic field; error copy from `frontend/lib/errors.ts` mapping

### FR Coverage Map

FR1: Epic 2 — Query submission form (topic + audience fields)
FR2: Epic 2 — Rotating example queries on form
FR3: Epic 2 — Value proposition + example result preview on landing page
FR4: Epic 3 — Email capture field
FR5: Epic 3 — Email DB check (new vs. returning user)
FR6: Epic 3 — Magic link generation + email send
FR7: Epic 3 — Blocking screen for returning users
FR8: Epic 3 — Pro waitlist CTA on blocking screen
FR9: Epic 3 — GDPR consent checkbox at email capture
FR10: Epic 4 — 15–20 persona generation (5 attitudinal dimensions)
FR11: Epic 4 — Parallel persona query execution
FR12: Epic 4 — Partial result delivery (≥12 personas)
FR13: Epic 4 — Hungarian cultural context in persona responses
FR14: Epic 5 — Result email delivery
FR15: Epic 5 — Aggregate sentiment score in result email
FR16: Epic 5 — Individual persona cards in result email
FR17: Epic 5 — Consensus alert flag (≥15/20 align)
FR18: Epic 5 — Interpretive disclaimer in result email
FR19: Epic 5 — Reflection question + single CTA in result email
FR20: Epic 5 — Reply-to address on result emails
FR21: Epic 3 — Magic link verification email send
FR22: Epic 5 — 3-email follow-up sequence (day 1/3/7)
FR23: Epic 5 — Unsubscribe link in all marketing emails
FR24: Epic 5 — Unsubscribe action processing
FR25: Epic 4 — Waiting screen with named states + 5s polling
FR26: Epic 6 — Operator run log with processing status
FR27: Epic 6 — Qualifier response log per email
FR28: Epic 6 — 80% API spend alert
FR29: Epic 1 — Hard monthly API cost cap middleware
FR30: Epic 6 — Email delivery + open rate monitoring
FR31: Epic 3 — Privacy Policy access link
FR32: Epic 3 — Terms of Service access link
FR33: Epic 5 — Data deletion request via email
FR34: Epic 2 — PII warning below topic field
FR35: Epic 3 — Waitlist signup + storage with timestamp
FR36: Epic 4 — 2-question qualifier survey

## Epic List

### Epic 1: Project Foundation & Core Infrastructure
The development team can work in a production-compatible environment with all infrastructure prerequisites in place, including the monorepo structure, Supabase schema with RLS policies, Docker/Caddy deployment, CI/CD pipeline, monitoring integrations, and the API cost enforcement middleware that gates all subsequent persona engine work.
**FRs covered:** FR29
**Arch reqs:** Monorepo init (Next.js 16.2 + FastAPI 0.135.1), Supabase migrations (8 files + RLS), Docker + docker-compose + Caddy on Hetzner VPS, GitHub Actions ci.yml + deploy.yml, Sentry + Plausible integration, lib/tokens.ts + lib/messages.ts + lib/errors.ts base files, cost_enforcement.py middleware

### Epic 2: Landing Page & Research Query Submission
Visitors can discover SwarmSense, immediately grasp the value proposition through an example result preview that demonstrates persona diversity, and submit a research topic and target audience description without friction.
**FRs covered:** FR1, FR2, FR3, FR34

### Epic 3: Email Verification & Access Control
New users verify their identity via a magic link and proceed through the funnel; returning users receive a clear, non-punitive blocking message and can join the Pro tier waitlist; GDPR-compliant consent is captured at every email submission point.
**FRs covered:** FR4, FR5, FR6, FR7, FR8, FR9, FR21, FR31, FR32, FR35

### Epic 4: Qualifier Survey & Persona Engine Processing
After magic link verification, users complete a 2-click qualifier survey that personalizes their analysis; the persona engine runs 15–20 parallel AI calls; users see real-time named progress states on a waiting screen and understand their result will arrive by email.
**FRs covered:** FR10, FR11, FR12, FR13, FR25, FR36

### Epic 5: Result Delivery & User Communication Lifecycle
Users receive a structured multi-persona analysis in their inbox where the "aha moment" lands above the fold; the follow-up communication sequence runs automatically; users can unsubscribe or request data deletion at any point.
**FRs covered:** FR14, FR15, FR16, FR17, FR18, FR19, FR20, FR22, FR23, FR24, FR33

### Epic 6: Operator Monitoring & Administration
The operator has full visibility into run activity, qualifier response data, email delivery metrics, and API cost tracking; automated alerts fire at 80% spend threshold; the system enforces the hard cost cap with user-visible feedback.
**FRs covered:** FR26, FR27, FR28, FR30

---

## Epic 1: Project Foundation & Core Infrastructure

The development team can work in a production-compatible environment with all infrastructure prerequisites in place, including the monorepo structure, core database tables with RLS policies, FastAPI application with API cost enforcement middleware, Docker/Caddy deployment, CI/CD pipeline, monitoring integrations, and shared frontend base configuration files.

### Story 1.1: Monorepo Initialization & Development Environment

As a developer,
I want the project scaffolded as a monorepo with a Next.js frontend and FastAPI backend,
So that I have a working, runnable development environment that matches the production architecture from day one.

**Acceptance Criteria:**

**Given** an empty git repository
**When** the initialization commands are run
**Then** a `frontend/` directory exists with Next.js 16.2 configured with TypeScript strict mode, Tailwind CSS, App Router, Turbopack, and shadcn/ui initialized with zinc color theme and class-based dark mode
**And** a `backend/` directory exists with FastAPI 0.135.1, Pydantic v2, the Supabase Python client, and Resend SDK installed in a Python 3.12+ virtual environment
**And** `supabase/config.toml` exists from `supabase init`
**And** `.gitignore` covers `.env.local`, `.env`, `__pycache__`, `.venv`, `.next`, and `node_modules`
**And** `pnpm dev` starts the Next.js dev server at `http://localhost:3000` without errors
**And** `fastapi dev app/main.py` starts the backend at `http://localhost:8000` without errors
**And** `supabase start` starts a local Postgres instance without errors

### Story 1.2: Database Foundation — Users & Cost Tracking Schema

As a developer,
I want the `users` and `cost_tracking` database tables created with RLS policies,
So that user records and monthly API spend tracking are securely in place before any auth or cost enforcement logic is built.

**Acceptance Criteria:**

**Given** a running local Supabase instance
**When** migration files `20260319_001_users.sql` and `20260319_006_cost_tracking.sql` are applied via `supabase db push`
**Then** the `users` table exists with columns: `id` (UUID PK), `email` (text unique not null), `has_consent` (boolean not null), `consent_timestamp` (timestamptz), `unsubscribed_at` (timestamptz null), `created_at` (timestamptz default now())
**And** the `cost_tracking` table exists with columns: `month` (text PK, format YYYY-MM), `total_usd` (numeric not null default 0)
**And** a Supabase RLS policy is active on `users` ensuring no row is readable or writable without the service role key
**And** running `SELECT * FROM users` from the Supabase anonymous client returns an empty result (RLS blocks access)
**And** email values are stored in normalized form (lowercase, trimmed) as enforced by a check constraint or migration note
**And** the pg_cron extension is enabled in the Supabase project, verified by `SELECT extname FROM pg_extension WHERE extname = 'pg_cron'` returning one row (required by Story 5.4 follow-up scheduling)

### Story 1.3: FastAPI Core Application & API Cost Enforcement Middleware

As the system,
I want all run-initiating API paths to check the monthly API spend cap before proceeding,
So that the $50/month hard limit is enforced at the application layer and cannot be bypassed by any future endpoint.

**Acceptance Criteria:**

**Given** the FastAPI application is running
**When** a request arrives at any run-initiating endpoint
**Then** `cost_enforcement.py` queries `cost_tracking` for the current month's `total_usd` before allowing the request to proceed
**And** if `total_usd >= 50.00`, the endpoint returns HTTP 402 with `{"detail": "A havi ingyenes kapacitás elérte a határát.", "code": "COST_LIMIT_REACHED"}`
**And** non-run endpoints (auth, waitlist, operator, status polling) are unaffected when the monthly limit is reached (NFR14)
**And** all environment variables are parsed via Pydantic Settings from `SWARMSENSE_`-prefixed env vars: `SWARMSENSE_SUPABASE_URL`, `SWARMSENSE_SUPABASE_SERVICE_KEY`, `SWARMSENSE_KIMI_API_KEY`, `SWARMSENSE_OPERATOR_API_KEY`
**And** CORS middleware is configured to allow requests only from the Vercel frontend domain
**And** FastAPI OpenAPI docs (`/docs`) are disabled in production via env config

### Story 1.5: Frontend Base Configuration & Monitoring Integration

As a developer,
I want shared design tokens, Hungarian string constants, error mappings, and monitoring configured across both frontend and backend,
So that all subsequent components have a single source of truth for visual tokens, copy, and error handling — and production errors are captured automatically.

**Acceptance Criteria:**

**Given** the Next.js frontend project
**When** the base configuration files are in place
**Then** `frontend/lib/tokens.ts` exports color constants for: `background` (zinc-950), `surface` (zinc-900), `border` (zinc-800), `textPrimary` (zinc-50), `textSecondary` (zinc-400), `accent` (amber-400), `stanceReject` (rose-400), `stanceSupport` (emerald-400), `stanceConditional` (amber-400)
**And** `frontend/lib/messages.ts` exports a `messages` object with keys for all user-visible Hungarian strings (at minimum: email capture, waiting screen, blocking screen, error states, PII warning)
**And** `frontend/lib/errors.ts` exports an `errorMessages` mapping from API error codes (`COST_LIMIT_REACHED`, `TOKEN_EXPIRED`, `TOKEN_INVALID`) to Hungarian user-facing strings
**And** `frontend/app/globals.css` defines CSS custom properties for all tokens via `@layer base`
**And** `frontend/app/layout.tsx` has `<html lang="hu">` on the root element
**And** Sentry is initialized in `frontend/app/layout.tsx` with the DSN from `NEXT_PUBLIC_SENTRY_DSN`
**And** Sentry is initialized in `backend/app/main.py` with the DSN from `SWARMSENSE_SENTRY_DSN`
**And** the Plausible Analytics script tag is present in `frontend/app/layout.tsx`
**And** both `.env.example` files list every required variable with placeholder values

---

## Epic 2: Landing Page & Research Query Submission

Visitors can discover SwarmSense, immediately grasp the value proposition through an example result preview that demonstrates persona diversity, and submit a research topic and target audience description without friction.

### Story 2.1: Landing Page with Value Proposition & Example Result Preview

As a visitor,
I want to see SwarmSense's value proposition and an example result preview when I arrive at the landing page,
So that I can immediately understand what the product does and whether it is worth trying — overcoming my initial "ChatGPT wrapper" skepticism.

**Acceptance Criteria:**

**Given** a visitor arrives at `/`
**When** the page loads
**Then** the page renders within 3 seconds for p95 visits (NFR1)
**And** a bold headline (44px, weight 800, letter-spacing -1px) states the value proposition in Hungarian
**And** an example result preview section is visible that shows: an oversized persona count stat (e.g. "15 / 18 personas rejected this"), a blockquote-style top objection callout, and at least 3 PersonaCard components in `compact` variant displaying distinct stances (reject/support/conditional) with left-border color indicators
**And** the example preview uses real-looking, specific persona data — not placeholder text — to demonstrate persona diversity
**And** the page background is pure black (#000) per the High Contrast Impact design direction
**And** the page passes axe-core automated accessibility scan with zero critical violations
**And** `<html lang="hu">` is set on the root layout
**And** all user-visible text is in Hungarian (NFR21)

### Story 2.2: Research Query Submission Form

As a visitor,
I want to fill in a research topic and a target audience description and submit my query,
So that I can initiate a SwarmSense analysis without needing an account or any pre-registration.

**Acceptance Criteria:**

**Given** a visitor is on the landing page
**When** they view the submission form
**Then** two textarea fields are visible: one for the research topic and one for the target audience description
**And** both fields have visible `<label>` elements (never placeholder-only)
**And** a static PII warning is displayed below the research topic field: "Ne adj meg személyes adatokat a kutatási témában" (FR34)
**And** a primary amber-400 CTA button (weight 800, black text) is the only submit action on the form
**And** the Submit button is `disabled` with `aria-disabled="true"` until both required fields contain non-empty text
**And** form validation fires on blur (not on keystroke); error text appears below the field as inline text (never as a toast)

**Given** a visitor fills both fields and clicks Submit
**When** the form is submitted
**Then** the email capture field appears inline below the form (no page reload, no redirect)
**And** the research topic and audience values are preserved and visible

> **Implementation note:** The email capture field is rendered and accepts input at the end of this story; the Server Action wiring to `POST /api/v1/auth/check-email` is implemented in Story 3.1. The field is intentionally non-functional (UI scaffold only) until Story 3.1 is complete.

**Given** a visitor submits the form
**When** the page renders on a mobile device (320px–767px)
**Then** the two textareas stack vertically (not side-by-side)
**And** all tap targets are minimum 44×44px

### Story 2.3: Rotating Example Placeholders on Form Fields

As a visitor,
I want to see example research topics and target audience descriptions cycling through the form fields,
So that I understand what good input looks like and can overcome the "what do I write?" cognitive barrier.

**Acceptance Criteria:**

**Given** a visitor arrives at the landing page with the form visible
**When** neither form field has been focused
**Then** the `RotatingPlaceholder` component cycles through at least 3 example research topics in the topic field every 4 seconds
**And** the `RotatingPlaceholder` component cycles through at least 3 example target audience descriptions in the audience field every 4 seconds
**And** cycling animations respect `prefers-reduced-motion` (cycling stops when this media query is active)

**Given** a visitor clicks into a form field
**When** the field receives focus
**Then** the placeholder cycling stops immediately for that field
**And** the cycling does not restart after the user clears the field and moves focus away

**Given** the page is read by a screen reader
**When** the RotatingPlaceholder is active
**Then** the cycling animation does not affect screen reader announcements (placeholder is supplemental; the `<label>` is the accessible name)

### Story 2.4: UI Redesign — Landing Page and Research Form

As a visitor,
I want to experience a polished, professional landing page with a clear CTA that leads to a focused research submission screen,
So that I immediately understand the product's value and can submit my hypothesis without friction.

**Acceptance Criteria:**

**Given** the Stitch "Zinc Monolith" design is adopted
**When** the app renders
**Then** `tokens.ts` contains the new Stitch color tokens and `globals.css` defines corresponding CSS custom properties
**And** Inter and Space Grotesk fonts are loaded via `next/font/google` in `layout.tsx`
**And** all Material Symbols icons are replaced with `lucide-react` equivalents

**Given** a visitor navigates to `/`
**When** the page loads
**Then** a scrollable landing page renders with: sticky nav (logo + "Ingyen kipróbálom" CTA only), Hero section, Example Result Preview (reusing `PersonaCard` compact variant), How It Works (3 steps), Trust Stats Bar (4 stats), Closing CTA section, and Footer
**And** all CTA buttons navigate to `/research`
**And** the page is a React Server Component (no `"use client"`)

**Given** a visitor navigates to `/research`
**When** the page loads
**Then** a focused, centered (max-w-[600px]) submission screen renders with "Mi a hipotézised?" heading, two textareas with bottom-border focus style, `RotatingPlaceholder` on both fields, and a full-width amber "Elemzés indítása →" CTA
**And** after filling both fields and submitting, the email capture section appears inline (no page reload)
**And** all existing form validation and email capture behavior is preserved

**Given** all new pages use colors and copy
**When** implemented
**Then** all color values are imported from `tokens.ts`, all Hungarian strings are in `messages.ts`, no hardcoded hex values or inline strings appear in JSX

> **Reference:** Full acceptance criteria and task breakdown in `_bmad-output/implementation-artifacts/2-4-ui-redesign-landing-page-and-research-form.md`
> **Stitch source files:** `docs/stitch/stitch/swarmsense_landing_page/code.html`, `docs/stitch/stitch/swarmsense_research_submission/code.html`

---

## Epic 3: Email Verification & Access Control

New users verify their identity via a magic link and proceed through the funnel; returning users receive a clear, non-punitive blocking message and can join the Pro tier waitlist; GDPR-compliant consent is captured at every email submission point.

### Story 3.1: Email Capture with GDPR Consent & DB Check

As a visitor,
I want to enter my email address after submitting my research query and give consent to data processing,
So that the system can deliver my results and I know exactly what I'm agreeing to.

**Acceptance Criteria:**

**Given** a visitor has submitted the research form
**When** the email capture field appears inline
**Then** an email input field is visible with the label "Email cím" and microcopy "Az eredményed erre az emailre érkezik"
**And** a GDPR consent checkbox is visible — never pre-checked — with an explicit label containing inline links to the Privacy Policy and Terms of Service (FR9, FR31, FR32)
**And** the Submit button remains disabled until the email field is filled and the checkbox is checked
**And** Privacy Policy and Terms of Service links open in a new tab

**Given** a visitor submits a valid email with consent checked
**When** the Server Action calls `POST /api/v1/auth/check-email`
**Then** the email is normalized (`.lower().strip()`) at the FastAPI input boundary before any DB operation
**And** if the email is new: the flow continues to magic link generation
**And** if the email is already in the `users` table with a completed run: the user is redirected to `/blocked`

**Given** a migration `20260319_002_magic_link_tokens.sql` is applied
**When** the schema is checked
**Then** the `magic_link_tokens` table exists with: `token` (UUID PK), `user_id` (FK → users.id), `expires_at` (timestamptz), `used_at` (timestamptz null), `created_at` (timestamptz default now())
**And** RLS is active on `magic_link_tokens` (service role only)

### Story 3.2: Magic Link Generation & Verification Flow

As a first-time user,
I want to receive a magic link in my email and click it to verify my identity,
So that I can proceed to the analysis without creating a password.

**Acceptance Criteria:**

**Given** a new user's email has passed the DB check
**When** `POST /api/v1/auth/magic-link` is called
**Then** a UUID v4 token is generated and stored in `magic_link_tokens` with `expires_at = now() + 24 hours`
**And** a new record is created in `users` with the normalized email and `has_consent = true` and `consent_timestamp = now()`
**And** a magic link verification email is sent via Resend within 60 seconds (NFR3) containing the link `https://[domain]/verify?token=[UUID]`
**And** the email is sent from a real, identified sender address with a real reply-to address

**Given** a user clicks the magic link in their email
**When** the `/verify` page Server Action calls `POST /api/v1/auth/verify`
**Then** if the token exists, is not expired, and `used_at IS NULL`: the token is marked as used (`used_at = now()`), and the user is redirected to `/qualifier` with the `user_id` in the session/URL parameter
**And** if the token is expired (> 24 hours): the endpoint returns 401 with `code: "TOKEN_EXPIRED"` and the frontend shows a full-screen error in Hungarian with a "Új link kérése" CTA (NFR8)
**And** if the token has already been used: the endpoint returns 401 with `code: "TOKEN_INVALID"` and the frontend shows the same error screen
**And** only the email address is stored as PII — no name, phone, or payment data (NFR11)

### Story 3.3: Returning User Blocking Screen & Pro Waitlist CTA

As a returning user who has already used the free analysis,
I want to see a clear, informative message explaining why I cannot run another free analysis,
So that I understand my options and can join the Pro waitlist if I'm interested in continued access.

**Acceptance Criteria:**

**Given** a returning user submits their email and the DB check confirms their free run has been used
**When** they are redirected to `/blocked`
**Then** the `BlockingScreen` component is displayed with `role="main"` and the heading: "Ez az emailcím már igénybe vette az ingyenes próbát"
**And** a single primary CTA button is visible: "Iratkozz fel az értesítőre" (a `<button>` element, not a link)
**And** no other competing actions are present on the screen

**Given** a returning user clicks the waitlist CTA
**When** the Server Action calls `POST /api/v1/waitlist`
**Then** a migration `20260319_005_waitlist.sql` has created the `waitlist` table with: `id` (UUID PK), `email` (text unique not null), `created_at` (timestamptz default now())
**And** the email and timestamp are stored in the `waitlist` table (FR35)
**And** the `BlockingScreen` transitions to its `waitlist-submitted` state: the CTA is replaced by a confirmation message in Hungarian
**And** if the email is already in the waitlist table, no duplicate is created and the confirmation state is still shown

---

## Epic 4: Qualifier Survey & Persona Engine Processing

After magic link verification, users complete a 2-click qualifier survey that personalizes their analysis; the persona engine runs 15–20 parallel AI calls; users see real-time named progress states on a waiting screen and understand their result will arrive by email.

### Story 4.1: Qualifier Survey Screen

As a verified user,
I want to answer two quick questions about my role and intended use case before my analysis starts,
So that the persona generation can be calibrated to my context without adding significant friction.

**Acceptance Criteria:**

**Given** a user has successfully verified their magic link and arrives at `/qualifier`
**When** the qualifier screen loads
**Then** the page displays the framing: "Segíts kalibrálni a personákat" (not "Töltsd ki ezt az űrlapot")
**And** Question 1 is a Select/dropdown: "Mi jellemzi legjobban a szerepkörét?" with at least 5 role options
**And** Question 2 is a RadioGroup: "Milyen célra szeretné leginkább használni a szintetikus kutatást?" with at least 4 use case options
**And** no free-text input is present — clickable selectors only
**And** the Submit button is disabled until both questions are answered
**And** all qualifier options are completable in under 30 seconds

**Given** the qualifier screen renders on a mobile device
**When** the user views Question 2
**Then** RadioGroup items are full-width with a minimum height of 48px per item

**Given** migrations `20260319_003_runs.sql` and `20260319_004_qualifier_responses.sql` are applied
**When** the schema is checked
**Then** the `runs` table exists with: `id` (UUID PK), `user_id` (FK → users.id), `topic` (text), `audience` (text), `status` (text — one of: queued/running/composing/completed/partial/failed), `persona_count` (int null), `cost_usd` (numeric null), `day1_sent` (boolean default false), `day3_sent` (boolean default false), `day7_sent` (boolean default false), `created_at` (timestamptz), `completed_at` (timestamptz null)
**And** the `qualifier_responses` table exists with: `id` (UUID PK), `run_id` (FK → runs.id), `user_id` (FK → users.id), `role_answer` (text), `use_case_answer` (text), `created_at` (timestamptz)
**And** RLS is active on both tables (service role only)

### Story 4.2: Run Initiation & BackgroundTask Dispatch

As a verified user who has completed the qualifier,
I want my analysis to start immediately after I submit the qualifier,
So that I reach the waiting screen within 2 seconds and the persona engine begins processing.

**Acceptance Criteria:**

**Given** a user submits the qualifier survey
**When** the Server Action calls `POST /api/v1/qualifier` then `POST /api/v1/runs`
**Then** qualifier responses are stored in `qualifier_responses` linked to the `user_id`
**And** the cost enforcement middleware confirms monthly spend is below $50 before the run is created
**And** a new run record is created in `runs` with `status: "queued"` and the research topic + audience
**And** a FastAPI `BackgroundTask` is dispatched for the persona engine
**And** the user is redirected to `/waiting/[run_id]` within 2 seconds of qualifier submission (NFR2)
**And** if the monthly cost cap has been reached, the endpoint returns HTTP 402 with `code: "COST_LIMIT_REACHED"` and the user sees the Hungarian error message — no run record is created

### Story 4.3: Persona Engine — Parallel LLM Execution

As the system,
I want to run 15–20 attitudinally distinct AI personas against the user's research query in parallel,
So that the analysis reflects genuine diversity of market perspectives rather than a single LLM response.

**Acceptance Criteria:**

**Given** a run has been dispatched as a BackgroundTask
**When** `persona_engine.py` executes
**Then** 15–20 distinct personas are generated based on five attitudinal dimensions: risk appetite, decision-making style, organizational role, price sensitivity, and technology adoption curve (FR10)
**And** all persona LLM calls are dispatched in parallel using `asyncio.gather` with an `asyncio.Semaphore` to cap concurrent requests (NFR19)
**And** each persona call targets Kimi K2 (Moonshot AI) as primary LLM via `llm_client.py`
**And** each completed persona response includes: persona name, role, stance (support/reject/conditional), primary argument, and condition for changing mind
**And** all prompts and persona generation instructions are in Hungarian with explicit Hungarian cultural context embedded (FR13)
**And** the run status is updated to `"running"` when the first persona call is dispatched

**Given** a persona API call returns a 429 rate-limit response
**When** `llm_client.py` handles the response
**Then** the call is retried with exponential backoff up to 3 attempts before marking that persona as failed

**Given** the persona engine completes execution
**When** fewer than 12 personas respond successfully within the timeout
**Then** the run status is set to `"failed"`, no result email is sent, and the failure is logged to Sentry with error code and timestamp (NFR13, NFR15)

### Story 4.4: Partial Result Handling & Run Completion

As the system,
I want to deliver results gracefully when some personas time out,
So that users receive value even when the full 15–20 persona set is not available.

**Acceptance Criteria:**

**Given** the persona engine has completed execution
**When** between 12 and 19 personas responded successfully (1–8 failed)
**Then** the run status is set to `"partial"` and `persona_count` is updated with the actual completed count
**And** the result is passed to `run_processor.py` for aggregation with the actual count noted
**And** the result email is sent with the persona count displayed as `"{completed}/{total} persona"` (e.g. "17/18 persona") in the email header (FR12)

**Given** all 15–20 personas responded successfully
**When** the run processor aggregates results
**Then** the run status is set to `"completed"` and `persona_count` is updated
**And** `completed_at` is set to `now()`
**And** the result email delivery begins

**Given** any run reaches a final status (completed/partial/failed)
**When** the run record is updated
**Then** `cost_usd` is recorded with the actual LLM API cost for that run
**And** `cost_tracking` monthly counter is incremented by the run's `cost_usd`

### Story 4.5: Waiting Screen with Named Progress States

As a user waiting for my analysis,
I want to see specific, named progress states and a persona counter during the 90-second wait,
So that I feel anticipation rather than anxiety and understand that my result will arrive by email.

**Acceptance Criteria:**

**Given** a user arrives at `/waiting/[run_id]`
**When** the `WaitingScreen` component renders
**Then** TanStack Query polls `GET /api/v1/runs/{run_id}/status` every 5 seconds (FR25)
**And** the run status maps to named states displayed on screen: `queued` → "Sorban…", `running` → "Futtatás: [N]/[total] persona", `composing` → "Eredmény összeállítása…", `completed`/`partial` → completion state
**And** a transient `generating` display state ("Personák generálása…") may be shown client-side between the initial render and the first poll returning `running`; `generating` is a frontend-only UI state — it must never be persisted to the DB or returned by the status API endpoint
**And** the persona count is displayed as a large numeric element (dominant visual) when status is `running`
**And** an email delivery notice is shown: "Az eredményed erre az emailre érkezik: [email]"
**And** `aria-live="polite"` is set on the progress label; the progress bar has `role="progressbar"` with `aria-valuenow`

**Given** processing exceeds 120 seconds without a final status
**When** the waiting screen detects the delay
**Then** a delayed notice appears in Hungarian informing the user the analysis is taking longer than expected but is still running (FR25)

**Given** the run reaches `completed`, `partial`, or `failed` status
**When** TanStack Query receives the final status
**Then** polling stops automatically
**And** if `failed`: a Hungarian error message is displayed with a retry suggestion

---

## Epic 5: Result Delivery & User Communication Lifecycle

Users receive a structured multi-persona analysis in their inbox where the "aha moment" lands above the fold; the follow-up communication sequence runs automatically; users can unsubscribe or request data deletion at any point.

### Story 5.1: Result Email — React Email Templates & Design Tokens

As a developer,
I want the result email built with React Email components that share design tokens with the browser UI,
So that the result email feels like a continuation of the web experience and renders correctly across email clients.

**Acceptance Criteria:**

**Given** `frontend/lib/tokens.ts` exists
**When** `frontend/emails/result-email.tsx` is implemented
**Then** the template imports color constants from `tokens.ts` for accent, stance colors, and surface values
**And** all styles in the email template are inline CSS (no external stylesheets) for email client compatibility
**And** the template accepts props: `topic`, `audience`, `personas` (array), `persona_count` (string e.g. "17/18"), `aggregate_score`, `consensus_flag` (optional), `user_email`
**And** the email renders correctly in Gmail (web + mobile), Apple Mail, and Outlook 2019

**Given** the result email is rendered
**When** viewed in an email client
**Then** the email uses a white/light background while maintaining amber accent and rose/emerald/amber stance border colors
**And** `<html lang="hu">` is set on the email root element
**And** all images have `alt` attributes; layout tables have `role="presentation"`

### Story 5.2: Result Email — Content Structure & Persona Cards

As a user who receives a result email,
I want to see the most surprising finding immediately upon opening the email — without scrolling,
So that I experience the "aha moment" at the moment of email open, not after clicking through.

**Acceptance Criteria:**

**Given** a run has completed with ≥12 personas
**When** the result email is composed by `run_processor.py`
**Then** the aggregate sentiment score is computed: count of support/reject/conditional stances across all personas (FR15)
**And** if ≥15 of the total persona count align on support or rejection, the `ConsensusFlag` is set with the count and direction (FR17)

**Given** the result email is opened
**When** the user views the email above the fold (no scroll)
**Then** the `ConsensusFlag` component (if triggered) is the first visible element — bold, high-contrast, with icon + count text (e.g. "⚠ 15/18 persona elutasítja") (FR17)
**And** the aggregate sentiment score is visible above the fold (FR15)
**And** the `ConsensusFlag` uses `role="alert"` in the React Email context

**Given** the user scrolls through the email
**When** they view persona cards
**Then** each `PersonaCard` in `full` variant shows: persona name, role, stance label, primary argument, and condition for changing mind (FR16)
**And** each card has a 4px left border in the stance color (rose=reject, emerald=support, amber=conditional)
**And** persona cards are laid out in a 3-column grid on desktop and 1-column on mobile
**And** the interpretive disclaimer is present at the bottom of the email: results are AI-generated synthetic simulations, not real human research (FR18)

### Story 5.3: Result Email — Reflection Question, CTA & Delivery

As a user,
I want to receive my result email within 120 seconds and find a closing reflection question that invites me to act on the insight,
So that the product experience ends with a concrete prompt rather than just information delivery.

**Acceptance Criteria:**

**Given** a run has reached `completed` or `partial` status
**When** `email_service.py` sends the result email via Resend
**Then** the result email is sent within 120 seconds of successful magic link verification for p95 runs (NFR4)
**And** the email delivery success rate is ≥95% per rolling 7-day window (NFR12)
**And** the closing reflection question "Mit tennél másképp ennek alapján?" is present at the bottom of the email (FR19)
**And** a single CTA below the reflection question links to the Pro tier waitlist (FR19)
**And** the reply-to address is a real, monitored operator email address (FR20)
**And** the email subject line is: "A SwarmSense elemzésed elkészült"

**Given** a partial result (12–19 personas)
**When** the result email is sent
**Then** the persona count is displayed as `"{completed}/{total} persona válaszolt"` in the email header (FR12)

**Given** email delivery fails
**When** the Resend API returns an error
**Then** the failure is logged with error code and timestamp (NFR13)
**And** the run status remains `completed` or `partial`

### Story 5.4: Automated Follow-up Email Sequence

As the system,
I want to send a 3-email follow-up sequence at day 1, day 3, and day 7 after result delivery,
So that verified users who haven't joined the Pro waitlist are re-engaged with value-focused messaging.

**Acceptance Criteria:**

**Given** the FastAPI backend is running
**When** `POST /api/v1/operator/send-followups` is called with a valid `SWARMSENSE_OPERATOR_API_KEY` Bearer token
**Then** the endpoint queries `runs` for records where `completed_at < now() - interval '1 day'` and `day1_sent = false` (and equivalents for day3/day7)
**And** for each eligible run, `email_service.py` dispatches the corresponding follow-up email via Resend (checking `unsubscribed_at IS NULL` first)
**And** the respective `dayN_sent` flag is set to `true` after successful send
**And** the endpoint returns HTTP 200 with `{"sent": N}` where N is the count of emails dispatched
**And** if the Bearer token is missing or invalid, the endpoint returns HTTP 403

**Given** a run has `completed_at` set and `day1_sent = false`
**When** the Supabase pg_cron daily job runs and calls `POST /api/v1/operator/send-followups` (Bearer token protected)
**Then** all runs where `completed_at < now() - interval '1 day'` and `day1_sent = false` receive the day-1 follow-up email via Resend
**And** `day1_sent` is set to `true` after successful send
**And** the same pattern applies for `day3_sent` (3 days) and `day7_sent` (7 days) (FR22)

**Given** a follow-up email is sent
**When** the user views the email
**Then** a functional unsubscribe link is present in the email footer (FR23)
**And** the unsubscribe link calls `POST /api/v1/unsubscribe` which sets `users.unsubscribed_at = now()`
**And** `email_service.py` checks `unsubscribed_at IS NULL` before dispatching any follow-up email for that user (FR24)
**And** a user whose `unsubscribed_at` is set receives no further follow-up emails

### Story 5.5: Data Deletion Request Handling

As a user,
I want to be able to request deletion of my personal data by email and receive confirmation within defined SLAs,
So that I can exercise my GDPR right to erasure.

**Acceptance Criteria:**

**Given** a user sends a data deletion request email to the operator's designated address
**When** the operator receives the request
**Then** the Privacy Policy documents the deletion contact email address and the expected response timeline
**And** an automated acknowledgement email is sent to the requester within 15 minutes of the request being received (FR33) — implemented as an auto-responder configured on the designated deletion inbox (e.g. Resend inbound, Gmail filter, or equivalent); no custom FastAPI endpoint is required for MVP
**And** the operator completes the deletion (removing the user's record from `users`, `runs`, `qualifier_responses`) within 7 calendar days (FR33)
**And** a deletion completion confirmation email is sent to the user within 7 calendar days

**Given** deletion is completed
**When** the user's email is subsequently submitted to the system
**Then** the system treats it as a new first-time user (no blocking, no prior run history)

---

### Story 1.4: Infrastructure Deployment & CI/CD Pipeline

As a developer,
I want the backend deployed to Hetzner VPS with automatic HTTPS and the CI/CD pipeline automated via GitHub Actions,
So that every PR is validated and every merge to main is deployed without manual steps.

**Acceptance Criteria:**

**Given** a Hetzner VPS with Docker installed and a registered domain
**When** `docker compose up -d` is run on the VPS
**Then** the `api` service runs FastAPI + Uvicorn on an internal port
**And** the `caddy` service proxies HTTPS traffic to the `api` service with automatic Let's Encrypt SSL (satisfying NFR6: TLS 1.2+)
**And** the FastAPI health endpoint returns HTTP 200 over HTTPS

**Given** a pull request is opened on GitHub
**When** the CI workflow (`ci.yml`) runs
**Then** ESLint + TypeScript type-check passes on the frontend with zero errors
**And** `pytest` passes on the backend with zero failures

**Given** a commit is merged to `main`
**When** the deploy workflow (`deploy.yml`) runs
**Then** a Docker image is built and pushed to `ghcr.io`
**And** the Hetzner VPS pulls the new image and restarts the container via SSH (`docker compose pull && docker compose up -d`)
**And** Vercel automatically deploys the Next.js frontend with no manual trigger required

## Epic 6: Operator Monitoring & Administration

The operator has full visibility into run activity, qualifier response data, email delivery metrics, and API cost tracking; automated alerts fire at 80% spend threshold; the system enforces the hard cost cap with user-visible feedback.

### Story 6.1: Operator Run Log Endpoint

As an operator,
I want to view a log of all submitted runs with their status, persona counts, and costs via a protected API endpoint,
So that I can monitor daily activity, identify failed runs, and verify the system is working as expected.

**Acceptance Criteria:**

**Given** the operator calls `GET /api/v1/operator/runs` with a valid Bearer token
**When** the endpoint processes the request
**Then** it returns a paginated list of run records with: `run_id`, `user_email`, `topic`, `audience`, `status`, `persona_count`, `cost_usd`, `created_at`, `completed_at` (FR26)
**And** runs are ordered by `created_at` descending
**And** if the Bearer token is missing or invalid, the endpoint returns HTTP 403

**Given** the operator calls `GET /api/v1/operator/runs` with `?status=failed`
**When** the endpoint filters results
**Then** only runs with `status = "failed"` are returned
**And** each failed run includes the error code and timestamp metadata

**Given** a run has `status = "failed"` or `status = "partial"`
**When** the run record was created
**Then** 100% of failed and partially-failed runs are logged with error code and timestamp metadata (NFR13)

### Story 6.2: Qualifier Response Log Endpoint

As an operator,
I want to view qualifier survey responses associated with each verified email address,
So that I can analyse what roles and use cases are most common among early users and inform product decisions.

**Acceptance Criteria:**

**Given** the operator calls `GET /api/v1/operator/qualifier-responses` with a valid Bearer token
**When** the endpoint processes the request
**Then** it returns a list of qualifier response records with: `user_email`, `role_answer`, `use_case_answer`, `created_at` (FR27)
**And** responses are ordered by `created_at` descending
**And** if the Bearer token is missing or invalid, the endpoint returns HTTP 403
**And** no cross-user data is exposed — each record contains only the data for that specific user/run pair (NFR9)

### Story 6.3: API Cost Tracking, 80% Alert & Hard Cap Enforcement

As an operator,
I want to receive an automatic alert when monthly API spend reaches 80% of the $50 limit and see current cost via an endpoint,
So that I can monitor burn rate and the system automatically protects against overruns.

**Acceptance Criteria:**

**Given** a run completes and `cost_tracker.py` increments `cost_tracking.total_usd`
**When** the new total reaches or exceeds $40.00 (80% of $50)
**Then** an automated alert is sent to the operator within 60 seconds via Sentry alert or email containing the current spend amount and the cap (FR28, NFR17)
**And** the alert fires only once per threshold crossing per month (not on every subsequent run)

**Given** the operator calls `GET /api/v1/operator/cost` with a valid Bearer token
**When** the endpoint processes the request
**Then** it returns: `month` (YYYY-MM), `total_usd` (current spend), `cap_usd` (50.00), `percentage` (total/cap × 100), `status` ("ok" | "warning" | "capped")

**Given** monthly `total_usd >= 50.00`
**When** a new run is attempted
**Then** the cost enforcement middleware blocks the run with HTTP 402 and `code: "COST_LIMIT_REACHED"` (NFR16)
**And** the user sees the Hungarian message: "A havi ingyenes kapacitás elérte a határát."
**And** all non-run features remain fully operational: auth, waitlist, status polling, operator endpoints (NFR14)

### Story 6.4: Email Delivery & Open Rate Monitoring

As an operator,
I want visibility into result email delivery rates and open rates,
So that I can monitor whether users are actually receiving and engaging with their analysis results.

**Acceptance Criteria:**

**Given** result emails and follow-up emails are sent via Resend
**When** the operator accesses monitoring data
**Then** email delivery success rates are visible in the Resend dashboard per email type (result, magic link, follow-up day 1/3/7) (FR30)
**And** email open rates are visible in the Resend dashboard for result emails and follow-up sequences (FR30)
**And** the operator endpoint `GET /api/v1/operator/email-stats` returns a summary: `{ "result_emails_sent": N, "result_delivery_rate": 0.97, "followup_day1_sent": N }` sourced from Resend webhook data or Resend API calls
**And** if the 7-day rolling delivery success rate drops below 95%, a Sentry alert fires (NFR12)
