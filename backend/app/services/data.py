import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_KEY"],
        )
    return _client


def get_fred_series(series_id: str, start: str = None, end: str = None) -> list[dict]:
    client = get_client()
    query = (
        client.table("fred_series")
        .select("date, value, mom_pct, yoy_pct")
        .eq("series_id", series_id)
        .order("date")
    )
    if start:
        query = query.gte("date", start)
    if end:
        query = query.lte("date", end)
    result = query.execute()
    return result.data


def get_bls_series(series_id: str, start: str = None, end: str = None) -> list[dict]:
    client = get_client()
    query = (
        client.table("bls_series")
        .select("date, value, mom_pct, yoy_pct")
        .eq("series_id", series_id)
        .order("date")
    )
    if start:
        query = query.gte("date", start)
    if end:
        query = query.lte("date", end)
    return query.execute().data


def get_census_data(category: str, industry: str = "MDM", start: str = None, end: str = None) -> list[dict]:
    client = get_client()
    query = (
        client.table("census_m3")
        .select("date, value, mom_pct, yoy_pct, category")
        .eq("category", category)
        .eq("industry", industry)
        .order("date")
    )
    if start:
        query = query.gte("date", start)
    if end:
        query = query.lte("date", end)
    return query.execute().data


def get_bea_data(table_name: str, line_desc: str = None, start: str = None, end: str = None) -> list[dict]:
    client = get_client()
    query = (
        client.table("bea_data")
        .select("date, line_desc, value")
        .eq("table_name", table_name)
        .order("date")
    )
    if line_desc:
        query = query.eq("line_desc", line_desc)
    if start:
        query = query.gte("date", start)
    if end:
        query = query.lte("date", end)
    return query.execute().data


def get_last_updated() -> str | None:
    client = get_client()
    result = (
        client.table("etl_runs")
        .select("ran_at")
        .eq("status", "success")
        .order("ran_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0]["ran_at"] if result.data else None