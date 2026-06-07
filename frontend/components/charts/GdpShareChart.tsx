"use client";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";

export function GdpShareChart({ data }: { data: any[] }) {
  // Filter to just the manufacturing GDP line
  const mfgData = data
    .filter((d) => d.line_desc?.toLowerCase().includes("manufacturing"))
    .map((d) => ({ date: d.date, value: d.value }));

  return (
    <div className="rounded-xl p-4" style={{ background: "var(--card)" }}>
      <h3 className="text-sm font-semibold mb-1" style={{ color: "var(--muted)" }}>
        MANUFACTURING VALUE ADDED ($B, QUARTERLY)
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={mfgData}>
          <defs>
            <linearGradient id="gdpGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#22c55e" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
          <XAxis dataKey="date" tickFormatter={(v) => v.slice(0, 7)} tick={{ fill: "var(--muted)", fontSize: 11 }} interval="preserveStartEnd" />
          <YAxis tick={{ fill: "var(--muted)", fontSize: 11 }} width={55} />
          <Tooltip contentStyle={{ background: "var(--card)", border: "1px solid var(--muted)" }} />
          <Area type="monotone" dataKey="value" stroke="#22c55e" fill="url(#gdpGrad)" strokeWidth={2} dot={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}