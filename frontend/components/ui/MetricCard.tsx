interface Props {
    label: string;
    value: string;
    momPct?: number | null;
  }
  
  export function MetricCard({ label, value, momPct }: Props) {
    const isPositive = momPct != null && momPct > 0;
    const isNegative = momPct != null && momPct < 0;
  
    return (
      <div
        className="rounded-xl p-4"
        style={{ background: "var(--card)" }}
      >
        <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--muted)" }}>
          {label}
        </p>
        <p className="text-3xl font-bold mt-1" style={{ color: "var(--text)" }}>
          {value}
        </p>
        {momPct != null && (
          <p
            className="text-sm mt-1"
            style={{ color: isPositive ? "var(--positive)" : isNegative ? "var(--negative)" : "var(--muted)" }}
          >
            {momPct > 0 ? "▲" : "▼"} {Math.abs(momPct).toFixed(2)}% MoM
          </p>
        )}
      </div>
    );
  }