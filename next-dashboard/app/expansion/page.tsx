import { SectionCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { DonutChart, OpportunityScatter } from "@/components/charts/Charts";
import { formatCurrency, getCityExpansionIndex, getRestaurantHealthScores } from "@/lib/data";

export default function ExpansionPage() {
  const cityIndex = getCityExpansionIndex();
  const health = getRestaurantHealthScores();
  const healthCounts = ["Champion", "Healthy", "At Risk", "Critical"].map((tier) => ({
    tier,
    count: health.filter((row) => row.Health_Tier === tier).length,
  }));
  const topCities = cityIndex.slice(0, 10);
  const topRestaurants = health.slice(0, 5);
  const bottomRestaurants = [...health].sort((a, b) => a.Health_Score - b.Health_Score).slice(0, 5);

  return (
    <>
      <PageHeader
        eyebrow="Expansion Strategy"
        title="Where to Expand and Where to Intervene"
        description="City opportunity and restaurant health scores are read directly from Python-generated CSV extracts."
      />
      <div className="grid gap-4 xl:grid-cols-[1.4fr_1fr]">
        <section className="xl:col-span-2">
          <SectionCard title="Executive Recommendations" caption="Top actions translated from the city opportunity and restaurant health models.">
            <div className="grid gap-3 md:grid-cols-3">
              <RecommendationCard
                action={`Prioritize ${topCities[0].City}`}
                why={`Highest opportunity score at ${topCities[0].Opportunity_Score.toFixed(1)} with ${formatCurrency(topCities[0].Revenue)} current revenue.`}
                impact="Use as the lead expansion market for executive storytelling and sales focus."
              />
              <RecommendationCard
                action="Stabilize at-risk partners"
                why={`${healthCounts.find((row) => row.tier === "At Risk")?.count.toLocaleString("en-IN")} restaurants are tagged At Risk by the Python health score.`}
                impact="Target onboarding, visibility, and menu-quality interventions before pursuing broad acquisition."
              />
              <RecommendationCard
                action="Separate stars from experiments"
                why="The city index splits high-revenue Stars from lower-revenue Untapped/Emerging markets."
                impact="Protect proven markets while testing lower-cost growth plays in selected opportunity cities."
              />
            </div>
          </SectionCard>
        </section>

        <SectionCard title="City Expansion Opportunity Index" caption="Quadrants compare current revenue performance against precomputed opportunity score.">
          <OpportunityScatter data={cityIndex} />
        </SectionCard>
        <SectionCard title="Top 10 Expansion Targets">
          <div className="space-y-2">
            {topCities.map((row, index) => (
              <div key={row.City} className="flex items-center justify-between rounded-xl bg-[var(--bg-card-hover)] px-3 py-2 text-xs">
                <span>{index + 1}. {row.City}</span>
                <span className="text-[var(--accent)]">{row.Opportunity_Score.toFixed(1)}</span>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard
          title="Restaurant Health Tier Mix"
          caption="At Risk is large because most partners are lower-volume local listings relative to national chains, not because every listing is in real distress."
        >
          <DonutChart data={healthCounts as unknown as Record<string, string | number>[]} nameKey="tier" valueKey="count" />
        </SectionCard>
        <SectionCard title="Top and Bottom Restaurant Health Scores">
          <div className="grid gap-4 md:grid-cols-2">
            <RestaurantList title="Top 5" rows={topRestaurants} />
            <RestaurantList title="Bottom 5" rows={bottomRestaurants} />
          </div>
        </SectionCard>
      </div>
    </>
  );
}

function RecommendationCard({ action, why, impact }: { action: string; why: string; impact: string }) {
  return (
    <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card-hover)] p-4">
      <p className="text-sm font-semibold text-[var(--text-primary)]">{action}</p>
      <p className="mt-2 text-xs leading-5 text-[var(--text-secondary)]">
        <span className="font-semibold text-[var(--accent)]">Why: </span>
        {why}
      </p>
      <p className="mt-2 text-xs leading-5 text-[var(--text-secondary)]">
        <span className="font-semibold text-[var(--accent)]">Expected impact: </span>
        {impact}
      </p>
    </div>
  );
}

function RestaurantList({
  title,
  rows,
}: {
  title: string;
  rows: { "Restaurant Name": string; Health_Score: number; Health_Tier: string; Revenue: number }[];
}) {
  return (
    <div>
      <h3 className="mb-2 text-xs uppercase tracking-[0.04em] text-[var(--text-secondary)]">{title}</h3>
      <div className="space-y-2">
        {rows.map((row) => (
          <div key={`${title}-${row["Restaurant Name"]}`} className="rounded-xl bg-[var(--bg-card-hover)] p-3 text-xs">
            <div className="flex items-center justify-between gap-3">
              <span className="truncate">{row["Restaurant Name"]}</span>
              <span className="text-[var(--accent)]">{row.Health_Score.toFixed(1)}</span>
            </div>
            <p className="mt-1 text-[var(--text-secondary)]">
              {row.Health_Tier} · {formatCurrency(row.Revenue)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
