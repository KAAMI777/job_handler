# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Existing codebase.

- **Backend:** FastAPI + SQLAlchemy 2.0 + Alembic on Postgres (Supabase), packaged
  with Docker, deployed on Render.
- **Frontend:** React 19 + Vite, plain JavaScript (not TypeScript), deployed on Vercel.
- **Scheduling:** a GitHub Actions cron (or a Render Cron Job) calls the scrape endpoint
  on an interval.
- **Planned dashboard additions:** react-router, TanStack Query, Tailwind CSS.

## Users

Primary user is the project owner — a software engineer job-seeking in India who watches a
self-chosen list of companies for SDE / backend / frontend / fullstack / platform roles.
They work from two places: the dashboard and an email digest.

Single user today, with no authentication. Intent is "me now, others later": keep the
layout and data model friendly to adding accounts and per-user company lists later, but
multi-tenancy is not built and not in current scope.

## Product Purpose

An AI-assisted job aggregation tool. The user adds a company by pasting a careers-page
link; the system detects which applicant-tracking system (ATS) that company uses and, on a
schedule, scrapes every watched company's openings, keeps only India-based full-time
software roles, scores each by keyword relevance, stores them, and surfaces them in a
dashboard plus an email digest of newly found matches.

Success: the user sees relevant new roles across many companies without visiting each
careers page, ranked so the strongest matches are obvious, and never re-sees a posting they
already dismissed.

## Positioning

- **vs. general job boards (LinkedIn, Naukri, Indeed):** this is a personal watchlist. The
  user picks the exact companies; the matcher applies *their* role/keyword rules with
  weighted scoring rather than a global recommendation feed.
- **vs. single-ATS scrapers:** one pasted link is enough — the system auto-detects and
  reads seven sources (Greenhouse, Lever, Ashby, Workday, SmartRecruiters, plus Amazon and
  Netflix).
- **vs. a raw scrape:** deterministic dedup + first-seen tracking means the email and the
  "new" counts only ever reflect genuinely new postings.

## Operating Context

- User pastes a company careers URL (marketing page or ATS board) → the backend resolves
  the ATS and stores the canonical board URL alongside the original.
- A scheduled run (~every 6h) triggers one full scrape; only one run executes at a time.
- Each run: scrape all active companies → filter (India, full-time, not internship, title
  matches a keyword) → score 0–100 → upsert on a deterministic hash (update in place, keep
  first-seen / last-seen, mark vanished postings inactive) → email a digest of jobs first
  seen in that run, grouped by company.
- User reviews matches in the dashboard and clicks through to each company's own apply page.
- Keyword rules (role → keyword → weight) live in the database, seeded with a starter set
  for software_engineer / backend / frontend / fullstack / platform.

## Capabilities and Constraints

- Company CRUD with ATS auto-detection; a resolve endpoint previews detection without
  saving; when a page is fully client-rendered the user supplies the ATS type and board
  URL explicitly.
- Scrapers: Greenhouse, Lever, Ashby, Workday, SmartRecruiters (multi-company), Amazon and
  Netflix (single-employer, India-scoped at the source API). Google / Apple / Microsoft /
  Meta are **not** supported — their public APIs are gated and would need a headless
  browser.
- Matcher: rule-based India detection (Indian city names + "remote India/Asia"), keyword
  scoring on the job **title** only, excludes internships and anything not full-time.
- Run history and counts; a jobs list endpoint (paginated; filter by company, minimum
  score, role, relevance) and a stats endpoint for dashboard cards.
- Email digest via Resend, opt-in through environment variables (recipient, minimum score,
  from-address). The free Resend sender only delivers to the account owner's own address.
- **No authentication** — every API route and the dashboard are open. Deliberate for now;
  revisit before any non-personal use.
- Scraping is **sequential** inside one background task / cron process. Fine for tens of
  companies; a worker queue is the path beyond ~50, and large employers (thousands of
  postings) take 1–2 minutes each.
- Scope is India + software roles; both are encoded in the matcher and changeable later.

## Brand Commitments

Name: **Job Agent** (used in the app header and README). No logo, color system, typography,
or other identity assets committed. Voice is not yet defined.

## Evidence on Hand

- Verified working end-to-end against live ATS APIs: Databricks (858 postings → 41 India
  software matches), Amazon (~2,300 India roles), NVIDIA via Workday (~2,000 India roles),
  Razorpay via Greenhouse (~17 India roles), Figma / Discord / Notion (US companies,
  correctly 0 India matches).
- Real matched-job examples: "SDE II – Backend, Cross Border Shopping | Bengaluru"
  (score 40), "Cross-domain Full stack Software Engineer | Bangalore" (score 40).
- No users, testimonials, customers, pricing, or usage metrics — a personal tool in active
  development.

## Product Principles

- The user's watchlist and keyword rules *are* the product's point of view; the system
  curates a chosen set, it does not recommend from a global pool.
- Only surface genuinely new, genuinely relevant postings — dedup and first-seen tracking
  exist so the dashboard and email never cry wolf.
- One pasted link should be enough; the system does the ATS detective work.
- The dashboard is for operating — scan, decide, apply — not for browsing. The fastest path
  from "a new role exists" to "applied" wins.
- Keep single-user simple now, but design nothing that a second user would force a rewrite
  of.

## Accessibility & Inclusion

No product-specific requirement established. Standard web accessibility expectations apply
(keyboard operability, sufficient contrast, semantic structure).
