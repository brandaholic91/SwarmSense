# Story 1.4: Infrastructure Deployment & CI/CD Pipeline

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want the backend deployed to Hetzner VPS with automatic HTTPS and the CI/CD pipeline automated via GitHub Actions,
so that every PR is validated and every merge to main is deployed without manual steps.

## Acceptance Criteria

1. Given a Hetzner VPS with Docker installed and a registered domain, when `docker compose up -d` is run on the VPS using the production compose definition in this repository (currently `docker-compose.swarmsense-backend.yml`), then the `api` service runs FastAPI + Uvicorn for backend traffic handling.
2. Given a Hetzner VPS with Docker installed and a registered domain, when `docker compose up -d` is run on the VPS, then Caddy proxies HTTPS traffic to the `api` service with automatic Let's Encrypt SSL (TLS 1.2+), where the active Caddy configuration is VPS-managed and documented in project operations notes.
3. Given infrastructure is up, when the FastAPI health endpoint is called via HTTPS, then it returns HTTP 200.
4. Given a pull request is opened on GitHub, when the CI workflow (`ci.yml`) runs, then ESLint + TypeScript type-check passes on frontend with zero errors.
5. Given a pull request is opened on GitHub, when the CI workflow (`ci.yml`) runs, then backend `pytest` passes with zero failures.
6. Given a commit is merged to `main`, when the deploy workflow (`deploy.yml`) runs, then a Docker image is built and pushed to `ghcr.io`.
7. Given a commit is merged to `main`, when the deploy workflow (`deploy.yml`) runs, then the Hetzner VPS pulls the new image and restarts containers over SSH using `docker compose pull && docker compose up -d`.
8. Given a commit is merged to `main`, when deployment completes, then Vercel auto-deploys frontend with no manual trigger.

## Tasks / Subtasks

- [x] Implement production container and reverse proxy stack (AC: 1, 2, 3)
  - [x] Add `backend/Dockerfile` optimized for FastAPI 0.135.1 + Python 3.12 runtime (non-root user, deterministic install order, health-friendly startup command).
  - [x] Maintain a versioned production compose definition in repo (currently `docker-compose.swarmsense-backend.yml`) with at least backend and reverse-proxy-aligned runtime settings.
  - [x] Document VPS-managed Caddy configuration source of truth and deployment ownership; do not require committing active Caddy config to this repository.
  - [x] Ensure backend exposes a stable health endpoint consumed by Caddy and post-deploy verification.

- [x] Add backend container/runtime guardrails (AC: 1, 3)
  - [x] Confirm backend startup command is production-safe (`uvicorn app.main:app --host 0.0.0.0 --port 8000`).
  - [x] Ensure required `SWARMSENSE_*` env vars are documented in `backend/.env.example` for VPS runtime.
  - [x] Keep OpenAPI docs disabled in production via existing config pattern from Story 1.3.

- [x] Create CI workflow for pull requests (AC: 4, 5)
  - [x] Add `.github/workflows/ci.yml` for PR events.
  - [x] Frontend job: `pnpm install --frozen-lockfile`, `pnpm lint`, `pnpm exec tsc --noEmit` (or project type-check script).
  - [x] Backend job: create Python 3.12 environment, install `requirements.txt` + dev test deps, run `pytest`.
  - [x] Fail fast on any lint/type/test error; no warning-only pass mode.

- [x] Create deploy workflow for main branch (AC: 6, 7, 8)
  - [x] Add `.github/workflows/deploy.yml` triggered on push to `main`.
  - [x] Build backend image and push to `ghcr.io` using GitHub-provided token or PAT with package write permissions.
  - [x] SSH into Hetzner VPS using GitHub Actions secrets and run `docker compose pull && docker compose up -d` in deployment directory.
  - [x] Add post-deploy HTTPS health check step against public API domain; fail workflow on non-200.
  - [x] Keep frontend deployment decoupled (Vercel auto-deploy remains source of truth for frontend).

- [x] Add operations and test coverage for infrastructure behavior (AC: 1-8)
  - [x] Add backend test for health endpoint contract (HTTP 200 + expected response body fields if defined).
  - [x] Add workflow-level sanity checks where feasible (e.g., YAML lint or dry-run checks in CI).
  - [x] Document manual smoke-test runbook in `README.md` for first VPS bootstrap and rollback.

## Dev Notes

- This story was deferred in sprint status (`1-4 ... backlog # deferred until after epic-5`). Keep scope strictly on deployment/CI/CD infrastructure, not feature work.
- Do not introduce Supabase access from frontend while wiring deploy scripts; architecture boundary remains unchanged.
- Keep API route prefix and existing FastAPI configuration patterns from Story 1.3; infra story must not regress runtime behavior already stabilized there.
- Reuse existing backend structure (`backend/app/main.py`, routers, tests) instead of creating parallel service entrypoints.
- Current production deployment uses `docker-compose.swarmsense-backend.yml` in repo root; canonical `docker-compose.yml` migration is deferred to a later step to avoid runtime risk.
- Active Caddy configuration is managed directly on the Hetzner VPS and is intentionally not stored in this repository.
- Current production topology keeps backend port `8000` published temporarily to preserve container-level visibility during operations; primary public ingress remains Caddy.
- Follow-up hardening action: remove direct backend public port exposure after validating equivalent observability through Caddy/VPS-level monitoring.

