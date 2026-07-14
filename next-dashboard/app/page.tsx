import { KpiCard, SectionCard } from "@/components/KpiCard";
import { IndiaRevenueMap } from "@/components/charts/Charts";
import {
  IconBulb,
  IconChartHistogram,
  IconCurrencyRupee,
  IconDatabase,
  IconMapPin,
  IconReportAnalytics,
  IconShoppingCart,
  IconTargetArrow,
  IconToolsKitchen2,
  IconUsersGroup,
} from "@tabler/icons-react";
import {
  aggregateBy,
  formatCurrency,
  getCityExpansionIndex,
  getOrders,
  getRestaurantHealthScores,
  monthlyRevenue,
} from "@/lib/data";
import { COLORS, tierColor } from "@/lib/theme";

export default function OverviewPage() {
  const orders = getOrders();
  const health = getRestaurantHealthScores();
  const cityIndex = getCityExpansionIndex();
  const monthly = monthlyRevenue(orders);
  const totalRevenue = orders.reduce((sum, row) => sum + row["Price (INR)"], 0);
  const atRisk = health.filter((row) => row.Health_Tier === "At Risk").length;
  const stars = cityIndex.filter((row) => row.City_Tier === "Stars").length;
  const avgOrderValue = Math.round(totalRevenue / orders.length);
  const states = aggregateBy(orders, "State", "Price (INR)").map((row) => ({ state: row.name, revenue: row.value }));
  const healthCounts = ["Champion", "Healthy", "At Risk", "Critical"].map((tier) => ({
    tier,
    count: health.filter((row) => row.Health_Tier === tier).length,
  }));

  return (
    <div className="relative overflow-hidden rounded-[30px] border border-[#2A2B33] bg-[#0D0E13]/95 p-4 shadow-[0_28px_80px_rgba(0,0,0,0.55)]">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_80%_0%,rgba(255,107,53,0.18),transparent_34%),radial-gradient(circle_at_0%_100%,rgba(111,207,151,0.08),transparent_32%)]" />
      <div className="relative">
        <TopRibbon />

        <div className="mb-3 grid gap-3 md:grid-cols-5">
          <KpiCard icon={<IconCurrencyRupee size={24} />} label="Total Revenue" value={formatCurrency(totalRevenue)} subline="+ from 197K orders" />
          <KpiCard icon={<IconShoppingCart size={24} />} label="Total Orders" value={orders.length.toLocaleString("en-IN")} subline="Jan-Aug 2025" />
          <KpiCard icon={<IconReportAnalytics size={24} />} label="Avg Order Value" value={`₹${avgOrderValue}`} subline="basket size" />
          <KpiCard icon={<IconMapPin size={24} />} label="Cities Covered" value={cityIndex.length.toLocaleString("en-IN")} subline={`${stars} tagged Stars`} tone="warning" />
          <KpiCard icon={<IconUsersGroup size={24} />} label="Restaurants" value={health.length.toLocaleString("en-IN")} subline={`${atRisk} flagged at risk`} tone="danger" />
        </div>

        <div className="grid gap-3 xl:grid-cols-[1.05fr_0.95fr_1.05fr]">
          <SectionCard title="Revenue Over Time">
            <RevenueOverTimeMini data={monthly} />
          </SectionCard>
          <SectionCard title="Revenue by State">
            <div className="relative h-[220px] overflow-hidden rounded-xl bg-[radial-gradient(circle_at_50%_52%,rgba(255,107,53,0.16),transparent_62%)]">
              <div className="absolute left-1/2 top-1 h-[200px] w-[260px] -translate-x-1/2">
                <IndiaRevenueMap data={states} width={260} height={200} scaleValue={330} center={[82, 22]} />
              </div>
              <div className="absolute bottom-5 right-6 flex items-end gap-2 text-[10px] text-[var(--text-secondary)]">
                <span>Low</span>
                <div className="h-16 w-3 rounded-full bg-[linear-gradient(180deg,#FF6B35,#FF9A62,#FFD4B4)]" />
                <span>High</span>
              </div>
            </div>
          </SectionCard>
          <SectionCard title="Menu Intelligence Matrix">
            <MiniMenuMatrix />
          </SectionCard>
        </div>

        <div className="mt-3 grid gap-3 xl:grid-cols-[1.05fr_0.95fr_1.05fr]">
          <SectionCard title="City Expansion Opportunity Index">
            <MiniOpportunityIndex data={cityIndex} />
          </SectionCard>
          <SectionCard title="Restaurant Health Score">
            <HealthScoreCard counts={healthCounts} />
          </SectionCard>
          <SectionCard title="Demand Heatmap (Time of Day)" caption="Modeled scenario; not observed order-hour data.">
            <DemandHeatmap />
          </SectionCard>
        </div>
      </div>
    </div>
  );
}

