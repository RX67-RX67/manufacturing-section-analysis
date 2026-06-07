from fastapi import APIRouter, Query
from ..services import data as db
from ..schemas import MetricPoint

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/fred/{series_id}", response_model=list[MetricPoint])
def get_fred(
    series_id: str,
    start: str = Query(None, description="Start date YYYY-MM-DD"),
    end:   str = Query(None, description="End date YYYY-MM-DD"),
):
    """Return time-series data for a FRED series."""
    return db.get_fred_series(series_id, start, end)


@router.get("/bls/{series_id}", response_model=list[MetricPoint])
def get_bls(
    series_id: str,
    start: str = Query(None),
    end:   str = Query(None),
):
    return db.get_bls_series(series_id, start, end)


@router.get("/census", response_model=list[MetricPoint])
def get_census(
    category: str = Query(..., description="shipments | orders | inventories"),
    industry: str = Query("MDM"),
    start:    str = Query(None),
    end:      str = Query(None),
):
    return db.get_census_data(category, industry, start, end)


@router.get("/bea", response_model=list[dict])
def get_bea(
    table: str = Query("T10306"),
    line:  str = Query(None),
    start: str = Query(None),
    end:   str = Query(None),
):
    return db.get_bea_data(table, line, start, end)