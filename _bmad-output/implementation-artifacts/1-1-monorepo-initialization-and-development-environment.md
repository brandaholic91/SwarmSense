# Story 1.1: Monorepo Initialization & Development Environment

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want the project scaffolded as a monorepo with a Next.js frontend and FastAPI backend,
so that I have a working, runnable development environment that matches the production architecture from day one.

## Acceptance Criteria

1. Given an empty git repository, when the initialization commands are run, then a `frontend/` directory exists with Next.js 16.2 configured with TypeScript strict mode, Tailwind CSS, App Router, Turbopack, and shadcn/ui initialized with zinc color theme and class-based dark mode.
2. A `backend/` directory exists with FastAPI 0.135.1, Pydantic v2, the Supabase Python client, and Resend SDK installed in a Python 3.12+ virtual environment.
3. `supabase/config.toml` exists from `supabase init`.
4. `.gitignore` covers `.env.local`, `.env`, `__pycache__`, `.venv`, `.next`, and `node_modules`.
5. `pnpm dev` starts the Next.js dev server at `http://localhost:3000` without errors.
6. `fastapi dev app/main.py` starts the backend at `http://localhost:8000` without errors.
7. `supabase start` starts a local Postgres instance without errors.

## Tasks / Subtasks

- [x] Initialize monorepo scaffold (AC: 1, 2, 3)
  - [x] Create `frontend/` via `pnpm create next-app@latest` with TS strict, Tailwind, App Router, Turbopack, ESLint, import alias @/*.
  - [x] Initialize shadcn/ui in `frontend/` with zinc theme and class-based dark mode.
  - [x] Create `backend/` and Python 3.12+ venv; install `fastapi[standard]==0.135.1`, `supabase`, `resend`.
  - [x] Run `supabase init` at repo root; verify `supabase/config.toml`.
- [x] Repo hygiene and ignore rules (AC: 4)
  - [x] Ensure `.gitignore` includes `.env.local`, `.env`, `__pycache__`, `.venv`, `.next`, `node_modules`.
- [x] Local dev sanity checks (AC: 5, 6, 7)
  - [x] Run `pnpm dev` in `frontend/` and confirm it serves `http://localhost:3000`.
  - [x] Run `fastapi dev app/main.py` in `backend/` and confirm it serves `http://localhost:8000`.
  - [x] Run `supabase start` and confirm local Postgres boots without errors.

## Dev Notes

- Use the exact versions specified: Next.js 16.2, FastAPI 0.135.1, Python 3.12+; do not upgrade versions in this story.
- Package manager for frontend is `pnpm` (per architecture initialization commands).
- Backend dependencies required now: FastAPI (standard extras), Supabase Python client, Resend SDK.
- Keep the repo as a single monorepo with top-level `frontend/`, `backend/`, and `supabase/`.
- Do not introduce additional tooling, build scripts, or CI/CD files unless explicitly required by acceptance criteria.

### Project Structure Notes

- Expected structure at minimum:
  - `frontend/` (Next.js App Router)
  - `backend/` (FastAPI app)
  - `supabase/` (CLI project with `config.toml`)
- Architecture doc lists infrastructure files (e.g. `docker-compose.yml`, `Caddyfile`, `.github/workflows/*`) as part of the first implementation story, but the Epic 1 Story 1 acceptance criteria do not require them. Treat those files as out-of-scope unless the PM explicitly expands this story.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 1, Story 1.1 Acceptance Criteria)
- `_bmad-output/planning-artifacts/architecture.md` (Starter Template Evaluation; Project Structure)

## Dev Agent Record

### Agent Model Used

openai/gpt-5.2-codex

### Debug Log References

- `corepack enable && corepack prepare pnpm@9.12.3 --activate`
- `pnpm create next-app@16.2.0 frontend --ts --tailwind --eslint --app --import-alias "@/*" --use-pnpm --yes`
- `pnpm dlx shadcn@latest init --template next --base radix --preset nova --no-monorepo --yes --css-variables`
- `python3 -m venv backend/.venv`
- `backend/.venv/bin/pip install fastapi[standard]==0.135.1 supabase resend`
- `npx supabase init`
- `pnpm dev` (Turbopack, confirmed startup)
- `fastapi dev app/main.py` (confirmed startup)
- `npx supabase start` (completed startup; warning about missing seed file)

### Completion Notes List

- Frontend scaffolded with Next.js 16.2, Tailwind, App Router, Turbopack dev script, and shadcn/ui initialized with zinc base color and class-based dark mode.
- Backend created with Python venv and FastAPI app entrypoint at `backend/app/main.py`, dependencies installed per spec.
- Supabase CLI initialized at repo root; `supabase/config.toml` created and local stack start verified.
- Repo hygiene updated with required ignore rules.

### File List

- .gitignore
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/main.py
- frontend/.gitignore
- frontend/AGENTS.md
- frontend/CLAUDE.md
- frontend/README.md
- frontend/app/favicon.ico
- frontend/app/globals.css
- frontend/app/layout.tsx
- frontend/app/page.tsx
- frontend/components.json
- frontend/components/ui/button.tsx
- frontend/eslint.config.mjs
- frontend/lib/utils.ts
- frontend/next.config.ts
- frontend/package.json
- frontend/pnpm-lock.yaml
- frontend/postcss.config.mjs
- frontend/public/file.svg
- frontend/public/globe.svg
- frontend/public/next.svg
- frontend/public/vercel.svg
- frontend/public/window.svg
- frontend/tsconfig.json
- supabase/.gitignore
- supabase/config.toml

### Change Log

- 2026-03-19: Initialized monorepo scaffold (frontend, backend, supabase) and updated repo ignore rules.