function TopRibbon() {
  const items = [
    { label: "Analytical Frameworks", icon: IconTargetArrow },
    { label: "Predictive Insights", icon: IconChartHistogram },
    { label: "SQL Pipeline", icon: IconDatabase },
    { label: "Interactive Dashboard", icon: IconReportAnalytics },
    { label: "Actionable Intelligence", icon: IconBulb },
  ];
  return (
    <div className="mx-auto mb-3 flex max-w-4xl items-center justify-center gap-5 rounded-b-[26px] rounded-t-xl border border-[#3A2A21] bg-[linear-gradient(180deg,#2A1C16,#15161D)] px-5 py-3 shadow-[0_14px_35px_rgba(0,0,0,0.35)]">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <div key={item.label} className="flex items-center gap-2 text-[11px] font-semibold text-[var(--text-primary)]">
            <Icon size={24} className="text-[var(--accent)] drop-shadow-[0_0_8px_rgba(255,107,53,0.7)]" />
            <span className="max-w-[100px] leading-tight">{item.label}</span>
          </div>
        );
      })}
    </div>
  );
}

function MiniMenuMatrix() {
  const cells = [
    { title: "Cash Cows", subtitle: "High Revenue\nLower Rating", color: COLORS.cashCows, icon: "♜", bg: "linear-gradient(135deg, rgba(242,201,76,0.28), rgba(21,22,29,0.62))" },
    { title: "Stars", subtitle: "High Revenue\nHigh Rating", color: COLORS.stars, icon: "★", bg: "linear-gradient(135deg, rgba(111,207,151,0.28), rgba(21,22,29,0.62))" },
    { title: "Review Needed", subtitle: "Low Revenue\nLower Rating", color: COLORS.reviewNeeded, icon: "⚠", bg: "linear-gradient(135deg, rgba(235,87,87,0.28), rgba(21,22,29,0.62))" },
    { title: "Hidden Gems", subtitle: "Low Revenue\nHigh Rating", color: COLORS.hiddenGems, icon: "◆", bg: "linear-gradient(135deg, rgba(86,204,242,0.28), rgba(21,22,29,0.62))" },
  ];
  return (
    <div className="relative h-[220px] rounded-xl border border-[var(--border-subtle)] bg-[radial-gradient(circle_at_center,rgba(255,107,53,0.10),transparent_65%)] px-8 pb-9 pt-5">
      <div className="grid h-full grid-cols-2 overflow-hidden rounded-lg border border-[#64452c] bg-[#181820] shadow-[0_0_28px_rgba(255,107,53,0.10)]">
        {cells.map((cell) => (
          <div
            key={cell.title}
            className="flex flex-col items-center justify-center border border-black/25 text-center"
            style={{ background: cell.bg }}
          >
            <div className="text-[22px] drop-shadow-[0_0_8px_rgba(255,255,255,0.20)]" style={{ color: cell.color }}>{cell.icon}</div>
            <p className="mt-1 text-[12px] font-black uppercase leading-none" style={{ color: cell.color }}>{cell.title}</p>
            <p className="mt-2 whitespace-pre-line text-[10px] font-semibold leading-4 text-[var(--text-primary)]">{cell.subtitle}</p>
          </div>
        ))}
      </div>
      <p className="absolute bottom-3 left-1/2 w-full -translate-x-1/2 text-center text-[10px] text-[var(--text-secondary)]">Lower Rating → Higher Rating</p>
      <p className="absolute left-3 top-1/2 -translate-y-1/2 -rotate-90 text-[10px] text-[var(--text-secondary)]">Revenue Share</p>
    </div>
  );
}

