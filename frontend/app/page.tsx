import { api } from "@/lib/api";
import {
  ProductionChart,
  EmploymentChart,
  CapacityGauge,
  OrdersChart,
  WagesChart,
  GdpShareChart,
  StateMapChart,
} from "@/components/charts/DynamicCharts";
import { ReportPanel } from "@/components/ReportPanel";
import { SummaryReport } from "@/components/SummaryReport";
import { MetricCard } from "@/components/ui/MetricCard";
import { Header } from "@/components/ui/Header";
import { Sidebar } from "@/components/ui/Sidebar";

export const dynamic = "force-dynamic";

// This is a Server Component — data fetching happens on the server
export default async function DashboardPage() {
  // Fetch all data in parallel (Promise.all = run simultaneously, not one-by-one)
  const [production, employment, capacity, shipments, orders, inventories, wages, bea, stateEmployment, lastUpdated] =
    await Promise.all([
      api.fred("IPMAN", "2020-01-01"),
      api.fred("MANEMP", "2020-01-01"),
      api.fred("MCUMFN", "2020-01-01"),
      api.census("shipments"),
      api.census("orders"),
      api.census("inventories"),
      api.fred("CES3000000008", "2020-01-01"),
      api.bea("GDPbyIndustry-1"),
      api.stateEmployment(),
      api.lastUpdated(),
    ]);

  // OrdersChart needs all three categories merged by date
  const censusData = [...shipments, ...orders, ...inventories];

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
        <div id="production" className="grid grid-cols-[3fr_2fr] gap-6 mb-6">
          <ProductionChart data={production} />
          <ReportPanel reportKey="chart:production" />
        </div>

        <div id="employment" className="grid grid-cols-[3fr_2fr] gap-6 mb-6">
          <EmploymentChart data={employment} />
          <ReportPanel reportKey="chart:employment" />
        </div>

        <div id="capacity" className="grid grid-cols-[3fr_2fr] gap-6 mb-6">
          <CapacityGauge data={capacity} />
          <ReportPanel reportKey="chart:capacity" />
        </div>

        <div id="orders" className="grid grid-cols-[3fr_2fr] gap-6 mb-6">
          <OrdersChart data={censusData} />
          <ReportPanel reportKey="chart:orders" />
        </div>

        <div id="wages" className="grid grid-cols-[3fr_2fr] gap-6 mb-6">
          <WagesChart data={wages} />
          <ReportPanel reportKey="chart:wages" />
        </div>

        <div id="gdp" className="grid grid-cols-[3fr_2fr] gap-6 mb-6">
          <GdpShareChart data={bea} />
          <ReportPanel reportKey="chart:gdp" />
        </div>

        <div id="map" className="mb-6">
          <StateMapChart data={stateEmployment} />
        </div>

        {/* Full-width executive summary */}
        <SummaryReport />
      </main>
    </div>
  );
}