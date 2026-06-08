import { api } from "@/lib/api";

export async function SummaryReport() {
  let content = "";
  try {
    const report = await api.report("summary");
    content = report.content;
  } catch {
    content = "Executive summary not yet available.";
  }

  return (
    <div
      className="rounded-xl p-6 w-full"
      style={{ background: "var(--card)", borderTop: "2px solid var(--accent)" }}
    >
      <h2 className="text-lg font-bold mb-4" style={{ color: "var(--text)" }}>
        Executive Summary
      </h2>
      <div className="grid grid-cols-2 gap-6 text-lg leading-relaxed" style={{ color: "var(--text)" }}>
        {content.split("\n\n").map((para, i) => (
          <p key={i}>{para}</p>
        ))}
      </div>
    </div>
  );
}