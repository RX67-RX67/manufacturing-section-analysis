import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

BLS_BASE = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

BLS_SERIES = {
    "CES3000000001": "Manufacturing Employment (thousands)",
    "PCU3313--3313--": "Producer Price Index: Manufacturing",
}


def fetch_series(series_ids: list[str], start_year: int = 2010, end_year: int = 2024) -> list[dict]:
    """
    BLS API accepts up to 50 series at once in a POST body.
    Returns normalized records.
    """
    headers = {"Content-type": "application/json"}
    payload = {
        "seriesid":          series_ids,
        "startyear":         str(start_year),
        "endyear":           str(end_year),
        "registrationkey":   os.environ["BLS_API_KEY"],
    }

    for attempt in range(3):
        try:
            response = requests.post(
                BLS_BASE,
                data=json.dumps(payload),  # serialize dict to JSON string
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            break
        except requests.RequestException as e:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

    if data.get("status") != "REQUEST_SUCCEEDED":
        raise ValueError(f"BLS API error: {data.get('message', 'unknown')}")

    records = []
    for series in data.get("Results", {}).get("series", []):
        sid = series["seriesID"]
        for point in series.get("data", []):
            # BLS returns year + period like "M01" (January) through "M12"
            if not point["period"].startswith("M"):
                continue  # skip annual "M13" entries
            month = point["period"][1:]  # "M01" -> "01"
            date_str = f"{point['year']}-{month}-01"
            try:
                value = float(point["value"].replace(",", ""))
            except (ValueError, AttributeError):
                continue
            records.append({
                "series_id": sid,
                "date":      date_str,
                "value":     value,
            })

    return records


def extract_all() -> list[dict]:
    series_ids = list(BLS_SERIES.keys())
    print(f"  Fetching BLS series: {series_ids}")
    records = fetch_series(series_ids)
    print(f"    Got {len(records)} observations")
    return records