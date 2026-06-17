# Manufacturing Section Analysis

A dashboard tracking the state of U.S. manufacturing, built from public economic data (FRED, BLS, BEA, Census) with AI-generated narrative reports.

## Architecture

```
etl/        Python pipeline that pulls FRED/BLS/BEA/Census data, normalizes it, and upserts into Supabase
backend/    FastAPI service exposing metrics + AI report endpoints, backed by Supabase
frontend/   Next.js dashboard (charts, state map, executive summary)
supabase/   SQL migrations for the Postgres schema
```

Data flow: `etl/pipeline.py` extracts from each source, normalizes the records, and loads them into Supabase. After a successful load it calls the backend's `/api/reports/refresh` endpoint, which regenerates an AI report (via Claude) only if the underlying data hash changed. The frontend reads metrics and reports from the backend API.

## Components

### ETL (`etl/`)
- `extractors/` — one module per data source (`fred.py`, `bls.py`, `bea.py`, `census.py`, `census_cbp.py`)
- `transformers/normalize.py` — normalizes raw API responses into a common record shape
- `loaders/supabase.py` — upserts normalized records and logs each run
- `pipeline.py` — orchestrates extract → transform → load per source, then triggers report refresh

Run it with:
```bash
cd etl
pip install -r requirements.txt
python pipeline.py
```

### Backend (`backend/`)
FastAPI app exposing:
- `GET /api/health`, `GET /api/last-updated`
- `GET /api/metrics/...` — time-series metrics by source
- `GET /api/reports/{report_key}` — cached AI report
- `POST /api/reports/refresh` — regenerate a report (called by the ETL pipeline, requires `X-Report-Secret`)

Run it with:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (`frontend/`)
Next.js app rendering the dashboard. See `frontend/README.md` for framework-specific commands.
```bash
cd frontend
npm install
npm run dev
```

### Database (`supabase/`)
SQL migrations defining the schema, including row-level security policies. Apply them via the Supabase CLI or dashboard.

## Environment variables

Set these in `.env` (used by `etl/` and `backend/`):

| Variable | Purpose |
|---|---|
| `FRED_API_KEY` | FRED data access |
| `BLS_API_KEY` | BLS data access |
| `BEA_API_KEY` | BEA data access |
| `CENSUS_API_KEY` | Census data access |
| `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` | Database access |
| `BACKEND_URL` | Backend URL the ETL pipeline calls to trigger report refresh |
| `REPORT_SECRET` | Shared secret authorizing report refresh requests |
| `ANTHROPIC_API_KEY` | Claude API access for AI-generated reports |

The frontend uses its own `frontend/.env.local` for the backend API URL.
