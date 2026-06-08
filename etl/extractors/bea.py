import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

BEA_BASE = "https://apps.bea.gov/api/data"

# The GDPbyIndustry dataset reports quarters as Roman numerals
QUARTER_MONTH = {"I": "01", "II": "04", "III": "07", "IV": "10"}

# Value Added by Industry (TableID 1) from the GDPbyIndustry dataset.
# Industry code 31G = Manufacturing. (NIPA table T10306, used previously,
# is a sector breakdown — Business/Households/Government — and has no
# "Manufacturing" line at all, which is why the chart was empty.)
TABLE_NAME = "GDPbyIndustry-1"
INDUSTRY_CODE = "31G"


def fetch_value_added(industry: str = INDUSTRY_CODE, frequency: str = "Q", year: str = "ALL") -> list[dict]:
    """
    Fetch quarterly Value Added ($ billions) for one industry from BEA's
    GDPbyIndustry dataset, Table 1.
    """
    params = {
        "UserID":       os.environ["BEA_API_KEY"],
        "method":       "GetData",
        "DataSetName":  "GDPbyIndustry",
        "TableID":      "1",
        "Industry":     industry,
        "Frequency":    frequency,   # "Q" = quarterly, "A" = annual
        "Year":         year,        # "ALL" = every year available
        "ResultFormat": "JSON",
    }

    for attempt in range(3):
        try:
            response = requests.get(BEA_BASE, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            break
        except requests.RequestException as e:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

    # GDPbyIndustry nests data under Results[0] > Data > [list of observations]
    results = data.get("BEAAPI", {}).get("Results", [])
    if isinstance(results, list):
        results = results[0] if results else {}
    rows = results.get("Data", [])

    records = []
    for item in rows:
        month = QUARTER_MONTH.get(item.get("Quarter", ""))
        if not month:
            continue  # skip annual rows; we only want quarterly
        date_str = f"{item['Year']}-{month}-01"

        try:
            value = float(item["DataValue"].replace(",", ""))
        except (ValueError, KeyError):
            continue

        records.append({
            "table_name": TABLE_NAME,
            "line_desc":  item.get("IndustrYDescription", ""),  # BEA misspells this field
            "date":       date_str,
            "value":      value,
        })

    return records


def extract_all() -> list[dict]:
    print(f"  Fetching BEA Value Added by Industry — Manufacturing ({INDUSTRY_CODE}, quarterly)...")
    records = fetch_value_added(INDUSTRY_CODE)
    print(f"    Got {len(records)} observations")
    return records
