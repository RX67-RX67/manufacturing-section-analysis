import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()  # reads .env file into os.environ

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

# These are the series we want from FRED
# Key = our internal name, value = FRED's series code
FRED_SERIES = {
    "IPMAN":          "Industrial Production: Manufacturing",
    "CAPUTLMFG":      "Capacity Utilization: Manufacturing",
    "MANEMP":         "Manufacturing Employment",
    "CES3000000008":  "Avg Hourly Earnings: Manufacturing",
}


def fetch_series(series_id: str, start_date: str = "2010-01-01") -> list[dict]:
    """
    Fetch all observations for one FRED series.
    Returns a list of dicts: [{"series_id": ..., "date": ..., "value": ...}, ...]
    
    Retries up to 3 times with exponential backoff on failure.
    """
    params = {
        "series_id":          series_id,
        "api_key":            os.environ["FRED_API_KEY"],
        "file_type":          "json",
        "observation_start":  start_date,
        "sort_order":         "asc",
    }

    for attempt in range(3):
        try:
            response = requests.get(FRED_BASE, params=params, timeout=30)
            response.raise_for_status()  # raises exception for 4xx/5xx responses
            data = response.json()
            break
        except requests.RequestException as e:
            if attempt == 2:
                raise  # re-raise after 3 failures
            wait = 2 ** attempt  # 1s, 2s, 4s
            print(f"  FRED {series_id} attempt {attempt+1} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)

    records = []
    for obs in data.get("observations", []):
        # FRED uses "." for missing values — skip those
        if obs["value"] == ".":
            continue
        records.append({
            "series_id": series_id,
            "date":      obs["date"],         # already "YYYY-MM-DD" string
            "value":     float(obs["value"]),
            "unit":      FRED_SERIES.get(series_id, ""),
        })

    return records


def extract_all() -> list[dict]:
    """Extract all configured FRED series. Returns combined list of records."""
    all_records = []
    for series_id in FRED_SERIES:
        print(f"  Fetching FRED {series_id}...")
        records = fetch_series(series_id)
        print(f"    Got {len(records)} observations")
        all_records.extend(records)
    return all_records