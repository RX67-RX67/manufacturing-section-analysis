"use client";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts";
import { MetricPoint } from "@/lib/types";

// Census returns separate records per category; we need to merge by date
function mergeByDate(records: MetricPoint[]): Record<string, any>[] {
  const map = new Map<string, Record<string, any>>();
  for (const r of records) {
    const entry = map.get(r.date) ?? { date: r.date };
    // The category field tells us which series this record belongs to
    entry[(r as any).category] = r.value;
    map.set(r.date, entry);
  }
  return Array.from(map.values()).sort((a, b) => a.date.localeCompare(b.date));
}

export function OrdersChart({ data }: { data: any[] }) {
  const merged = mergeByDate(data);

  return (
    <div className="rounded-xl p-4" style={{ background: "var(--card)" }}>
      <h3 className="text-sm font-semibold mb-1" style={{ color: "var(--muted)" }}>
        SHIPMENTS, ORDERS & INVENTORIES ($M)
      </h3>
      <ResponsiveContainer width="100%" height={340}>
        <LineChart data={merged}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
          <XAxis dataKey="date" tickFormatter={(v) => v.slice(0, 7)} tick={{ fill: "var(--muted)", fontSize: 11 }} interval="preserveStartEnd" />
          <YAxis tick={{ fill: "var(--muted)", fontSize: 11 }} width={55} />
          <Tooltip contentStyle={{ background: "var(--card)", border: "1px solid var(--muted)" }} />
          <Legend wrapperStyle={{ color: "var(--muted)", fontSize: 11 }} />
          <Line type="monotone" dataKey="shipments"    stroke="#3b82f6" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="orders"       stroke="#22c55e" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="inventories"  stroke="#f59e0b" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}