function RevenueOverTimeMini({ data }: { data: { month: string; revenue: number; ma3: number }[] }) {
  const width = 310;
  const height = 178;
  const padLeft = 36;
  const padRight = 16;
  const padTop = 18;
  const padBottom = 26;
  const min = Math.floor((Math.min(...data.map((row) => row.revenue)) - 250000) / 500000) * 500000;
  const max = Math.ceil((Math.max(...data.map((row) => row.revenue)) + 250000) / 500000) * 500000;
  const ticks = [max, max - (max - min) / 3, max - ((max - min) * 2) / 3, min];
  const points = data.map((row, index) => {
    const x = padLeft + (index / (data.length - 1)) * (width - padLeft - padRight);
    const y = height - padBottom - ((row.revenue - min) / (max - min)) * (height - padTop - padBottom);
    return { x, y, label: row.month.slice(5), value: row.revenue };
  });
  const maPoints = data.map((row, index) => {
    const x = padLeft + (index / (data.length - 1)) * (width - padLeft - padRight);
    const y = height - padBottom - ((row.ma3 - min) / (max - min)) * (height - padTop - padBottom);
    return `${x},${y}`;
  }).join(" ");
  const line = points.map((point) => `${point.x},${point.y}`).join(" ");

  return (
    <div className="h-[220px] rounded-xl bg-[linear-gradient(180deg,rgba(255,107,53,0.04),transparent)] px-3 pt-1">
      <svg viewBox={`0 0 ${width} ${height}`} className="h-[178px] w-full overflow-visible">
        {ticks.map((value) => {
          const y = height - padBottom - ((value - min) / (max - min)) * (height - padTop - padBottom);
          return (
            <g key={value}>
              <line x1={padLeft} x2={width - padRight} y1={y} y2={y} stroke="rgba(138,139,147,0.14)" />
              <text x={padLeft - 7} y={y + 3} textAnchor="end" fill={COLORS.textSecondary} fontSize="9">
                ₹{Math.round(value / 100000)}L
              </text>
            </g>
          );
        })}
        <polyline points={maPoints} fill="none" stroke="#B9A28F" strokeWidth="2" strokeDasharray="5 5" opacity="0.8" />
        <polyline points={line} fill="none" stroke={COLORS.accent} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" filter="drop-shadow(0 0 7px rgba(255,107,53,0.7))" />
        {points.map((point) => (
          <circle key={point.label} cx={point.x} cy={point.y} r="3.5" fill={COLORS.accent} stroke="#2A1710" strokeWidth="1.5" />
        ))}
        {points.filter((_, index) => index % 2 === 1 || index === data.length - 1).map((point) => (
          <text key={point.label} x={point.x} y={height - 4} textAnchor="middle" fill={COLORS.textSecondary} fontSize="10">
            {point.label}
          </text>
        ))}
      </svg>
      <div className="flex justify-center gap-6 text-[10px] text-[var(--text-secondary)]">
        <span><span className="mr-1 inline-block h-0.5 w-5 bg-[var(--accent)] align-middle" />Revenue</span>
        <span><span className="mr-1 inline-block h-0.5 w-5 border-t border-dashed border-[#B9A28F] align-middle" />3-Month Moving Average</span>
      </div>
    </div>
  );
}

function MiniOpportunityIndex({
  data,
}: {
  data: { City: string; Revenue: number; Opportunity_Score: number; Orders: number; City_Tier: string }[];
}) {
  const width = 328;
  const height = 212;
  const padLeft = 44;
  const padRight = 24;
  const padTop = 24;
  const padBottom = 38;
  const selected = data.slice(0, 22);
  const revenues = selected.map((row) => row.Revenue);
  const scores = selected.map((row) => row.Opportunity_Score);
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
    <div className="relative h-[220px] rounded-xl bg-black/5">
      <svg viewBox={`0 0 ${width} ${height}`} className="h-full w-full">
        <line x1={padLeft} x2={width - padRight} y1={height - padBottom} y2={height - padBottom} stroke="rgba(242,242,240,0.45)" />
        <line x1={padLeft} x2={padLeft} y1={padTop} y2={height - padBottom} stroke="rgba(242,242,240,0.45)" />
        <line x1={xMedian} x2={xMedian} y1={padTop} y2={height - padBottom} stroke="rgba(242,242,240,0.35)" strokeDasharray="4 4" />
        <line x1={padLeft} x2={width - padRight} y1={yMedian} y2={yMedian} stroke="rgba(242,242,240,0.35)" strokeDasharray="4 4" />
        <text x={padLeft + 8} y={padTop + 20} fill={COLORS.untapped} fontSize="11" fontWeight="700">UNTAPPED</text>
        <text x={width - padRight - 58} y={padTop + 20} fill={COLORS.stars} fontSize="11" fontWeight="700">STARS</text>
        <text x={padLeft + 8} y={height - padBottom - 32} fill={COLORS.emerging} fontSize="11" fontWeight="700">EMERGING</text>
        <text x={width - padRight - 96} y={height - padBottom - 32} fill={COLORS.lowPriority} fontSize="11" fontWeight="700">LOW PRIORITY</text>
        {selected.map((row) => (
          <circle
            key={row.City}
            cx={xScale(row.Revenue)}
            cy={yScale(row.Opportunity_Score)}
            r={Math.max(3, Math.min(6, row.Orders / 3500))}
            fill={tierColor(row.City_Tier)}
            opacity="0.9"
            stroke="#101118"
            strokeWidth="1"
          />
        ))}
        <text x={width / 2} y={height - 8} fill={COLORS.textSecondary} fontSize="10" textAnchor="middle">Current Performance</text>
        <text x={14} y={height / 2} fill={COLORS.textSecondary} fontSize="10" textAnchor="middle" transform={`rotate(-90 14 ${height / 2})`}>Market Attractiveness</text>
      </svg>
    </div>
  );
}

