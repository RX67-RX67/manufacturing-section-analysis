from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .routers import metrics, reports
from .services import data as db

load_dotenv()

app = FastAPI(title="US Manufacturing Dashboard API")

# CORS: allow the frontend (on a different domain) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # in production, restrict to your Vercel URL
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics.router)
app.include_router(reports.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/last-updated")
def last_updated():
    ts = db.get_last_updated()
    return {"last_updated": ts}