from pydantic import BaseModel
from typing import Optional


class MetricPoint(BaseModel):
    """One data point in a time series."""
    date: str
    value: float
    mom_pct: Optional[float] = None
    yoy_pct: Optional[float] = None
    category: Optional[str] = None


class ReportResponse(BaseModel):
    """A cached AI report."""
    report_key: str
    content: str
    generated_at: str
    model_used: Optional[str] = None


class ReportRefreshRequest(BaseModel):
    """Body sent by the ETL pipeline to trigger report regeneration."""
    report_key: str
    data_hash: str