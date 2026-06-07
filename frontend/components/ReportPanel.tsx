import { api } from "@/lib/api";

interface Props {
  reportKey: string;
}

// Server Component — fetches report text server-side
export async function ReportPanel({ reportKey }: Props) {
  let content = "";
  try {
    const report = await api.report(reportKey);
    content = report.content;
  } catch {
    content = "Analysis not yet available. Run the ETL pipeline to generate reports.";
  }

  return (
    <div
      className="rounded-xl p-4 flex flex-col"
      style={{ background: "var(--card)" }}
    >
      <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--muted)" }}>
        AI ANALYSIS
      </h3>
      <div
        className="text-sm leading-relaxed flex-1"
        style={{ color: "var(--text)" }}
      >
        {content.split("\n\n").map((para, i) => (
          <p key={i} className={i > 0 ? "mt-3" : ""}>
            {para}
          </p>
        ))}
      </div>
    </div>
  );
}