"use client";  // this component uses browser APIs (events, hover), must be client-side

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from "recharts";
import { MetricPoint } from "@/lib/types";

interface Props {
  data: MetricPoint[];
}

// Custom tooltip shown on hover
function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as MetricPoint;
  return (
    <div
      className="rounded-lg p-3 text-sm"
      style={{ background: "var(--card)", border: "1px solid var(--muted)" }}
    >
      <p className="font-semibold">{label}</p>
      <p>Value: <span style={{ color: "var(--accent)" }}>{d.value.toFixed(2)}</span></p>
      {d.mom_pct != null && (
        <p style={{ color: d.mom_pct >= 0 ? "var(--positive)" : "var(--negative)" }}>
          MoM: {d.mom_pct > 0 ? "+" : ""}{d.mom_pct.toFixed(2)}%
        </p>
      )}
    </div>
  );
}

export function ProductionChart({ data }: Props) {
  return (
    <div
      className="rounded-xl p-4"
      style={{ background: "var(--card)" }}
    >
      <h3 className="text-sm font-semibold mb-1" style={{ color: "var(--muted)" }}>
        INDUSTRIAL PRODUCTION
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
          <XAxis
            dataKey="date"
            tickFormatter={(v) => v.slice(0, 7)}  // "2024-01-01" -> "2024-01"
            tick={{ fill: "var(--muted)", fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={["auto", "auto"]}
            tick={{ fill: "var(--muted)", fontSize: 11 }}
            width={45}
          />
          <Tooltip content={<CustomTooltip />} />
          {/* Reference line at 100 = the 2017 baseline */}
          <ReferenceLine y={100} stroke="var(--muted)" strokeDasharray="4 4" />
          <Line
            type="monotone"
            dataKey="value"
            stroke="var(--accent)"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}