function HealthScoreCard({ counts }: { counts: { tier: string; count: number }[] }) {
  const total = counts.reduce((sum, row) => sum + row.count, 0);
  const critical = counts.find((row) => row.tier === "Critical")?.count ?? 0;
  return (
    <div className="grid h-[220px] grid-cols-[0.9fr_1fr] items-center gap-4">
      <div className="relative mx-auto flex h-32 w-32 items-center justify-center rounded-full" style={{ background: "conic-gradient(var(--tier-champion) 0 1%, var(--tier-healthy) 1% 2%, var(--tier-at-risk) 2% 92%, var(--tier-critical) 92% 100%)" }}>
        <div className="flex h-20 w-20 flex-col items-center justify-center rounded-full bg-[var(--bg-card)] text-center shadow-inner">
          <IconToolsKitchen2 size={22} className="text-[var(--text-primary)]" />
          <p className="text-xl font-bold">{critical}</p>
          <p className="text-[10px] text-[var(--text-secondary)]">critical</p>
        </div>
      </div>
      <div className="space-y-2">
        {counts.map((row) => (
          <div key={row.tier} className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-2 text-[var(--text-secondary)]">
              <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: tierColor(row.tier) }} />
              {row.tier}
            </span>
            <span className="text-[var(--text-primary)]">{Math.round((row.count / total) * 100)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function DemandHeatmap() {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const hours = Array.from({ length: 14 }, (_, index) => index);
  return (
    <div className="relative h-[220px] rounded-xl bg-[radial-gradient(circle_at_55%_50%,rgba(255,107,53,0.16),transparent_60%)] p-1">
      <div className="grid grid-cols-[34px_1fr_22px] gap-2">
        <div className="grid grid-rows-7 gap-1 pt-1">
          {days.map((day) => <span key={day} className="text-[10px] text-[var(--text-secondary)]">{day}</span>)}
        </div>
        <div className="grid grid-cols-14 gap-1">
          {days.flatMap((day, dayIndex) =>
            hours.map((hour) => {
              const lunch = Math.exp(-((hour - 5) ** 2) / 7);
              const dinner = Math.exp(-((hour - 10) ** 2) / 8);
              const weekend = dayIndex >= 5 ? 0.22 : 0;
              const stripe = ((hour + dayIndex) % 4) * 0.035;
              const intensity = Math.min(1, 0.16 + lunch * 0.38 + dinner * 0.42 + weekend + stripe);
              const lightness = 78 - intensity * 30;
              return (
                <div
                  key={`${day}-${hour}`}
                  className="aspect-square rounded-[4px] border border-black/20 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]"
                  style={{
                    background: `linear-gradient(135deg, hsl(25 100% ${lightness + 4}%), hsl(16 100% ${lightness}%))`,
                    boxShadow: intensity > 0.72 ? "0 0 10px rgba(255,107,53,0.45)" : undefined,
                  }}
                />
              );
            }),
          )}
        </div>
        <div className="flex flex-col items-center justify-between text-[9px] text-[var(--text-secondary)]">
          <span>High</span>
          <div className="h-28 w-3 rounded-full bg-[linear-gradient(180deg,#FF6B35,#FF9A62,#FFD4B4)]" />
          <span>Low</span>
        </div>
      </div>
      <div className="ml-10 mt-3 flex justify-between text-[10px] text-[var(--text-secondary)]">
        <span>6 AM</span>
        <span>12 PM</span>
        <span>6 PM</span>
        <span>12 AM</span>
      </div>
    </div>
  );
}
