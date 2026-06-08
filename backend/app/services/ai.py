import os
import anthropic
from dotenv import load_dotenv
from . import data as db

load_dotenv()

MODEL = "claude-sonnet-4-6"

CHART_PROMPTS = {
    "chart:production": (
        "Industrial Production Index: Manufacturing (IPMAN)",
        "manufacturing output volume relative to 2017 baseline"
    ),
    "chart:capacity": (
        "Capacity Utilization: Manufacturing (MCUMFN)",
        "percentage of manufacturing capacity currently in use"
    ),
    "chart:employment": (
        "Manufacturing Employment (MANEMP)",
        "total number of manufacturing workers in thousands"
    ),
    "chart:wages": (
        "Average Hourly Earnings: Manufacturing",
        "average hourly wage for manufacturing workers in USD"
    ),
    "chart:bls_jobs": (
        "BLS Manufacturing Employment (CES3000000001)",
        "detailed BLS establishment survey employment count"
    ),
    "chart:orders": (
        "Census M3: New Orders",
        "new manufacturing orders in millions of dollars"
    ),
    "chart:gdp": (
        "Manufacturing Value Added (BEA GDP by Industry)",
        "manufacturing contribution to GDP in billions of dollars"
    ),
}

CHART_REPORT_PROMPT = """You are an economic analyst specializing in U.S. manufacturing.

Metric: {metric_name}
Description: {metric_description}

Data (last 24 months, chronological):
{data_json}

Key statistics:
- Most recent value: {current}
- Month-over-month change: {mom_pct}%
- Year-over-year change: {yoy_pct}%

In one short paragraph, cover:
1. What the current level and trend indicate
2. What the month-over-month and year-over-year changes signal
3. What this means for overall manufacturing health

Tone: professional, data-driven, accessible to a non-economist reader.
Format: prose only, no bullet points or headers.
Hard limit: under 100 words total. Be concise — do not pad."""

SUMMARY_PROMPT = """You are a senior economic analyst covering U.S. manufacturing.

Below are summaries of key manufacturing indicators. Write a brief executive
summary covering: overall sector health, labor market conditions,
production and capacity trends, order book dynamics, and GDP contribution.
Conclude with a one-sentence forward-looking observation.

Indicator data:
{indicators_json}

Tone: authoritative but accessible. Prose paragraphs only, no headers or bullets.
Hard limit: under 500 words total. Be concise — do not pad."""


def _fetch_chart_data(report_key: str) -> list[dict]:
    """Fetch the relevant data records for a given report key."""
    if report_key == "chart:production":
        return db.get_fred_series("IPMAN")[-24:]
    elif report_key == "chart:capacity":
        return db.get_fred_series("MCUMFN")[-24:]
    elif report_key == "chart:employment":
        return db.get_fred_series("MANEMP")[-24:]
    elif report_key == "chart:wages":
        return db.get_fred_series("CES3000000008")[-24:]
    elif report_key == "chart:bls_jobs":
        return db.get_bls_series("CES3000000001")[-24:]
    elif report_key == "chart:orders":
        return db.get_census_data("orders")[-24:]
    elif report_key == "chart:gdp":
        return db.get_bea_data("GDPbyIndustry-1")[-12:]  # quarterly, so fewer points
    return []


def generate_report(report_key: str, data_hash: str):
    """
    Generate and cache an AI report for the given report_key.
    Called as a background task from the /refresh endpoint.
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    if report_key == "summary":
        _generate_summary(client, data_hash)
    elif report_key in CHART_PROMPTS:
        _generate_chart_report(client, report_key, data_hash)
    else:
        print(f"Unknown report_key: {report_key}")


def _generate_chart_report(client: anthropic.Anthropic, report_key: str, data_hash: str):
    metric_name, metric_desc = CHART_PROMPTS[report_key]
    records = _fetch_chart_data(report_key)

    if not records:
        return

    # Compute key stats from the last record
    last = records[-1]
    current = last.get("value", "N/A")
    mom_pct = last.get("mom_pct", "N/A")
    yoy_pct = last.get("yoy_pct", "N/A")

    prompt = CHART_REPORT_PROMPT.format(
        metric_name=metric_name,
        metric_description=metric_desc,
        data_json=records,
        current=current,
        mom_pct=mom_pct,
        yoy_pct=yoy_pct,
    )

    message = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    content = message.content[0].text

    # Store in database
    db_client = db.get_client()
    db_client.table("ai_reports").upsert({
        "report_key":  report_key,
        "content":     content,
        "data_hash":   data_hash,
        "model_used":  MODEL,
    }, on_conflict="report_key").execute()

    print(f"  Report generated: {report_key}")


def _generate_summary(client: anthropic.Anthropic, data_hash: str):
    # Gather the most recent value for each indicator
    indicators = {}
    for key in CHART_PROMPTS:
        records = _fetch_chart_data(key)
        if records:
            last = records[-1]
            name, _ = CHART_PROMPTS[key]
            indicators[name] = {
                "current": last.get("value"),
                "mom_pct": last.get("mom_pct"),
                "yoy_pct": last.get("yoy_pct"),
                "date":    last.get("date"),
            }

    prompt = SUMMARY_PROMPT.format(indicators_json=indicators)

    message = client.messages.create(
        model=MODEL,
        max_tokens=900,
        messages=[{"role": "user", "content": prompt}],
    )
    content = message.content[0].text

    db_client = db.get_client()
    db_client.table("ai_reports").upsert({
        "report_key":  "summary",
        "content":     content,
        "data_hash":   data_hash,
        "model_used":  MODEL,
    }, on_conflict="report_key").execute()

    print("  Summary report generated.")