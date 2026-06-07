import hashlib
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Import our modules
from extractors import fred, bls, census, bea
from transformers.normalize import normalize
from loaders import supabase as db


def compute_hash(records: list[dict]) -> str:
    """Compute a deterministic MD5 hash of a list of records."""
    # Sort by date to ensure same hash regardless of order
    sorted_records = sorted(records, key=lambda r: r.get("date", ""))
    serialized = json.dumps(sorted_records, sort_keys=True, default=str)
    return hashlib.md5(serialized.encode()).hexdigest()


def trigger_report_refresh(report_key: str, data_hash: str):
    """
    Call the backend API to regenerate an AI report.
    The backend checks if data_hash has changed before calling Claude.
    """
    backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
    secret = os.environ["REPORT_SECRET"]
    try:
        response = requests.post(
            f"{backend_url}/api/reports/refresh",
            json={"report_key": report_key, "data_hash": data_hash},
            headers={"X-Report-Secret": secret},
            timeout=120,  # Claude calls can take up to 30s
        )
        response.raise_for_status()
        print(f"    Report '{report_key}' refreshed.")
    except Exception as e:
        print(f"    Warning: report refresh for '{report_key}' failed: {e}")


def run_source(name: str, extract_fn, transform_fn, upsert_fn):
    """
    Run one ETL source end-to-end. Catches exceptions so one failure
    doesn't stop the whole pipeline.
    """
    print(f"\n[{name}] Starting...")
    try:
        raw = extract_fn()
        normalized = transform_fn(raw)
        rows = upsert_fn(normalized)
        db.log_etl_run(name, "success", rows_upserted=rows)
        print(f"[{name}] Done — {rows} rows upserted.")
        return normalized
    except Exception as e:
        db.log_etl_run(name, "failed", error_msg=str(e))
        print(f"[{name}] FAILED: {e}")
        return []


def main():
    print("=== ETL Pipeline Starting ===\n")

    # --- Extract, transform, load each source ---

    fred_records  = run_source("FRED",   fred.extract_all,   normalize, db.upsert_fred)
    bls_records   = run_source("BLS",    bls.extract_all,    normalize, db.upsert_bls)
    census_records= run_source("Census", census.extract_all, normalize, db.upsert_census)
    bea_records   = run_source("BEA",    bea.extract_all,    normalize, db.upsert_bea)

    # --- Trigger AI report regeneration ---
    print("\n=== Triggering AI Report Refresh ===")

    # Map each chart report to the data it depends on
    report_data_map = {
        "chart:production":   [r for r in fred_records  if r.get("series_id") == "IPMAN"],
        "chart:capacity":     [r for r in fred_records  if r.get("series_id") == "CAPUTLMFG"],
        "chart:employment":   [r for r in fred_records  if r.get("series_id") == "MANEMP"],
        "chart:wages":        [r for r in fred_records  if r.get("series_id") == "CES3000000008"],
        "chart:bls_jobs":     bls_records,
        "chart:orders":       census_records,
        "chart:gdp":          bea_records,
        "summary":            fred_records + bls_records + census_records + bea_records,
    }

    for report_key, records in report_data_map.items():
        if records:
            data_hash = compute_hash(records)
            trigger_report_refresh(report_key, data_hash)

    print("\n=== Pipeline Complete ===")


if __name__ == "__main__":
    main()