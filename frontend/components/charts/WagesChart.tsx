"use client";
import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";
import { MetricPoint } from "@/lib/types";

export function WagesChart({ data }: { data: MetricPoint[] }) {
  return (
    <div className="rounded-xl p-4" style={{ background: "var(--card)" }}>
      <h3 className="text-sm font-semibold mb-1" style={{ color: "var(--muted)" }}>
        AVG HOURLY EARNINGS — MANUFACTURING (USD)
      </h3>
      <ResponsiveContainer width="100%" height={340}>
        {/* ComposedChart lets you mix bar + line */}
        <ComposedChart data={data.slice(-36)}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
          <XAxis dataKey="date" tickFormatter={(v) => v.slice(0, 7)} tick={{ fill: "var(--muted)", fontSize: 11 }} interval="preserveStartEnd" />
          <YAxis tick={{ fill: "var(--muted)", fontSize: 11 }} width={40} />
          <Tooltip contentStyle={{ background: "var(--card)", border: "1px solid var(--muted)" }} />
          <Bar dataKey="value" fill="#3b82f620" radius={[2, 2, 0, 0]} />
          <Line type="monotone" dataKey="value" stroke="#3b82f6" dot={false} strokeWidth={2} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}