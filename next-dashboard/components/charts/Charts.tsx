"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
import { scaleQuantize } from "d3-scale";

import { COLORS, tierColor } from "@/lib/theme";

const axisStyle = { fill: COLORS.textSecondary, fontSize: 11 };
const gridStroke = "rgba(138,139,147,0.16)";
const topoUrl = "https://cdn.jsdelivr.net/npm/datamaps@0.5.10/src/js/data/ind.topo.json";

type ChartProps<T> = {
  data: T[];
  height?: number;
};

function numberTooltip(value: unknown): string {
  return typeof value === "number" ? value.toLocaleString("en-IN", { maximumFractionDigits: 2 }) : String(value);
}

export function MonthlyRevenueChart({
  data,
  height = 280,
}: ChartProps<{ month: string; revenue: number; ma3: number }>) {
  const values = data.flatMap((row) => [row.revenue, row.ma3]);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const yMin = Math.floor((minValue - 250000) / 500000) * 500000;
  const yMax = Math.ceil((maxValue + 250000) / 500000) * 500000;
  const ticks = Array.from({ length: 5 }, (_, index) => yMin + ((yMax - yMin) / 4) * index);

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 18, right: 28, bottom: 10, left: 8 }}>
        <CartesianGrid stroke={gridStroke} vertical={false} />
        <XAxis dataKey="month" tick={axisStyle} axisLine={false} tickLine={false} />
        <YAxis
          tick={axisStyle}
          axisLine={false}
          tickLine={false}
          domain={[yMin, yMax]}
          ticks={ticks}
          tickFormatter={(v) => `₹${Math.round(Number(v) / 100000)}L`}
        />
        <Tooltip formatter={numberTooltip} contentStyle={{ background: COLORS.bgCard, border: `1px solid ${COLORS.borderSubtle}` }} />
        <Line type="monotone" dataKey="revenue" stroke={COLORS.accent} strokeWidth={3} dot={{ r: 3, fill: COLORS.accent, stroke: "#2A1710", strokeWidth: 1 }} name="Revenue" />
        <Line type="monotone" dataKey="ma3" stroke="#B9A28F" strokeDasharray="5 5" strokeWidth={2.2} dot={false} name="3M MA" />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function SimpleBarChart({
  data,
  xKey,
  yKey,
  layout = "vertical",
  color = COLORS.accent,
  height = 280,
}: ChartProps<Record<string, string | number>> & {
  xKey: string;
  yKey: string;
  layout?: "horizontal" | "vertical";
  color?: string;
}) {
  const vertical = layout === "vertical";
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout={vertical ? "vertical" : "horizontal"} margin={{ left: vertical ? 60 : 0 }}>
        <CartesianGrid stroke={gridStroke} horizontal={!vertical} vertical={vertical} />
        <XAxis type={vertical ? "number" : "category"} dataKey={vertical ? undefined : xKey} tick={axisStyle} axisLine={false} tickLine={false} />
        <YAxis type={vertical ? "category" : "number"} dataKey={vertical ? xKey : undefined} tick={axisStyle} axisLine={false} tickLine={false} width={vertical ? 90 : undefined} />
        <Tooltip formatter={numberTooltip} contentStyle={{ background: COLORS.bgCard, border: `1px solid ${COLORS.borderSubtle}` }} />
        <Bar dataKey={yKey} fill={color} radius={[6, 6, 6, 6]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function MoMBarChart({ data }: ChartProps<{ month: string; mom: number }>) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid stroke={gridStroke} vertical={false} />
        <XAxis dataKey="month" tick={axisStyle} axisLine={false} tickLine={false} />
        <YAxis tick={axisStyle} axisLine={false} tickLine={false} tickFormatter={(v) => `${Number(v).toFixed(0)}%`} />
        <Tooltip formatter={(v) => `${Number(v).toFixed(2)}%`} contentStyle={{ background: COLORS.bgCard, border: `1px solid ${COLORS.borderSubtle}` }} />
        <Bar dataKey="mom" radius={[6, 6, 0, 0]}>
          {data.map((entry) => (
            <Cell key={entry.month} fill={entry.mom >= 0 ? COLORS.champion : COLORS.critical} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function DonutChart({
  data,
  nameKey,
  valueKey,
  height = 260,
  colors,
}: ChartProps<Record<string, string | number>> & {
  nameKey: string;
  valueKey: string;
  colors?: string[] | Record<string, string>;
}) {
  const fallbackColors = [COLORS.accent, COLORS.healthy, COLORS.atRisk, COLORS.champion, COLORS.critical, "#9B7CFF"];
  const resolveColor = (entry: Record<string, string | number>, index: number) => {
    const label = String(entry[nameKey]);
    if (Array.isArray(colors)) return colors[index % colors.length];
    if (colors?.[label]) return colors[label];
    const tier = tierColor(label);
    return tier === COLORS.lowPriority ? fallbackColors[index % fallbackColors.length] : tier;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie data={data} dataKey={valueKey} nameKey={nameKey} innerRadius={55} outerRadius={90} paddingAngle={3}>
          {data.map((entry, index) => (
            <Cell key={String(entry[nameKey])} fill={resolveColor(entry, index)} />
          ))}
        </Pie>
        <Tooltip formatter={numberTooltip} contentStyle={{ background: COLORS.bgCard, border: `1px solid ${COLORS.borderSubtle}` }} />
        <Legend wrapperStyle={{ color: COLORS.textSecondary, fontSize: 11 }} />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function MatrixScatter({
  data,
  height = 380,
}: ChartProps<{ category: string; revenueShare: number; weightedRating: number; quadrant: string }>) {
  const medianX = [...data].sort((a, b) => a.revenueShare - b.revenueShare)[Math.floor(data.length / 2)].revenueShare;
  const medianY = [...data].sort((a, b) => a.weightedRating - b.weightedRating)[Math.floor(data.length / 2)].weightedRating;
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ScatterChart>
        <CartesianGrid stroke={gridStroke} />
        <XAxis dataKey="revenueShare" name="Revenue Share" tick={axisStyle} unit="%" />
        <YAxis dataKey="weightedRating" name="Weighted Rating" tick={axisStyle} domain={[4, 4.7]} />
        <Tooltip cursor={{ strokeDasharray: "3 3" }} contentStyle={{ background: COLORS.bgCard, border: `1px solid ${COLORS.borderSubtle}` }} />
        <ReferenceLine x={medianX} stroke={COLORS.textSecondary} strokeDasharray="4 4" />
        <ReferenceLine y={medianY} stroke={COLORS.textSecondary} strokeDasharray="4 4" />
        <Scatter data={data} name="Categories">
          {data.map((entry) => (
            <Cell key={entry.category} fill={tierColor(entry.quadrant)} />
          ))}
        </Scatter>
      </ScatterChart>
    </ResponsiveContainer>
  );
}

export function OpportunityScatter({
  data,
  height = 390,
}: ChartProps<{ City: string; Revenue: number; Opportunity_Score: number; Orders: number; City_Tier: string }>) {
  const width = 720;
  const padLeft = 82;
  const padRight = 46;
  const padTop = 42;
  const padBottom = 62;
  const revenues = data.map((row) => row.Revenue);
  const scores = data.map((row) => row.Opportunity_Score);
  const revenueSpan = Math.max(...revenues) - Math.min(...revenues);
  const scoreSpan = Math.max(...scores) - Math.min(...scores);
  const minRevenue = Math.min(...revenues) - revenueSpan * 0.08;
  const maxRevenue = Math.max(...revenues) + revenueSpan * 0.08;
  const minScore = Math.min(...scores) - scoreSpan * 0.12;
  const maxScore = Math.max(...scores) + scoreSpan * 0.08;
  const medianRevenue = [...revenues].sort((a, b) => a - b)[Math.floor(revenues.length / 2)];
  const medianScore = [...scores].sort((a, b) => a - b)[Math.floor(scores.length / 2)];
  const xScale = (value: number) => padLeft + ((value - minRevenue) / (maxRevenue - minRevenue || 1)) * (width - padLeft - padRight);
  const yScale = (value: number) => height - padBottom - ((value - minScore) / (maxScore - minScore || 1)) * (height - padTop - padBottom);
  const xMedian = xScale(medianRevenue);
  const yMedian = yScale(medianScore);

  return (
    <div className="rounded-xl bg-black/5">
      <svg viewBox={`0 0 ${width} ${height}`} className="h-full w-full">
        <line x1={padLeft} x2={width - padRight} y1={height - padBottom} y2={height - padBottom} stroke="rgba(242,242,240,0.45)" />
        <line x1={padLeft} x2={padLeft} y1={padTop} y2={height - padBottom} stroke="rgba(242,242,240,0.45)" />
        <line x1={xMedian} x2={xMedian} y1={padTop} y2={height - padBottom} stroke="rgba(242,242,240,0.35)" strokeDasharray="5 5" />
        <line x1={padLeft} x2={width - padRight} y1={yMedian} y2={yMedian} stroke="rgba(242,242,240,0.35)" strokeDasharray="5 5" />
        <text x={padLeft + 18} y={padTop + 26} fill={COLORS.untapped} fontSize="15" fontWeight="800">UNTAPPED</text>
        <text x={width - padRight - 78} y={padTop + 26} fill={COLORS.stars} fontSize="15" fontWeight="800">STARS</text>
        <text x={padLeft + 18} y={height - padBottom - 42} fill={COLORS.emerging} fontSize="15" fontWeight="800">EMERGING</text>
        <text x={width - padRight - 130} y={height - padBottom - 42} fill={COLORS.lowPriority} fontSize="15" fontWeight="800">LOW PRIORITY</text>
        {data.map((row) => (
          <circle
            key={row.City}
            cx={xScale(row.Revenue)}
            cy={yScale(row.Opportunity_Score)}
            r={Math.max(4, Math.min(9, row.Orders / 2600))}
            fill={tierColor(row.City_Tier)}
            opacity="0.88"
            stroke="#101118"
            strokeWidth="1.5"
          >
            <title>{`${row.City}: score ${row.Opportunity_Score.toFixed(1)}, revenue ₹${Math.round(row.Revenue / 100000)}L`}</title>
          </circle>
        ))}
        <text x={width / 2} y={height - 18} fill={COLORS.textSecondary} fontSize="12" textAnchor="middle">Current Performance / Revenue</text>
        <text x={25} y={height / 2} fill={COLORS.textSecondary} fontSize="12" textAnchor="middle" transform={`rotate(-90 25 ${height / 2})`}>Market Attractiveness / Opportunity Score</text>
      </svg>
    </div>
  );
}

export function IndiaRevenueMap({
  data,
  height = 420,
  width = 800,
  scaleValue = 900,
  center = [82, 22.5],
}: {
  data: { state: string; revenue: number }[];
  height?: number;
  width?: number;
  scaleValue?: number;
  center?: [number, number];
}) {
  const revenueByState = new Map(data.map((row) => [row.state, row.revenue]));
  const max = Math.max(...data.map((row) => row.revenue));
  const scale = scaleQuantize<string>().domain([0, max]).range(["#FFD4B4", "#FFB789", "#FF9560", "#E66F3B", COLORS.accent]);

  return (
    <ComposableMap
      projection="geoMercator"
      projectionConfig={{ scale: scaleValue, center }}
      width={width}
      height={height}
    >
      <Geographies geography={topoUrl}>
        {({ geographies }: { geographies: { rsmKey: string; properties: { name: string } }[] }) =>
          geographies.map((geo) => {
            const stateName = geo.properties.name as string;
            const revenue = revenueByState.get(stateName) ?? 0;
            return (
              <Geography
                key={geo.rsmKey}
                geography={geo}
                fill={scale(revenue)}
                stroke={COLORS.borderSubtle}
                strokeWidth={0.5}
                style={{
                  default: { outline: "none" },
                  hover: { fill: COLORS.accent, outline: "none" },
                  pressed: { outline: "none" },
                }}
              />
            );
          })
        }
      </Geographies>
    </ComposableMap>
  );
}
