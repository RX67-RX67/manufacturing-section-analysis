import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

BEA_BASE = "https://apps.bea.gov/api/data"


def fetch_nipa(table_name: str, frequency: str = "Q", year: str = "ALL") -> list[dict]:
    """
    Fetch NIPA (National Income and Product Accounts) table from BEA.
    Returns records for all lines in the table.
    """
    params = {
        "UserID":       os.environ["BEA_API_KEY"],
        "method":       "GetData",
        "DataSetName":  "NIPA",
        "TableName":    table_name,
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

    # BEA nests data under Results > Data > [list of observations]
    results = data.get("BEAAPI", {}).get("Results", {}).get("Data", [])

    records = []
    for item in results:
        # TimePeriod is like "2024Q1" for quarterly or "2024" for annual
        period = item.get("TimePeriod", "")
        if "Q" in period:
            year_str, quarter = period.split("Q")
            # Convert quarter to first month of that quarter
            month = {"1": "01", "2": "04", "3": "07", "4": "10"}[quarter]
            date_str = f"{year_str}-{month}-01"
        else:
            date_str = f"{period}-01-01"  # annual data -> Jan 1 of that year

        try:
            value = float(item["DataValue"].replace(",", ""))
        except (ValueError, KeyError):
            continue

        records.append({
            "table_name": table_name,
            "line_desc":  item.get("LineDescription", ""),
            "date":       date_str,
            "value":      value,
        })

    return records


def extract_all() -> list[dict]:
    print("  Fetching BEA NIPA Table T10306 (GDP by industry, quarterly)...")
    records = fetch_nipa("T10306", frequency="Q")
    print(f"    Got {len(records)} observations")
    return records