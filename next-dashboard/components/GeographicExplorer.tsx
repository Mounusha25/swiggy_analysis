"use client";

import { useMemo, useState } from "react";

import { SectionCard } from "@/components/KpiCard";
import { IndiaRevenueMap, SimpleBarChart } from "@/components/charts/Charts";

type RankedMetric = {
  name: string;
  value: number;
  orders?: number;
};

export type StateSummary = {
  state: string;
  revenue: number;
  orders: number;
  avgOrderValue: number;
  avgRating: number;
  topCities: RankedMetric[];
  topRestaurants: RankedMetric[];
  topDishes: RankedMetric[];
  foodSplit: RankedMetric[];
  valueSegments: RankedMetric[];
};

type ParetoRow = {
  rank: number;
  city: string;
  cumulative: number;
};

type Props = {
  stateSummaries: StateSummary[];
  topCities: { city: string; revenue: number }[];
  cumulative: ParetoRow[];
};

type MetricKey = "revenue" | "orders" | "avgOrderValue" | "avgRating";
type DrilldownKey = "topCities" | "topRestaurants" | "topDishes" | "foodSplit" | "valueSegments";

const metricOptions: { key: MetricKey; label: string; valueLabel: string; format: (value: number) => string }[] = [
  { key: "revenue", label: "Revenue", valueLabel: "revenue", format: formatCurrency },
  { key: "orders", label: "Orders", valueLabel: "orders", format: (value) => Math.round(value).toLocaleString("en-IN") },
  { key: "avgOrderValue", label: "AOV", valueLabel: "avg order value", format: formatCurrency },
  { key: "avgRating", label: "Rating", valueLabel: "avg rating", format: (value) => value.toFixed(2) },
];

const drilldownTabs: { key: DrilldownKey; label: string }[] = [
  { key: "topCities", label: "Cities" },
  { key: "topRestaurants", label: "Restaurants" },
  { key: "topDishes", label: "Dishes" },
  { key: "foodSplit", label: "Food Mix" },
  { key: "valueSegments", label: "Value Mix" },
];

function formatCurrency(value: number): string {
  if (value >= 10_000_000) return `₹${(value / 10_000_000).toFixed(2)} Cr`;
  if (value >= 100_000) return `₹${(value / 100_000).toFixed(1)} L`;
  return `₹${Math.round(value).toLocaleString("en-IN")}`;
}

