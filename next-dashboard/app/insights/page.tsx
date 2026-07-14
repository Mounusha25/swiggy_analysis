import { KpiCard, SectionCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { MatrixScatter, SimpleBarChart } from "@/components/charts/Charts";
import { formatCurrency, getCategoryQuadrants, getOrders, getRfmSummary, priceRatingCorrelation } from "@/lib/data";

export default function InsightsPage() {
  const orders = getOrders();
  const quadrants = getCategoryQuadrants();
  const rfm = getRfmSummary();
  const correlation = priceRatingCorrelation(orders);

  return (
    <>
      <PageHeader
        eyebrow="Insights"
        title="Menu, RFM, and Pricing Signals"
        description="Menu quadrants are static precomputed results. RFM segment outputs come from the Python extract layer."
      />
      <div className="grid gap-4 xl:grid-cols-[1.4fr_1fr]">
        <SectionCard title="Menu Intelligence Matrix" caption="Revenue share vs weighted rating, colored by precomputed quadrant.">
          <MatrixScatter data={quadrants} />
        </SectionCard>
        <div className="grid gap-4">
          <KpiCard label="Price-Rating Correlation" value={correlation.toFixed(3)} subline="Weak relationship; pricing is not strongly tied to ratings." />
          <SectionCard title="RFM Segment Counts">
            <SimpleBarChart data={rfm as unknown as Record<string, string | number>[]} xKey="RFM_Segment" yKey="Entities" />
          </SectionCard>
        </div>
        <section className="xl:col-span-2">
          <SectionCard title="RFM Revenue by Segment">
            <div className="overflow-hidden rounded-xl border border-[var(--border-subtle)]">
              <table className="w-full text-left text-xs">
                <thead className="bg-[var(--bg-card-hover)] text-[var(--text-secondary)]">
                  <tr>
                    <th className="px-3 py-2">Segment</th>
                    <th className="px-3 py-2">Restaurants</th>
                    <th className="px-3 py-2">Total Revenue</th>
                    <th className="px-3 py-2">Avg RFM Score</th>
                  </tr>
                </thead>
                <tbody>
                  {rfm.map((row) => (
                    <tr key={row.RFM_Segment} className="border-t border-[var(--border-subtle)]">
                      <td className="px-3 py-2">{row.RFM_Segment}</td>
                      <td className="px-3 py-2">{row.Entities}</td>
                      <td className="px-3 py-2">{formatCurrency(row.Total_Revenue)}</td>
                      <td className="px-3 py-2">{row.Avg_RFM_Score.toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </SectionCard>
        </section>
      </div>
    </>
  );
}
