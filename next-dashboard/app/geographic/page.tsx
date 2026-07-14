import { SectionCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { IndiaRevenueMap, SimpleBarChart } from "@/components/charts/Charts";
import { aggregateBy, formatCurrency, getOrders } from "@/lib/data";

export default function GeographicPage() {
  const orders = getOrders();
  const states = aggregateBy(orders, "State", "Price (INR)");
  const cities = aggregateBy(orders, "City", "Price (INR)");
  const mapData = states.map((row) => ({ state: row.name, revenue: row.value }));
  const topStates = states.slice(0, 8).map((row) => ({ state: row.name, revenue: row.value }));
  const topCities = cities.slice(0, 8).map((row) => ({ city: row.name, revenue: row.value }));
  const totalRevenue = states.reduce((sum, row) => sum + row.value, 0);
  const leadingState = states[0];

  const cumulative = cities.map((row, index) => {
    const total = cities.reduce((sum, item) => sum + item.value, 0);
    const cumulativeRevenue = cities.slice(0, index + 1).reduce((sum, item) => sum + item.value, 0);
    return { rank: index + 1, city: row.name, cumulative: (cumulativeRevenue / total) * 100 };
  });

  return (
    <>
      <PageHeader
        eyebrow="Geography"
        title="Where Revenue Concentrates"
        description="State and city revenue are aggregated from orders_enriched.csv. The India map joins directly on TopoJSON state names."
      />
      <div className="grid gap-4 xl:grid-cols-[1.2fr_1fr]">
        <SectionCard title="India Revenue Choropleth" caption="Real India state boundaries via datamaps TopoJSON.">
          <div className="mb-3 grid gap-3 md:grid-cols-3">
            <MapStat label="Mapped Revenue" value={formatCurrency(totalRevenue)} />
            <MapStat label="States Covered" value={states.length.toLocaleString("en-IN")} />
            <MapStat label="Revenue Leader" value={leadingState.name} helper={formatCurrency(leadingState.value)} />
          </div>
          <div className="relative flex h-[520px] items-center justify-center overflow-hidden rounded-xl border border-[var(--border-subtle)] bg-[radial-gradient(circle_at_50%_45%,rgba(255,107,53,0.12),transparent_58%)]">
            <IndiaRevenueMap data={mapData} width={560} height={500} scaleValue={720} center={[82, 22]} />
            <div className="absolute bottom-4 left-4 max-w-[260px] rounded-xl border border-[var(--border-subtle)] bg-[#101118]/85 p-3 text-xs text-[var(--text-secondary)] shadow-xl backdrop-blur">
              <p className="font-semibold text-[var(--text-primary)]">How to read this map</p>
              <p className="mt-1 leading-5">Each state is colored by total order revenue from `orders_enriched.csv`. Deeper orange means stronger revenue contribution.</p>
              <div className="mt-3 flex items-center gap-2">
                <span>Lower</span>
                <div className="h-2 flex-1 rounded-full bg-[linear-gradient(90deg,#FFD4B4,#FFB789,#FF9560,#E66F3B,#FF6B35)]" />
                <span>Higher</span>
              </div>
            </div>
          </div>
        </SectionCard>
        <div className="grid gap-4">
          <SectionCard title="Top 8 States" caption="Karnataka leads by a wide margin.">
            <SimpleBarChart data={topStates as unknown as Record<string, string | number>[]} xKey="state" yKey="revenue" />
          </SectionCard>
          <SectionCard title="Top 8 Cities" caption="Bengaluru is the strongest city-level market.">
            <SimpleBarChart data={topCities as unknown as Record<string, string | number>[]} xKey="city" yKey="revenue" />
          </SectionCard>
        </div>
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
    </>
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