export function GeographicExplorer({ stateSummaries, topCities, cumulative }: Props) {
  const sortedStates = useMemo(
    () => [...stateSummaries].sort((a, b) => b.revenue - a.revenue),
    [stateSummaries],
  );
  const [selectedState, setSelectedState] = useState(sortedStates[0]?.state ?? "");
  const [selectedMetric, setSelectedMetric] = useState<MetricKey>("revenue");
  const [selectedDrilldown, setSelectedDrilldown] = useState<DrilldownKey>("topCities");
  const selected = sortedStates.find((row) => row.state === selectedState) ?? sortedStates[0];
  const totalRevenue = sortedStates.reduce((sum, row) => sum + row.revenue, 0);
  const metricConfig = metricOptions.find((option) => option.key === selectedMetric) ?? metricOptions[0];
  const leaderForMetric = [...sortedStates].sort((a, b) => b[selectedMetric] - a[selectedMetric])[0];
  const metricAverage = sortedStates.reduce((sum, row) => sum + row[selectedMetric], 0) / sortedStates.length;
  const selectedMetricValue = selected[selectedMetric];
  const mapData = sortedStates.map((row) => ({ state: row.state, revenue: row[selectedMetric] }));
  const topStates = sortedStates.slice(0, 8).map((row) => ({ state: row.state, revenue: row.revenue }));
  const drilldownRows = selected[selectedDrilldown];

  return (
    <div className="grid gap-4 xl:grid-cols-[1.2fr_1fr]">
      <SectionCard title="Interactive India State Explorer" caption="Change metric, hover for values, click a state for drilldown details." tooltip="The map color can represent revenue, orders, AOV, or rating. Clicking a state updates all drilldown cards.">
        <div className="mb-3 grid gap-3 md:grid-cols-3">
          <MapStat label="Mapped Revenue" value={formatCurrency(totalRevenue)} />
          <MapStat label="States Covered" value={sortedStates.length.toLocaleString("en-IN")} />
          <MapStat label="Selected State" value={selected.state} helper={formatCurrency(selected.revenue)} />
        </div>
        <div className="mb-3 flex flex-wrap gap-2">
          {metricOptions.map((option) => (
            <button
              key={option.key}
              type="button"
              onClick={() => setSelectedMetric(option.key)}
              className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
                selectedMetric === option.key
                  ? "border-[var(--accent)] bg-[var(--accent)] text-black"
                  : "border-[var(--border-subtle)] bg-[var(--bg-card-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              }`}
            >
              Color by {option.label}
            </button>
          ))}
        </div>
        <div className="relative flex h-[520px] items-center justify-center overflow-hidden rounded-xl border border-[var(--border-subtle)] bg-[radial-gradient(circle_at_50%_45%,rgba(255,107,53,0.12),transparent_58%)]">
          <IndiaRevenueMap
            data={mapData}
            width={560}
            height={500}
            scaleValue={720}
            center={[82, 22]}
            selectedState={selected.state}
            onStateClick={(state) => {
              if (sortedStates.some((row) => row.state === state)) setSelectedState(state);
            }}
          />
          <div className="absolute bottom-4 left-4 max-w-[280px] rounded-xl border border-[var(--border-subtle)] bg-[#101118]/85 p-3 text-xs text-[var(--text-secondary)] shadow-xl backdrop-blur">
            <p className="font-semibold text-[var(--text-primary)]">How to use this map</p>
            <p className="mt-1 leading-5">Switch the map metric, hover for values, or click a state. The right panel updates instantly.</p>
            <div className="mt-3 flex items-center gap-2">
              <span>Lower</span>
              <div className="h-2 flex-1 rounded-full bg-[linear-gradient(90deg,#FFD4B4,#FFB789,#FF9560,#E66F3B,#FF6B35)]" />
              <span>Higher</span>
            </div>
          </div>
        </div>
      </SectionCard>

      <div className="grid gap-4">
        <SectionCard title={`${selected.state} Snapshot`} caption="State drilldown from enriched order extracts." tooltip="Metrics are computed from orders_enriched.csv rows filtered to the selected state.">
          <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-1">
            <MapStat label="Revenue" value={formatCurrency(selected.revenue)} />
            <MapStat label="Orders" value={selected.orders.toLocaleString("en-IN")} helper={`AOV ${formatCurrency(selected.avgOrderValue)}`} />
            <MapStat label="Avg Rating" value={selected.avgRating.toFixed(2)} />
            <MapStat
              label={`${metricConfig.label} vs Avg`}
              value={metricConfig.format(selectedMetricValue)}
              helper={`All-state avg ${metricConfig.format(metricAverage)}`}
            />
          </div>
        </SectionCard>
        <SectionCard title="Quick State Picker" caption={`Leader by ${metricConfig.label}: ${leaderForMetric.state}`} tooltip="These buttons jump to the top states by revenue for fast comparison.">
          <div className="flex flex-wrap gap-2">
            {sortedStates.slice(0, 10).map((row) => (
              <button
                key={row.state}
                type="button"
                onClick={() => setSelectedState(row.state)}
                className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
                  selected.state === row.state
                    ? "border-[var(--accent)] bg-[var(--accent)] text-black"
                    : "border-[var(--border-subtle)] bg-[var(--bg-card-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                }`}
              >
                {row.state}
              </button>
            ))}
          </div>
        </SectionCard>
        <SectionCard title={`${selected.state} Drilldown`} caption="Switch categories to inspect the selected state." tooltip="Each tab ranks the selected state's cities, restaurants, dishes, food categories, or value segments by revenue.">
          <div className="mb-3 flex flex-wrap gap-2">
            {drilldownTabs.map((tab) => (
              <button
                key={tab.key}
                type="button"
                onClick={() => setSelectedDrilldown(tab.key)}
                className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
                  selectedDrilldown === tab.key
                    ? "border-[var(--accent)] bg-[var(--accent)] text-black"
                    : "border-[var(--border-subtle)] bg-[var(--bg-card-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
          <RankList rows={drilldownRows} />
        </SectionCard>
      </div>

      <section className="xl:col-span-2">
        <div className="grid gap-4 xl:grid-cols-2">
          <SectionCard title="Top 8 States" caption="Overall revenue leaders across the dataset.">
            <SimpleBarChart data={topStates as unknown as Record<string, string | number>[]} xKey="state" yKey="revenue" />
          </SectionCard>
          <SectionCard title="Top 8 Cities" caption="Overall city-level revenue leaders.">
            <SimpleBarChart data={topCities as unknown as Record<string, string | number>[]} xKey="city" yKey="revenue" />
          </SectionCard>
        </div>
      </section>

      <section className="xl:col-span-2">
        <SectionCard title="City Pareto Snapshot" caption="Cumulative revenue contribution by city, sorted descending.">
          <div className="grid gap-2 md:grid-cols-4">
            {cumulative.slice(0, 8).map((row) => (
              <div key={row.city} className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card-hover)] p-3">
                <p className="text-xs text-[var(--text-secondary)]">#{row.rank} {row.city}</p>
                <p className="mt-1 text-lg font-medium">{row.cumulative.toFixed(1)}%</p>
              </div>
            ))}
          </div>
        </SectionCard>
      </section>
    </div>
  );
}

function RankList({ rows }: { rows: RankedMetric[] }) {
  return (
    <div className="space-y-2">
      {rows.slice(0, 5).map((row, index) => (
        <div
          key={`${row.name}-${index}`}
          className="flex items-center justify-between gap-3 rounded-xl bg-[var(--bg-card-hover)] px-3 py-2 text-xs"
        >
          <span className="truncate">{index + 1}. {row.name}</span>
          <span className="shrink-0 text-[var(--accent)]">{formatCurrency(row.value)}</span>
        </div>
      ))}
    </div>
  );
}

function MapStat({ label, value, helper }: { label: string; value: string; helper?: string }) {
  return (
    <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card-hover)] p-3">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-[var(--text-secondary)]">{label}</p>
      <p className="mt-1 text-lg font-semibold text-[var(--text-primary)]">{value}</p>
      {helper ? <p className="mt-1 text-xs text-[var(--text-secondary)]">{helper}</p> : null}
    </div>
  );
}
