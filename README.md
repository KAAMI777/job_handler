# Job Agent

AI-assisted job aggregation platform. It checks 50–100 company career pages on a schedule,
extracts software-related roles, filters and scores them, and shows the results in a
dashboard.

## Architecture

```
Frontend (Vercel)  ->  FastAPI API (Render)  ->  Supabase PostgreSQL
                              ^
                       n8n Cloud scheduler (calls POST /api/v1/scrape/run)
```

The backend owns all scraping. n8n only triggers runs; the frontend never scrapes.

## Repository layout

| Path        | Contents                                             |
|-------------|------------------------------------------------------|
| `backend/`  | FastAPI service, SQLAlchemy models, scrapers          |
| `frontend/` | React + Vite dashboard                                |
| `docs/`     | Architecture notes and decision records              |

## Local development

### Everything at once (Docker)

```bash
docker compose up --build
```

- API + Swagger UI: <http://localhost:10000/docs>
- Postgres is created and migrated automatically; data persists in a named volume.

Try it:

```bash
curl -X POST localhost:10000/api/v1/companies \
  -H 'content-type: application/json' \
  -d '{"name":"Discord","career_url":"https://boards.greenhouse.io/discord","parser_type":"greenhouse"}'

curl -X POST localhost:10000/api/v1/scrape/run -H 'content-type: application/json' -d '{}'
curl localhost:10000/api/v1/scrape/runs      # poll until status != running
curl localhost:10000/api/v1/jobs             # matched jobs
curl localhost:10000/api/v1/stats            # dashboard counts
```

### Backend only (no Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # point DATABASE_URL at any Postgres
alembic upgrade head          # create tables
uvicorn app.main:app --reload
```

Health check: <http://127.0.0.1:8000/health>

### Frontend

```bash
cd frontend
npm install
cp .env.example .env          # VITE_API_URL defaults to the local backend
npm run dev
```

## Deployment

| Component | Host   | Notes                                            |
|-----------|--------|--------------------------------------------------|
| Backend   | Render | Docker build from `backend/Dockerfile`; `DATABASE_URL` set in Render env; binds `$PORT` |
| Frontend  | Vercel | `VITE_API_URL` set in Vercel project settings     |
| Database  | Supabase | PostgreSQL; connection string stored in Render only |