### Architecture Compliance

- Backend hosting target is Hetzner VPS with Docker Compose and Caddy SSL termination.
- Frontend hosting target remains Vercel; deployment must not attempt to replace Vercel flow.
- CI policy is PR gate for lint/typecheck/pytest before merge.
- Secrets stay in GitHub Actions secrets and VPS `.env`; never committed and never exposed via `NEXT_PUBLIC_*`.

### Library / Framework Requirements

- Backend runtime: FastAPI 0.135.1, Python 3.12+.
- Frontend CI: Next.js 16.2.0 / TypeScript strict / `pnpm` package manager.
- Infrastructure: Docker + docker-compose + Caddy, GitHub Actions, GHCR.

### File Structure Requirements

- Root: `docker-compose.swarmsense-backend.yml` (current production compose definition; optional follow-up migration to `docker-compose.yml`)
- VPS-managed: active Caddy configuration (documented in ops notes, not committed in repo)
- CI/CD: `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`
- Backend container: `backend/Dockerfile`
- Environment docs: `backend/.env.example` (and root deployment docs if needed)
- Optional docs update: `README.md` deployment section

### Testing Requirements

- Backend tests: `cd backend && pytest`
- Frontend static checks in CI: `cd frontend && pnpm lint` and type-check
- Infrastructure smoke checks:
  - `docker compose config` (syntax validation)
  - Public HTTPS health check after deploy
  - Verify Caddy remains the primary public ingress for HTTPS traffic; backend direct port exposure is a documented temporary operational exception.

### Previous Story Intelligence (1.3)

- Reuse established `SWARMSENSE_*` settings model and production docs toggle pattern.
- Preserve existing CORS/domain restrictions; deployment scripts must not widen CORS as a shortcut.
- Keep stable error envelope contract and avoid infra changes that bypass middleware ordering fixed in Story 1.3.

### Git Intelligence Summary

- Recent commits show a strong pattern of adding story file + sprint-status updates together; keep that release hygiene.
- Current codebase already has backend routers and tests but lacks infrastructure artifacts (`docker-compose.yml`, `Caddyfile`, workflows), so this story should create foundational files rather than refactor app logic.
- Recent review cycles are strict on edge cases and contracts; include health check and deploy failure handling from day one.

### Latest Tech Information

- Use project-pinned versions from `_bmad-output/project-context.md` (Next.js 16.2.0, FastAPI 0.135.1, Python 3.12+, Tailwind v4, Vitest/pytest).
- No additional framework adoption is required for this story; prioritize deterministic CI and deployment reliability over adding tooling.

### Project Context Reference

- Follow `_bmad-output/project-context.md` for strict TypeScript, API `snake_case`, env var naming, testing locations, and anti-patterns.

### References

- Epic source and AC: `_bmad-output/planning-artifacts/epics.md#Story 1.4: Infrastructure Deployment & CI/CD Pipeline`
- Architecture hosting/deploy decisions: `_bmad-output/planning-artifacts/architecture.md#Infrastructure & Deployment`
- Architecture CI/CD patterns: `_bmad-output/planning-artifacts/architecture.md#Development Workflow Integration`
- Architecture structure/contracts: `_bmad-output/planning-artifacts/architecture.md#Project Structure & Boundaries`
- Prior implementation context: `_bmad-output/implementation-artifacts/1-3-fastapi-core-application-and-api-cost-enforcement-middleware.md`
- Project-wide guardrails: `_bmad-output/project-context.md`

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- `git log -5 --pretty=format:'%h %ad %s' --date=short`
- `git log -5 --name-only --pretty=format:'--- %h %s'`

### Completion Notes List

- Step 1 delivered: `.github/workflows/deploy.yml` added for `main` + manual dispatch deploy flow.
- Deploy workflow validation runs executed: `23456836745` (tag formatting fail), `23456883385` (SSH action input/auth fail), `23456938358` (SSH auth fail), `23457087083` (compose file not found), `23457141017` (success).
- Workflow hardened to current VPS layout: supports `docker-compose.yml` and fallback `docker-compose.swarmsense-backend.yml` in `HETZNER_DEPLOY_PATH`.
- Runtime verification done via successful GitHub Actions run including GHCR push, SSH deploy, and HTTPS health check.
- Scope decision recorded: keep `docker-compose.swarmsense-backend.yml` as current production compose file for now; postpone rename/standardization to `docker-compose.yml`.
- Scope decision recorded: Caddyfile remains VPS-managed and is referenced via documentation only (no Caddyfile committed in repo).
- Backend container hardening applied in `backend/Dockerfile`: non-root runtime user, deterministic dependency install layer, and explicit pip runtime guardrails.
- CI workflow hardened with `workflow_sanity` job in `.github/workflows/ci.yml` to run `actionlint` and `docker compose ... config` before frontend/backend jobs.
- Root `README.md` added with full project setup, CI/CD overview, and VPS bootstrap/smoke-test/rollback runbooks.

### File List

- .github/workflows/deploy.yml
- .github/workflows/ci.yml
- backend/Dockerfile
- README.md
- _bmad-output/implementation-artifacts/1-4-infrastructure-deployment-and-cicd-pipeline.md
