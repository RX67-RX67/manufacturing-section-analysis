"use client";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { MetricPoint } from "@/lib/types";

export function EmploymentChart({ data }: { data: MetricPoint[] }) {
  return (
    <div className="rounded-xl p-4" style={{ background: "var(--card)" }}>
      <h3 className="text-sm font-semibold mb-1" style={{ color: "var(--muted)" }}>
        MANUFACTURING EMPLOYMENT (thousands)
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data}>
          <defs>
            {/* Gradient fill under the area */}
            <linearGradient id="empGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
          <XAxis
            dataKey="date"
            tickFormatter={(v) => v.slice(0, 7)}
            tick={{ fill: "var(--muted)", fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={["auto", "auto"]}
            tick={{ fill: "var(--muted)", fontSize: 11 }}
            width={55}
          />
          <Tooltip
            contentStyle={{ background: "var(--card)", border: "1px solid var(--muted)" }}
            labelStyle={{ color: "var(--text)" }}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#3b82f6"
            fill="url(#empGrad)"
            strokeWidth={2}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}