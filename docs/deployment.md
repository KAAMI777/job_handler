# Deployment

## Overview

| Component | Host | How |
|---|---|---|
| API | Render **Web Service** | Docker build from `backend/Dockerfile`; `scripts/start.sh` runs `alembic upgrade head` then uvicorn |
| Scheduled scrape | Render **Cron Job** | same image, command `python -m app.scrape_runner` |
| Database | Supabase Postgres | `DATABASE_URL` in Render (bare `postgresql://…` is fine) |
| Frontend | Vercel | `VITE_API_URL` = the Render web service URL |

Both Render services share the same repo, the same image, and the same `DATABASE_URL`.

## Web service (Render)

- Root directory: `backend`
- Environment: Docker
- `DATABASE_URL` — Supabase **direct connection** string (port 5432), not the transaction pooler.
- Optional: `CORS_ORIGINS` (comma-separated), `LOG_LEVEL`, `ENVIRONMENT=production`.
- Health check path: `/health`
- Start command: leave blank (the Dockerfile `CMD` is `sh scripts/start.sh`). If you must
  set one, use `sh scripts/start.sh`.

## Cron job (Render) — the scheduled scrape

Scraping is **not** run by the web service. Create a separate Render **Cron Job**:

- Root directory: `backend`
- Environment: Docker (same Dockerfile)
- Command: `python -m app.scrape_runner`
- Schedule: e.g. `0 */6 * * *` (every 6 hours)
- Same `DATABASE_URL` as the web service.

The runner starts one `scrape_runs` row, scrapes every active company, and exits non-zero
if the run fails — so Render surfaces failures. Only one run executes at a time (a run still
`running` after 3 hours is treated as crashed and superseded).

## Migrations

`alembic upgrade head` runs automatically on every web-service boot (`scripts/start.sh`).
For a single instance this is fine. If you ever run multiple web instances, move the
migration step to a Render **Pre-Deploy Command** instead.

## Manual / n8n triggering (optional)

`POST /api/v1/scrape/run` still works for ad-hoc runs and is what n8n would call. With the
Render Cron Job in place, n8n is not required for scheduling — see `docs/n8n.md`.
