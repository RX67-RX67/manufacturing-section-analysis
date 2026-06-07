import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# Census time series API endpoint for M3 survey
CENSUS_BASE = "https://api.census.gov/data/timeseries/eits/m3"

# We want three categories
CATEGORIES = ["shipments", "neword", "inventories"]
CATEGORY_MAP = {"shipments": "shipments", "neword": "orders", "inventories": "inventories"}

# Industries to pull (NAICS-based codes)
INDUSTRIES = ["MDM",  # All manufacturing
              "MNDM"] # Non-durable goods manufacturing


def fetch_category(category: str, industry: str = "MDM") -> list[dict]:
    """Fetch one category (shipments/orders/inventories) for one industry."""
    params = {
        "get":      f"cell_value,error_data,time_slot_id",
        "for":      "us:*",
        "category": category,
        "data_type_code": "MSM",
        "industry": industry,
        "key":      os.environ.get("CENSUS_API_KEY", ""),
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

    # Census returns an array of arrays; first row is the header
    # [["cell_value","error_data","time_slot_id","us"], ["102543","1.2","2024-01","1"], ...]
    if not raw or len(raw) < 2:
        return []

    header = raw[0]
    value_idx = header.index("cell_value")
    time_idx  = header.index("time_slot_id")

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


