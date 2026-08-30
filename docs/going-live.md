# Going live — ordered checklist

## 1. Test the email digest locally

1. Sign up at **resend.com** (free tier: 3,000 emails/month). Verify your account email.
2. **API Keys → Create API Key** → copy the `re_...` value.
3. Copy `backend/.env.example` to **`backend/.env`** (gitignored) and fill in:

   ```
   RESEND_API_KEY=re_xxxxxxxx
   NOTIFY_EMAIL=you@example.com          # must be your Resend signup email while using the test sender
   NOTIFY_FROM_EMAIL=onboarding@resend.dev
   NOTIFY_MIN_SCORE=0
   ```

   `docker compose` and a direct `uvicorn` both read this one file.

4. `docker compose up --build`
5. Add a company that has India software roles, e.g.:

   ```bash
   curl -X POST localhost:10000/api/v1/companies -H 'content-type: application/json' \
     -d '{"name":"Databricks","career_url":"https://boards.greenhouse.io/databricks"}'
   ```

6. `curl -X POST localhost:10000/api/v1/scrape/run -H 'content-type: application/json' -d '{}'`
7. When the run finishes (`GET /api/v1/scrape/runs`), check your inbox / spam. The digest
   lists the new relevant jobs grouped by company.

Notes:
- No email is sent if a run finds **0 new** relevant jobs. Check `GET /api/v1/jobs` first.
- `onboarding@resend.dev` only delivers to your own Resend account email. To send anywhere,
  verify a domain in Resend and set `NOTIFY_FROM_EMAIL=jobs@yourdomain.com`.
- To re-test from scratch: `docker compose down -v` wipes the DB, so the next run treats
  every job as new again.

## 2. Set dashboard config (before merging)

**Render** → your web service → **Environment**:

| Key | Value |
|---|---|
| `DATABASE_URL` | Supabase **direct connection** string (port 5432), not the transaction pooler |
| `RESEND_API_KEY` | `re_...` |
| `NOTIFY_EMAIL` | recipient(s) |
| `NOTIFY_FROM_EMAIL` | `onboarding@resend.dev` or a sender on your verified domain |
| `NOTIFY_MIN_SCORE` | e.g. `20` |

Also confirm the service's **Start Command** is blank (uses the Dockerfile) or `sh scripts/start.sh`.

**Vercel** → project → **Settings → Environment Variables**: `VITE_API_URL` = your Render URL.

## 3. Push and merge

```bash
git push -u origin chore/p0-cleanup
gh pr create --base main --title "Backend: scrapers, matching, scrape API, email digest" \
  --body "Foundation, 7 scrapers, matcher, scrape API, jobs/stats, ATS auto-detect, email digest"
gh pr checks --watch            # wait for CI to go green
gh pr merge --squash --delete-branch
git checkout main && git pull
```

No `gh`? Push the branch, open the PR on github.com, wait for the green check, click
**Squash and merge**.

The moment `main` updates:
- **Render** rebuilds the image, runs `alembic upgrade head` against Supabase (creates the
  4 tables + seeds keyword rules on first deploy), starts the API.
- **Vercel** rebuilds the frontend.

## 4. Turn on the scheduled scrape (GitHub Actions)

1. GitHub repo → **Settings → Secrets and variables → Actions → Variables** tab →
   **New repository variable**:
   - Name: `API_BASE_URL`
   - Value: your Render URL, no trailing slash (e.g. `https://job-handler-xxxx.onrender.com`)
2. **Settings → Actions → General** → "Allow all actions and reusable workflows" (usually on).
3. Test it: **Actions → Scheduled scrape → Run workflow**.
4. It then runs every 6 hours. Change the cadence by editing the `cron:` line in
   `.github/workflows/scrape.yml` and pushing.

Alternative: a **Render Cron Job** (dashboard → New → Cron Job, command
`python -m app.scrape_runner`, same env vars). Use **either** GitHub Actions **or** Render
Cron — not both.

## 5. The pipeline — what runs automatically

| Automation | Config | Trigger | Watch at | Change by |
|---|---|---|---|---|
| CI (lint + tests) | `.github/workflows/ci.yml` | every push / PR | GitHub → Actions | edit yml, push |
| Scheduled scrape | `.github/workflows/scrape.yml` | cron + manual | GitHub → Actions | edit `cron:`; the `API_BASE_URL` var |
| Backend deploy | Render dashboard settings | push to `main` | Render → service → Events / Logs | Render dashboard |
| Frontend deploy | Vercel dashboard settings | push to `main` | Vercel → Deployments | Vercel dashboard |

The GitHub Actions cron only **calls** `POST /scrape/run` on Render. The scrape, matching,
and the email all happen **inside the Render service** — which is why the email env vars
live on Render, not GitHub.

A scheduled run:

```
GitHub Actions (every 6h)
  └─ POST https://<render-url>/api/v1/scrape/run
       └─ Render backend: scrape every active company → match → store → email digest
  └─ polls GET /scrape/run/{id} until done; fails the Actions job if the run failed
```

## 6. Authentication (optional — off by default)

Every API route and the dashboard are open until you switch this on. Auth uses **Supabase
Auth** (same Supabase project as the database — no new service to host).

Accounts are created through the app's own **/register** page (username, email, password);
`POST /api/v1/auth/register` and `/login` wrap Supabase server-side.

1. **Supabase dashboard → Authentication → Sign In / Providers**: enable **Email**. Turn
   *Confirm email* **off** (there is no SMTP set up) — new registrations then get a session
   immediately.
2. **Authentication → URL Configuration**: set *Site URL* to your Vercel URL and add
   `http://localhost:5173/**` plus `https://job-handler-*.vercel.app/**` as redirect URLs.
3. **Settings → API Keys**: copy the *Project URL* (`https://<ref>.supabase.co`) and the
   `anon` `public` key.
4. Generate a service token for the cron: `openssl rand -hex 32`.
5. **Render → Environment**: add `AUTH_ENABLED=true`, `SUPABASE_URL=https://<ref>.supabase.co`,
   `SUPABASE_ANON_KEY=<anon key>`, `SERVICE_TOKEN=<the random hex>`. (Tokens are verified
   against the project's published JWKS keys — no JWT secret needed. Projects still on the
   legacy HS256 secret can set `SUPABASE_JWT_SECRET` from **Settings → JWT Keys** instead.)
6. **Vercel → Environment Variables**: add `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`.
7. **GitHub → Settings → Secrets and variables → Actions → Secrets**: add `SERVICE_TOKEN`
   with the same value as Render, so the scheduled scrape keeps working.
8. Redeploy both. Visiting `/graph` or `/profile` now redirects to `/login`; register your
   account at `/register`.

Leaving `AUTH_ENABLED` unset (or `false`) and the `VITE_SUPABASE_*` vars blank keeps the
app fully open — useful for local development.
