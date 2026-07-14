import { SectionCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { DonutChart, SimpleBarChart } from "@/components/charts/Charts";
import { foodBreakdown, getOrders, getSqlQueries, segmentBreakdown } from "@/lib/data";

export default function SegmentsPage() {
  const orders = getOrders();
  const segments = segmentBreakdown(orders);
  const food = foodBreakdown(orders);
  const frequency = getSqlQueries().find((query) => query.name === "Restaurant Frequency Tiers")?.rows ?? [];

  return (
    <>
      <PageHeader
        eyebrow="Segments"
        title="Order Value, Food Type, and Partner Volume"
        description="Simple segment cuts come from enriched order columns. Restaurant frequency tiers are pulled from the precomputed SQL result."
      />

      <div className="grid gap-4 xl:grid-cols-3">
        <SectionCard title="Order-Value Revenue Mix" caption="Value_Segment is prepared in Python.">
          <DonutChart
            data={segments as unknown as Record<string, string | number>[]}
            nameKey="segment"
            valueKey="revenue"
            colors={{
              "Budget (<=200)": "#56CCF2",
              "Standard (201-500)": "#FF6B35",
              "Premium (501-1000)": "#F2C94C",
              "Luxury (>1000)": "#9B7CFF",
            }}
          />
        </SectionCard>
        <SectionCard title="Veg vs Non-Veg Revenue" caption="Food Category uses the conservative Python classifier.">
          <DonutChart
            data={food as unknown as Record<string, string | number>[]}
            nameKey="name"
            valueKey="value"
            colors={{
              Veg: "#6FCF97",
              "Non-Veg": "#EB5757",
            }}
          />
        </SectionCard>
        <SectionCard title="Restaurant Frequency Tiers" caption="40/80 split from the Python/SQL pipeline.">
          <SimpleBarChart data={frequency as Record<string, string | number>[]} xKey="Frequency Tier" yKey="Restaurants" layout="horizontal" />
        </SectionCard>
        <section className="xl:col-span-3">
          <SectionCard title="Orders by Value Segment" caption="Revenue and order count per prepared segment.">
            <SimpleBarChart data={segments as unknown as Record<string, string | number>[]} xKey="segment" yKey="orders" layout="horizontal" height={260} />
          </SectionCard>
        </section>
      </div>
    </>
  );
}
