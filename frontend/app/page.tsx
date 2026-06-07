import { api } from "@/lib/api";
import { ProductionChart } from "@/components/charts/ProductionChart";
import { EmploymentChart } from "@/components/charts/EmploymentChart";
import { CapacityGauge } from "@/components/charts/CapacityGauge";
import { OrdersChart } from "@/components/charts/OrdersChart";
import { WagesChart } from "@/components/charts/WagesChart";
import { GdpShareChart } from "@/components/charts/GdpShareChart";
import { ReportPanel } from "@/components/ReportPanel";
import { SummaryReport } from "@/components/SummaryReport";
import { MetricCard } from "@/components/ui/MetricCard";
import { Header } from "@/components/ui/Header";
import { Sidebar } from "@/components/ui/Sidebar";

// This is a Server Component — data fetching happens on the server
export default async function DashboardPage() {
  // Fetch all data in parallel (Promise.all = run simultaneously, not one-by-one)
  const [production, employment, capacity, orders, wages, bea, lastUpdated] =
    await Promise.all([
      api.fred("IPMAN", "2020-01-01"),
      api.fred("MANEMP", "2020-01-01"),
      api.fred("CAPUTLMFG", "2020-01-01"),
      api.census("orders"),
      api.fred("CES3000000008", "2020-01-01"),
      api.bea("T10306"),
      api.lastUpdated(),
    ]);

  // Get the most recent data point for KPI cards
  const latestProd  = production.at(-1);
  const latestEmp   = employment.at(-1);
  const latestCap   = capacity.at(-1);

  return (
    <div className="flex min-h-screen" style={{ background: "var(--bg)" }}>
      <Sidebar />

      <main className="flex-1 p-6">
        <Header lastUpdated={lastUpdated.last_updated} />

        {/* KPI Cards */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <MetricCard
            label="Production Index"
            value={latestProd?.value.toFixed(1) ?? "—"}
            momPct={latestProd?.mom_pct}
          />
          <MetricCard
            label="Capacity Utilization"
            value={latestCap ? `${latestCap.value.toFixed(1)}%` : "—"}
            momPct={latestCap?.mom_pct}
          />
          <MetricCard
            label="Manufacturing Jobs"
            value={latestEmp ? `${(latestEmp.value / 1000).toFixed(1)}M` : "—"}
            momPct={latestEmp?.mom_pct}
          />
        </div>

        {/* Chart + Report pairs */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <ProductionChart data={production} />
          <ReportPanel reportKey="chart:production" />
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <EmploymentChart data={employment} />
          <ReportPanel reportKey="chart:employment" />
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <CapacityGauge data={capacity} />
          <ReportPanel reportKey="chart:capacity" />
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <OrdersChart data={orders} />
          <ReportPanel reportKey="chart:orders" />
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <WagesChart data={wages} />
          <ReportPanel reportKey="chart:wages" />
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <GdpShareChart data={bea} />
          <ReportPanel reportKey="chart:gdp" />
        </div>

        {/* Full-width executive summary */}
        <SummaryReport />
      </main>
    </div>
  );
}