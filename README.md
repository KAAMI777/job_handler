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

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit DATABASE_URL
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
