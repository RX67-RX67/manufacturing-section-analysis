import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

CBP_BASE = "https://api.census.gov/data/{year}/cbp"

# County Business Patterns publishes one annual snapshot per year, with roughly
# an 18-month lag (the 2022 vintage was the latest available as of writing).
# Manufacturing = NAICS sector 31-33.
YEAR = 2022
NAICS_CODE = "31-33"


def fetch_state_employment(year: int = YEAR, naics: str = NAICS_CODE) -> list[dict]:
    """
    Fetch total manufacturing employment (EMP) by state for one year from
    the Census County Business Patterns dataset.
    Returns a list of dicts: [{"fips": "06", "year": 2022, "value": 1160856}, ...]
    """
    params = {
        "get": "EMP",
        "for": "state:*",
        "NAICS2017": naics,
        "key": os.environ.get("CENSUS_API_KEY", ""),
    }

    for attempt in range(3):
        try:
            response = requests.get(CBP_BASE.format(year=year), params=params, timeout=30)
            response.raise_for_status()
            raw = response.json()
            break
        except requests.RequestException as e:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

    # Census returns an array of arrays; first row is the header.
    if not raw or len(raw) < 2:
        return []

    header = raw[0]
    emp_idx   = header.index("EMP")
    fips_idx  = header.index("state")

    records = []
    for row in raw[1:]:
        try:
            value = float(row[emp_idx])
        except (ValueError, TypeError):
            continue
        records.append({
            "fips":  row[fips_idx],
            "year":  year,
            "value": value,
        })

    return records


def extract_all() -> list[dict]:
    print(f"  Fetching Census CBP manufacturing employment by state ({YEAR})...")
    records = fetch_state_employment()
    print(f"    Got {len(records)} observations")
    return records
