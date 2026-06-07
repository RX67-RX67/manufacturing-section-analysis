import os
import time
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

# Census time series API endpoint for M3 survey
CENSUS_BASE = "https://api.census.gov/data/timeseries/eits/m3"

# We want three categories. The Census API identifies these via the
# "data_type_code" predicate (VS = value of shipments, NO = new orders,
# TI = total inventories) — not via a "category" predicate, which doesn't exist.
CATEGORIES = ["shipments", "neword", "inventories"]
CATEGORY_MAP = {"shipments": "shipments", "neword": "orders", "inventories": "inventories"}
DATA_TYPE_CODES = {"shipments": "VS", "neword": "NO", "inventories": "TI"}

# Industries to pull (NAICS-based codes). The Census API identifies these via
# the "category_code" predicate — not "industry", which doesn't exist.
# (MDM = Durable goods manufacturing, MNM = Non-durable goods manufacturing;
# MDM + MNM = MTM, the total manufacturing series.)
INDUSTRIES = ["MDM",  # Durable goods manufacturing
              "MNM"]  # Non-durable goods manufacturing


def fetch_category(category: str, industry: str = "MDM") -> list[dict]:
    """Fetch one category (shipments/orders/inventories) for one industry."""
    params = {
        "get":             "cell_value,error_data,time_slot_id",
        "for":             "us:*",
        "category_code":   industry,
        "data_type_code":  DATA_TYPE_CODES[category],
        "seasonally_adj":  "yes",
        "time":            f"from 2010 to {datetime.date.today().year}",
        "key":             os.environ.get("CENSUS_API_KEY", ""),
    }

    for attempt in range(3):
        try:
            response = requests.get(CENSUS_BASE, params=params, timeout=30)
            response.raise_for_status()
            raw = response.json()
            break
        except requests.RequestException as e:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

    # Census returns an array of arrays; first row is the header. The "time"
    # predicate is echoed back as its own column (e.g. "2024-01"), separate
    # from "time_slot_id" (an internal slot index, not a date).
    if not raw or len(raw) < 2:
        return []

    header = raw[0]
    value_idx = header.index("cell_value")
    time_idx  = header.index("time")

    records = []
    for row in raw[1:]:
        try:
            date_str = row[time_idx] + "-01"  # "2024-01" -> "2024-01-01"
            value = float(row[value_idx])
        except (ValueError, IndexError):
            continue
        records.append({
            "category": CATEGORY_MAP.get(category, category),
            "industry": industry,
            "date":     date_str,
            "value":    value,
        })

    return records


def extract_all() -> list[dict]:
    all_records = []
    for industry in INDUSTRIES:
        for category in CATEGORIES:
            print(f"  Fetching Census M3 {category} / {industry}...")
            records = fetch_category(category, industry)
            print(f"    Got {len(records)} observations")
            all_records.extend(records)
    return all_records


