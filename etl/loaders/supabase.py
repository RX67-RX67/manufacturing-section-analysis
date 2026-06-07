import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client | None = None


def get_client() -> Client:
    """Singleton pattern — create the Supabase client once, reuse it."""
    global _client
    if _client is None:
        _client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_KEY"],  # service role key bypasses row-level security
        )
    return _client


def upsert_fred(records: list[dict]) -> int:
    """Upsert FRED records. Returns number of rows affected."""
    if not records:
        return 0
    client = get_client()
    # on_conflict tells Supabase which columns form the unique key
    result = (
        client.table("fred_series")
        .upsert(records, on_conflict="series_id,date")
        .execute()
    )
    return len(result.data)


def upsert_bls(records: list[dict]) -> int:
    if not records:
        return 0
    client = get_client()
    result = (
        client.table("bls_series")
        .upsert(records, on_conflict="series_id,date")
        .execute()
    )
    return len(result.data)


def upsert_census(records: list[dict]) -> int:
    if not records:
        return 0
    client = get_client()
    result = (
        client.table("census_m3")
        .upsert(records, on_conflict="category,industry,date")
        .execute()
    )
    return len(result.data)


def upsert_bea(records: list[dict]) -> int:
    if not records:
        return 0
    client = get_client()
    result = (
        client.table("bea_data")
        .upsert(records, on_conflict="table_name,line_desc,date")
        .execute()
    )
    return len(result.data)


def log_etl_run(source: str, status: str, rows_upserted: int = 0, error_msg: str = None):
    """Write one row to the etl_runs audit table."""
    client = get_client()
    client.table("etl_runs").insert({
        "source":        source,
        "status":        status,
        "rows_upserted": rows_upserted,
        "error_msg":     error_msg,
    }).execute()


def upsert_ai_report(report_key: str, content: str, data_hash: str, model_used: str):
    """Store or update a cached AI report."""
    client = get_client()
    client.table("ai_reports").upsert({
        "report_key":  report_key,
        "content":     content,
        "data_hash":   data_hash,
        "model_used":  model_used,
    }, on_conflict="report_key").execute()


def get_ai_report(report_key: str) -> dict | None:
    """Retrieve a cached AI report by key. Returns None if not found."""
    client = get_client()
    result = (
        client.table("ai_reports")
        .select("*")
        .eq("report_key", report_key)
        .execute()
    )
    return result.data[0] if result.data else None