"use client";
import { useEffect, useRef } from "react";
import * as d3 from "d3";

interface StateData {
  fips: string;   // 2-digit FIPS code, e.g. "06" for California
  value: number;  // manufacturing employment value
}

interface Props {
  data: StateData[];
}

export function StateMapChart({ data }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);

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

    // Color scale: low values = dark, high values = blue
    const colorScale = d3.scaleSequential(d3.interpolateBlues)
      .domain([0, d3.max(data, (d) => d.value) ?? 1]);

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
            return val != null ? colorScale(val) : "#2a2d3a";
          })
          .attr("stroke", "#0f1117")
          .attr("stroke-width", 0.5)
          .append("title")  // native browser tooltip on hover
          .text((d: any) => {
            const val = dataMap.get(d.id.toString().padStart(2, "0"));
            return val != null ? `${d.properties.name}: ${val.toLocaleString()}` : d.properties.name;
          });
      });
  }, [data]);  // re-run whenever data changes

  return (
    <div className="rounded-xl p-4" style={{ background: "var(--card)" }}>
      <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--muted)" }}>
        MANUFACTURING EMPLOYMENT BY STATE
      </h3>
      <svg ref={svgRef} className="w-full" />
    </div>
  );
}