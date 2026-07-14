import { SectionCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { MoMBarChart, MonthlyRevenueChart, SimpleBarChart } from "@/components/charts/Charts";
import { getOrders, monthlyRevenue, quarterlyRevenue } from "@/lib/data";

export default function TrendsPage() {
  const orders = getOrders();
  const monthly = monthlyRevenue(orders);
  const quarterly = quarterlyRevenue(orders);

  return (
    <>
      <PageHeader
        eyebrow="Trends"
        title="Revenue Momentum"
        description="Monthly and quarterly trend views are aggregated from orders_enriched.csv. Forecast scoring remains in Python extracts, not JavaScript."
      />
      <div className="grid gap-4">
        <SectionCard title="Monthly Revenue Trend" caption="Zoomed y-axis highlights movement across the steady monthly revenue band.">
          <MonthlyRevenueChart data={monthly} height={360} />
        </SectionCard>
        <div className="grid gap-4 xl:grid-cols-2">
          <SectionCard title="Month-over-Month Growth" caption="Green above zero, red below zero.">
            <MoMBarChart data={monthly} />
          </SectionCard>
          <SectionCard title="Quarterly Performance Trend" caption="Q3 is partial: July-August only.">
            <SimpleBarChart data={quarterly as unknown as Record<string, string | number>[]} xKey="quarter" yKey="revenue" layout="horizontal" />
          </SectionCard>
        </div>
      </div>
    </>
  );
}
