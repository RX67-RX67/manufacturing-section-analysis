import type { MetricPoint, Report } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Generic fetch with error handling
async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    next: { revalidate: 3600 },  // Next.js cache: revalidate every 1 hour
  });
  if (!res.ok) throw new Error(`API error: ${res.status} ${path}`);
  return res.json();
}

export const api = {
  fred: (seriesId: string, start?: string) =>
    apiFetch<MetricPoint[]>(
      `/api/metrics/fred/${seriesId}${start ? `?start=${start}` : ""}`
    ),

  bls: (seriesId: string) =>
    apiFetch<MetricPoint[]>(`/api/metrics/bls/${seriesId}`),

  census: (category: string) =>
    apiFetch<MetricPoint[]>(`/api/metrics/census?category=${category}`),

  bea: (table: string, line?: string) =>
    apiFetch<{ date: string; line_desc: string; value: number }[]>(
      `/api/metrics/bea?table=${table}${line ? `&line=${encodeURIComponent(line)}` : ""}`
    ),

  report: (key: string) =>
    apiFetch<Report>(`/api/reports/${key}`),

  lastUpdated: () =>
    apiFetch<{ last_updated: string }>("/api/last-updated"),
};