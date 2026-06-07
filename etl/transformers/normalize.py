import pandas as pd


def normalize(records: list[dict], value_col: str = "value") -> list[dict]:
    """
    Given a list of raw records (each with at least 'date' and a value column),
    return the same records with added mom_pct and yoy_pct columns,
    sorted by date, with nulls removed.
    
    mom_pct = month-over-month % change
    yoy_pct = year-over-year % change (vs same month 12 periods ago)
    """
    if not records:
        return []

    df = pd.DataFrame(records)

    # Ensure date column is a proper datetime type (not just a string)
    df["date"] = pd.to_datetime(df["date"])

    # Sort oldest to newest
    df = df.sort_values("date").reset_index(drop=True)

    # Drop rows where the main value is missing
    df = df.dropna(subset=[value_col])

    # Compute derived columns grouped by series_id (if that column exists)
    # This prevents mixing different series when computing changes
    group_cols = []
    for col in ["series_id", "category", "industry", "table_name", "line_desc"]:
        if col in df.columns:
            group_cols.append(col)

    if group_cols:
        df["mom_pct"] = df.groupby(group_cols)[value_col].pct_change(1) * 100
        df["yoy_pct"] = df.groupby(group_cols)[value_col].pct_change(12) * 100
    else:
        df["mom_pct"] = df[value_col].pct_change(1) * 100
        df["yoy_pct"] = df[value_col].pct_change(12) * 100

    # Round to 2 decimal places — Supabase stores NUMERIC, not float64
    df["mom_pct"] = df["mom_pct"].round(2)
    df["yoy_pct"] = df["yoy_pct"].round(2)

    # Convert dates back to ISO strings for JSON serialization
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # Replace NaN with None (Python's null) — pandas NaN is not JSON serializable
    import math
    records = df.to_dict("records")
    return [
        {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in row.items()}
        for row in records
    ]