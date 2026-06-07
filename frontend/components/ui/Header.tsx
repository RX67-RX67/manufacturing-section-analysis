interface Props {
    lastUpdated: string | null;
  }
  
  export function Header({ lastUpdated }: Props) {
    const formatted = lastUpdated
      ? new Date(lastUpdated).toLocaleDateString("en-US", {
          month: "short", day: "numeric", year: "numeric",
        })
      : "Never";
  
    return (
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: "var(--text)" }}>
            U.S. Manufacturing Dashboard
          </h1>
          <p className="text-sm" style={{ color: "var(--muted)" }}>
            Powered by FRED · BLS · Census · BEA
          </p>
        </div>
        <p className="text-sm" style={{ color: "var(--muted)" }}>
          Last updated: {formatted}
        </p>
      </div>
    );
  }