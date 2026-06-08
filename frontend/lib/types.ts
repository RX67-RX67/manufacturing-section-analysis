export interface MetricPoint {
  date: string;
  value: number;
  mom_pct?: number | null;
  yoy_pct?: number | null;
  category?: string | null;
}

export interface StatePoint {
  fips: string;
  value: number;
}

export interface Report {
  report_key: string;
  content: string;
  generated_at: string;
  model_used?: string;
}
