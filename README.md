# SwarmSense

SwarmSense is a full-stack application with:
- `frontend`: Next.js 16, TypeScript, Vitest
- `backend`: FastAPI, Python 3.12, pytest
- deployment: GHCR + Hetzner VPS (Docker Compose), HTTPS via VPS-managed Caddy

## Repository Structure

```text
.
├── backend/
│   ├── app/                    # FastAPI app code
│   ├── tests/                  # backend tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/                    # Next.js App Router code
│   ├── package.json
│   └── pnpm-lock.yaml
├── .github/workflows/
│   ├── ci.yml
│   └── deploy.yml
└── docker-compose.swarmsense-backend.yml
```

## Prerequisites

- Node.js 20+
- pnpm 9+
- Python 3.12+
- Docker with Compose plugin (`docker compose`)

## Local Development

### 1) Backend environment

```bash
cp backend/.env.example backend/.env
```

Fill required `SWARMSENSE_*` values in `backend/.env`.

### 2) Run backend with Docker (recommended)

```bash
docker compose -f docker-compose.swarmsense-backend.yml up -d --build
```

Health check:

```bash
curl -i http://localhost:8000/api/v1/status
```

### 3) Run frontend

```bash
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

Frontend default URL: `http://localhost:3000`

## Environment Variables

### Backend (`backend/.env`)

Source of truth: `backend/.env.example`

Core keys include:
- `SWARMSENSE_SUPABASE_URL`
- `SWARMSENSE_SUPABASE_SERVICE_KEY`
- `SWARMSENSE_KIMI_API_KEY`
- `SWARMSENSE_OPENROUTER_API_KEY`
- `SWARMSENSE_OPENROUTER_MODEL`
- `SWARMSENSE_OPENROUTER_BASE_URL`
- `SWARMSENSE_OPERATOR_API_KEY`
- `SWARMSENSE_INTERNAL_SECRET`
- `SWARMSENSE_FRONTEND_ORIGIN`
- `SWARMSENSE_BACKEND_ORIGIN`
- `SWARMSENSE_RESEND_API_KEY`
- `SWARMSENSE_EMAIL_FROM`
- `SWARMSENSE_EMAIL_REPLY_TO`
- `SWARMSENSE_SENTRY_DSN`
- `SWARMSENSE_ENVIRONMENT`
- `SWARMSENSE_DISABLE_SINGLE_RUN_LIMIT`

### Frontend (for local/runtime configuration)

Typical keys used in code:
- `API_URL`
- `NEXT_PUBLIC_API_URL`
- `INTERNAL_SECRET`
- `COOKIE_DOMAIN`
- `NEXT_PUBLIC_SENTRY_DSN`
- `NEXT_PUBLIC_PLAUSIBLE_DOMAIN`

## Quality and Test Commands

### Frontend

```bash
cd frontend
pnpm install --frozen-lockfile
pnpm lint
pnpm exec tsc --noEmit
pnpm test
pnpm build
```

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests -q
```

Optional local backend run without Docker:

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## CI/CD

### CI (`.github/workflows/ci.yml`)

Triggers:
- `pull_request`
- `push` to `main`

Pipeline stages:
1. Workflow sanity checks:
   - `actionlint` for GitHub Actions workflows
   - `docker compose -f docker-compose.swarmsense-backend.yml config`
2. Frontend checks:
   - install, lint, type-check, tests, build
3. Backend checks:
   - Python setup, dependency install, `pytest`

### Deploy (`.github/workflows/deploy.yml`)

Triggers:
- `push` to `main` and `master`
- manual `workflow_dispatch`

Deploy flow:
1. Build backend image from `backend/Dockerfile`
2. Push image to GHCR (`ghcr.io/<owner>/swarmsense-backend`)
3. SSH into Hetzner VPS and run:
   - `docker compose pull`
   - `docker compose up -d`
4. Run post-deploy HTTPS health check against `BACKEND_HEALTHCHECK_URL`

Required GitHub Secrets:
- `HETZNER_HOST`
- `HETZNER_USER`
- `HETZNER_SSH_PRIVATE_KEY`
- `HETZNER_SSH_PORT`
- `HETZNER_DEPLOY_PATH`
- `GHCR_USERNAME`
- `GHCR_TOKEN`
- `BACKEND_HEALTHCHECK_URL`

Note: active Caddy configuration is intentionally VPS-managed and not stored in this repository.

## Hetzner VPS Bootstrap and Smoke Test Runbook

Use this once for first-time setup, then for routine verification.

1. Prepare host and deployment directory.
   - Install Docker + Compose plugin on the VPS.
   - Create deployment directory (matches `HETZNER_DEPLOY_PATH`).
2. Copy deployment files to VPS.
   - `docker-compose.swarmsense-backend.yml`
   - backend environment file (`backend/.env`) with production values
3. Log in to GHCR on VPS.
   - `echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USERNAME" --password-stdin`
4. Start services.
   - `docker compose -f docker-compose.swarmsense-backend.yml pull`
   - `docker compose -f docker-compose.swarmsense-backend.yml up -d`
5. Verify container health.
   - `docker compose -f docker-compose.swarmsense-backend.yml ps`
   - `docker compose -f docker-compose.swarmsense-backend.yml logs --tail=200`
6. Verify public HTTPS endpoint.
   - `curl --fail --silent --show-error https://<your-domain>/api/v1/status`
7. Confirm Caddy ingress.
   - Validate that public traffic terminates at Caddy and proxies to backend service.

Smoke test checklist:
- API health endpoint returns HTTP 200
- backend container is healthy and keeps restarting disabled (`restart: unless-stopped` expected behavior)
- no critical errors in backend logs

## Rollback Runbook

If a deployment is unhealthy:

1. Inspect current service state and logs:

```bash
docker compose -f docker-compose.swarmsense-backend.yml ps
docker compose -f docker-compose.swarmsense-backend.yml logs --tail=300
```

2. Roll back to the previous known-good backend image tag in your compose/runtime configuration.
3. Re-deploy:

```bash
docker compose -f docker-compose.swarmsense-backend.yml pull
docker compose -f docker-compose.swarmsense-backend.yml up -d
```

4. Re-run health verification:

```bash
curl --fail --silent --show-error https://<your-domain>/api/v1/status
```

5. If rollback fails, freeze further deploys and investigate:
   - GHCR image availability
   - VPS disk space/memory
   - Caddy routing/TLS status
   - backend environment configuration drift
