"use client";

// next/dynamic with ssr:false is only allowed inside Client Components — this
// wrapper exists so app/page.tsx (a Server Component) can lazy-load the charts
// client-side only. Recharts' ResponsiveContainer needs browser measurement
// APIs (ResizeObserver, getBoundingClientRect) that don't exist during SSR.
import dynamic from "next/dynamic";

export const ProductionChart = dynamic(() => import("./ProductionChart").then((m) => m.ProductionChart), { ssr: false });
export const EmploymentChart = dynamic(() => import("./EmploymentChart").then((m) => m.EmploymentChart), { ssr: false });
export const CapacityGauge = dynamic(() => import("./CapacityGauge").then((m) => m.CapacityGauge), { ssr: false });
export const OrdersChart = dynamic(() => import("./OrdersChart").then((m) => m.OrdersChart), { ssr: false });
export const WagesChart = dynamic(() => import("./WagesChart").then((m) => m.WagesChart), { ssr: false });
export const GdpShareChart = dynamic(() => import("./GdpShareChart").then((m) => m.GdpShareChart), { ssr: false });
