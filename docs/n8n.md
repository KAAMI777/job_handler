# n8n Cloud integration

n8n only *triggers* scrapes. All scraping, matching and storage lives in the backend.

> **You may not need this.** The recommended setup schedules scraping with a Render
> Cron Job (`docs/deployment.md`), which needs no n8n. Use this doc only if you want
> n8n to own the schedule instead, or for ad-hoc triggering.

## Workflow

1. **Schedule Trigger** — e.g. every 6 hours.
2. **HTTP Request** — start the run:
   - `POST https://<api-host>/api/v1/scrape/run`
   - Body: `{ "run_type": "scheduled" }`
   - Expected: `202` with `{ "run_id": <int>, "status": "running" }`
   - `409` means a run is already in progress — the body carries that run's id; let
     the workflow end quietly.
3. **Wait** — 30–60 seconds.
4. **HTTP Request** — poll:
   - `GET https://<api-host>/api/v1/scrape/run/{{ $json.run_id }}`
   - Repeat (loop back to *Wait*) while `status == "running"`.
5. When `status` is `success` / `partial` / `failed`, read the counts:
   `companies_checked`, `new_jobs`, `failed`, `duration_seconds`. Route `failed`
   / `partial` to an alert if desired.

## Notes

- The endpoint is currently unauthenticated (auth is a later milestone). Keep the
  API host out of public docs and restrict by network if the platform allows.
- One run executes at a time. Runs left stuck by a crashed worker are auto-failed
  after 3 hours so the next trigger can proceed.
