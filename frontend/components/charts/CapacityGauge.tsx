"use client";
import {
  RadialBarChart, RadialBar, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
} from "recharts";
import { MetricPoint } from "@/lib/types";

export function CapacityGauge({ data }: { data: MetricPoint[] }) {
  const latest = data.at(-1);
  const pct = latest?.value ?? 0;

  // RadialBar needs value as a fraction of the max (100)
  const radialData = [{ value: pct, fill: "#3b82f6" }];

  return (
    <div className="rounded-xl p-4" style={{ background: "var(--card)" }}>
      <h3 className="text-sm font-semibold mb-1" style={{ color: "var(--muted)" }}>
        CAPACITY UTILIZATION
      </h3>
      <div className="flex items-start gap-4">
        {/* Gauge on the left */}
        <div className="relative w-32 h-32">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              innerRadius="60%"
              outerRadius="100%"
              data={radialData}
              startAngle={180}
              endAngle={0}
              barSize={12}
            >
              <RadialBar dataKey="value" cornerRadius={4} background={{ fill: "#2a2d3a" }} />
            </RadialBarChart>
          </ResponsiveContainer>
          {/* Center text overlay */}
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xl font-bold">{pct.toFixed(1)}%</span>
          </div>
        </div>
        {/* Trend line on the right */}
        <div className="flex-1">
          <ResponsiveContainer width="100%" height={120}>
            <LineChart data={data.slice(-36)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
              <XAxis dataKey="date" tickFormatter={(v) => v.slice(0, 7)} tick={{ fontSize: 9, fill: "var(--muted)" }} interval="preserveStartEnd" />
              <YAxis domain={[60, 90]} tick={{ fontSize: 9, fill: "var(--muted)" }} width={30} />
              <Tooltip contentStyle={{ background: "var(--card)", fontSize: 11 }} />
              <Line type="monotone" dataKey="value" stroke="#3b82f6" dot={false} strokeWidth={1.5} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}