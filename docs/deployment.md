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

## Scheduling with GitHub Actions instead (free)

If you'd rather not pay for a Render Cron Job, `.github/workflows/scrape.yml` does the same
job by calling the API on a schedule:

1. In GitHub: **Settings → Secrets and variables → Actions → Variables → New variable**
   - Name: `API_BASE_URL`
   - Value: your Render web-service URL, no trailing slash (e.g. `https://job-handler-xxxx.onrender.com`)
2. Make sure Actions are enabled: **Settings → Actions → General → Allow all actions**.
3. The workflow runs every 6 hours (`cron: "0 */6 * * *"` — edit in the file). You can also
   run it on demand: **Actions → Scheduled scrape → Run workflow**.
4. It POSTs `/api/v1/scrape/run`, then polls the run until it finishes and fails the job if
   the run failed.

Use **either** the Render Cron Job **or** GitHub Actions — not both.

## Email digest (optional)

After each run the backend can email a digest of the *new* relevant jobs it found, grouped
by company. Set these on the **web service and the scrape runner** (whichever executes the
run):

| Var | Meaning |
|---|---|
| `RESEND_API_KEY` | from resend.com (free tier: 3,000/mo) |
| `NOTIFY_EMAIL` | recipient(s), comma-separated |
| `NOTIFY_FROM_EMAIL` | `onboarding@resend.dev` works with no domain but only sends to your own Resend account email; use a sender on a verified domain otherwise |
| `NOTIFY_MIN_SCORE` | only include jobs at/above this score (default `0`) |

Leave `RESEND_API_KEY` / `NOTIFY_EMAIL` unset to disable it. If you schedule with GitHub
Actions, set these on the **web service** (that's where the background run executes).

## Migrations

`alembic upgrade head` runs automatically on every web-service boot (`scripts/start.sh`).
For a single instance this is fine. If you ever run multiple web instances, move the
migration step to a Render **Pre-Deploy Command** instead.

## Manual / n8n triggering (optional)

`POST /api/v1/scrape/run` still works for ad-hoc runs and is what n8n would call. With a
cron in place (Render or GitHub Actions), n8n is not required — see `docs/n8n.md`.
