import hashlib
import os
from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from ..schemas import ReportResponse, ReportRefreshRequest
from ..services import data as db
from ..services.ai import generate_report, PROMPT_VERSION

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{report_key}", response_model=ReportResponse)
def get_report(report_key: str):
    """Return a cached AI report by key."""
    client = db.get_client()
    result = (
        client.table("ai_reports")
        .select("*")
        .eq("report_key", report_key)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Report not found")
    row = result.data[0]
    return ReportResponse(
        report_key=row["report_key"],
        content=row["content"],
        generated_at=row["generated_at"],
        model_used=row.get("model_used"),
    )


@router.post("/refresh")
def refresh_report(
    body: ReportRefreshRequest,
    background_tasks: BackgroundTasks,
    x_report_secret: str = Header(...),  # requires X-Report-Secret header
):
    """
    Trigger AI report regeneration. Called by the ETL pipeline.
    Uses BackgroundTasks so the response returns immediately.
    """
    if x_report_secret != os.environ["REPORT_SECRET"]:
        raise HTTPException(status_code=403, detail="Invalid secret")

    # Fold PROMPT_VERSION into the comparison hash so that editing a prompt
    # template invalidates the cache too — not just changes to the source
    # data. Otherwise the pipeline would keep sending the same data_hash and
    # we'd keep serving a stale report generated under the old prompt.
    cache_key = hashlib.md5(f"{body.data_hash}:{PROMPT_VERSION}".encode()).hexdigest()

    # Check if data (or the prompt) has changed by comparing hash
    client = db.get_client()
    existing = (
        client.table("ai_reports")
        .select("data_hash")
        .eq("report_key", body.report_key)
        .execute()
    )
    if existing.data and existing.data[0]["data_hash"] == cache_key:
        return {"status": "skipped", "reason": "data unchanged"}

    # Run report generation in the background (doesn't block the HTTP response)
    background_tasks.add_task(generate_report, body.report_key, cache_key)
    return {"status": "queued", "report_key": body.report_key}