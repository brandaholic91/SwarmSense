# Story 1.4: Infrastructure Deployment & CI/CD Pipeline

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want the backend deployed to Hetzner VPS with automatic HTTPS and the CI/CD pipeline automated via GitHub Actions,
so that every PR is validated and every merge to main is deployed without manual steps.

## Acceptance Criteria

1. Given a Hetzner VPS with Docker installed and a registered domain, when `docker compose up -d` is run on the VPS, then the `api` service runs FastAPI + Uvicorn on an internal port.
2. Given a Hetzner VPS with Docker installed and a registered domain, when `docker compose up -d` is run on the VPS, then the `caddy` service proxies HTTPS traffic to the `api` service with automatic Let's Encrypt SSL (TLS 1.2+).
3. Given infrastructure is up, when the FastAPI health endpoint is called via HTTPS, then it returns HTTP 200.
4. Given a pull request is opened on GitHub, when the CI workflow (`ci.yml`) runs, then ESLint + TypeScript type-check passes on frontend with zero errors.
5. Given a pull request is opened on GitHub, when the CI workflow (`ci.yml`) runs, then backend `pytest` passes with zero failures.
6. Given a commit is merged to `main`, when the deploy workflow (`deploy.yml`) runs, then a Docker image is built and pushed to `ghcr.io`.
7. Given a commit is merged to `main`, when the deploy workflow (`deploy.yml`) runs, then the Hetzner VPS pulls the new image and restarts containers over SSH using `docker compose pull && docker compose up -d`.
8. Given a commit is merged to `main`, when deployment completes, then Vercel auto-deploys frontend with no manual trigger.

## Tasks / Subtasks

- [ ] Implement production container and reverse proxy stack (AC: 1, 2, 3)
  - [ ] Add `backend/Dockerfile` optimized for FastAPI 0.135.1 + Python 3.12 runtime (non-root user, deterministic install order, health-friendly startup command).
  - [ ] Add root `docker-compose.yml` with at least `api` and `caddy` services, internal networking, restart policy, and mounted `Caddyfile`.
  - [ ] Add root `Caddyfile` with host-based TLS termination and reverse proxy to `api` internal port; avoid exposing API container directly to public internet.
  - [ ] Ensure backend exposes a stable health endpoint consumed by Caddy and post-deploy verification.

- [ ] Add backend container/runtime guardrails (AC: 1, 3)
  - [ ] Confirm backend startup command is production-safe (`uvicorn app.main:app --host 0.0.0.0 --port 8000`).
  - [ ] Ensure required `SWARMSENSE_*` env vars are documented in `backend/.env.example` for VPS runtime.
  - [ ] Keep OpenAPI docs disabled in production via existing config pattern from Story 1.3.

- [ ] Create CI workflow for pull requests (AC: 4, 5)
  - [ ] Add `.github/workflows/ci.yml` for PR events.
  - [ ] Frontend job: `pnpm install --frozen-lockfile`, `pnpm lint`, `pnpm exec tsc --noEmit` (or project type-check script).
  - [ ] Backend job: create Python 3.12 environment, install `requirements.txt` + dev test deps, run `pytest`.
  - [ ] Fail fast on any lint/type/test error; no warning-only pass mode.

- [ ] Create deploy workflow for main branch (AC: 6, 7, 8)
  - [ ] Add `.github/workflows/deploy.yml` triggered on push to `main`.
  - [ ] Build backend image and push to `ghcr.io` using GitHub-provided token or PAT with package write permissions.
  - [ ] SSH into Hetzner VPS using GitHub Actions secrets and run `docker compose pull && docker compose up -d` in deployment directory.
  - [ ] Add post-deploy HTTPS health check step against public API domain; fail workflow on non-200.
  - [ ] Keep frontend deployment decoupled (Vercel auto-deploy remains source of truth for frontend).

- [ ] Add operations and test coverage for infrastructure behavior (AC: 1-8)
  - [ ] Add backend test for health endpoint contract (HTTP 200 + expected response body fields if defined).
  - [ ] Add workflow-level sanity checks where feasible (e.g., YAML lint or dry-run checks in CI).
  - [ ] Document manual smoke-test runbook in `README.md` for first VPS bootstrap and rollback.

## Dev Notes

- This story was deferred in sprint status (`1-4 ... backlog # deferred until after epic-5`). Keep scope strictly on deployment/CI/CD infrastructure, not feature work.
- Do not introduce Supabase access from frontend while wiring deploy scripts; architecture boundary remains unchanged.
- Keep API route prefix and existing FastAPI configuration patterns from Story 1.3; infra story must not regress runtime behavior already stabilized there.
- Reuse existing backend structure (`backend/app/main.py`, routers, tests) instead of creating parallel service entrypoints.

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

- Root: `docker-compose.yml`, `Caddyfile`
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
  - Verify only Caddy exposes public ports; API container remains internal

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

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

- _bmad-output/implementation-artifacts/1-4-infrastructure-deployment-and-cicd-pipeline.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
