"use client";
import { useEffect, useMemo, useRef } from "react";
import * as d3 from "d3";

interface StateData {
  fips: string;   // 2-digit FIPS code, e.g. "06" for California
  value: number;  // manufacturing employment value
}

interface Props {
  data: StateData[];
}

// Discrete tiers (low -> high manufacturing employment) computed via a
// quantile scale — a lightweight "cluster analysis" so regional patterns
// read at a glance instead of blending into a smooth gradient.
//
// Metallic bronze-to-gold gradient: a warm progression from dark bronze
// through copper and brass to bright gold and pale champagne. Every tone is
// warm and light enough to stand out clearly against the cool, dark navy
// dashboard background (avoiding the blending issue of earlier palettes).
const CLUSTER_COLORS = ["#7a4a23", "#a9703f", "#c89b5a", "#e0bc7a", "#f5dca3"];
const CLUSTER_LABELS = ["Lowest", "Low", "Moderate", "High", "Highest"];

export function StateMapChart({ data }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);

  // Quantile breakpoints double as both the map's color scale and the
  // legend's range labels, so they always stay in sync with the data.
  const legend = useMemo(() => {
    if (!data.length) return [];
    const values = data.map((d) => d.value);
    const scale = d3.scaleQuantile<string>().domain(values).range(CLUSTER_COLORS);
    const thresholds = scale.quantiles();
    const fmt = d3.format(",.0f");
    return CLUSTER_COLORS.map((color, i) => {
      const lo = i === 0 ? d3.min(values)! : thresholds[i - 1];
      const hi = i === CLUSTER_COLORS.length - 1 ? d3.max(values)! : thresholds[i];
      return { color, label: CLUSTER_LABELS[i], range: `${fmt(lo)}–${fmt(hi)}` };
    });
  }, [data]);

  useEffect(() => {
    if (!svgRef.current || !data.length) return;

    const width = 700;
    const height = 420;

    // Clear any previous render
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3.select(svgRef.current)
      .attr("viewBox", `0 0 ${width} ${height}`);

    // Albersusa projection: a composite map that puts Alaska and Hawaii
    // in the lower-left corner so all 50 states fit on one map
    const projection = d3.geoAlbersUsa()
      .translate([width / 2, height / 2])
      .scale(900);

    const path = d3.geoPath().projection(projection);

    const values = data.map((d) => d.value);
    const clusterScale = d3.scaleQuantile<string>().domain(values).range(CLUSTER_COLORS);
    const dataMap = new Map(data.map((d) => [d.fips, d.value]));

    // Load US states GeoJSON from a public CDN
    // In production, host this file yourself in /public/
    d3.json("https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json")
      .then((us: any) => {
        const { feature } = require("topojson-client");
        const states = feature(us, us.objects.states);

        svg.append("g")
          .selectAll("path")
          .data(states.features)
          .join("path")
          .attr("d", path as any)
          .attr("fill", (d: any) => {
            const val = dataMap.get(d.id.toString().padStart(2, "0"));
            return val != null ? clusterScale(val) : "#11141c";
          })
          .attr("stroke", "#0f1117")
          .attr("stroke-width", 0.5)
          .append("title")  // native browser tooltip on hover
          .text((d: any) => {
            const val = dataMap.get(d.id.toString().padStart(2, "0"));
            return val != null
              ? `${d.properties.name}: ${val.toLocaleString()} employees`
              : d.properties.name;
          });
      });
  }, [data]);  // re-run whenever data changes

  return (
    <div className="rounded-xl p-4" style={{ background: "var(--card)" }}>
      <h3 className="text-sm font-semibold mb-1" style={{ color: "var(--muted)" }}>
        MANUFACTURING EMPLOYMENT BY STATE
      </h3>
      <p className="text-xs mb-3" style={{ color: "var(--muted)" }}>
        Number of manufacturing employees by state · 2022 · Census County Business Patterns
      </p>
      <svg ref={svgRef} className="w-full" />
      {legend.length > 0 && (
        <div className="flex flex-wrap gap-x-6 gap-y-2 mt-4">
          {legend.map(({ color, label, range }) => (
            <div key={label} className="flex items-center gap-2 text-xs">
              <span className="inline-block w-3.5 h-3.5 rounded-sm shrink-0" style={{ background: color }} />
              <span style={{ color: "var(--text)" }}>{label}</span>
              <span style={{ color: "var(--muted)" }}>({range} employees)</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
