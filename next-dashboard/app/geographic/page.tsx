import { GeographicExplorer, type StateSummary } from "@/components/GeographicExplorer";
import { PageHeader } from "@/components/PageHeader";
import { aggregateBy, getOrders, type OrderRow } from "@/lib/data";

export default function GeographicPage() {
  const orders = getOrders();
  const cities = aggregateBy(orders, "City", "Price (INR)");
  const topCities = cities.slice(0, 8).map((row) => ({ city: row.name, revenue: row.value }));
  const stateSummaries = buildStateSummaries(orders);

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
      <GeographicExplorer stateSummaries={stateSummaries} topCities={topCities} cumulative={cumulative} />
    </>
  );
}

function buildStateSummaries(orders: OrderRow[]): StateSummary[] {
  const stateNames = Array.from(new Set(orders.map((row) => row.State)));
  return stateNames
    .map((state) => {
      const rows = orders.filter((row) => row.State === state);
      const revenue = rows.reduce((sum, row) => sum + row["Price (INR)"], 0);
      const avgRating = rows.reduce((sum, row) => sum + row.Rating, 0) / rows.length;
      return {
        state,
        revenue,
        orders: rows.length,
        avgOrderValue: revenue / rows.length,
        avgRating,
        topCities: rankRows(rows, "City").slice(0, 5),
        topRestaurants: rankRows(rows, "Restaurant Name").slice(0, 5),
        topDishes: rankRows(rows, "Dish Name").slice(0, 5),
        foodSplit: rankRows(rows, "Food Category").slice(0, 5),
        valueSegments: rankRows(rows, "Value_Segment").slice(0, 5),
      };
    })
    .sort((a, b) => b.revenue - a.revenue);
}

function rankRows(rows: OrderRow[], key: keyof OrderRow) {
  const grouped = new Map<string, { name: string; value: number; orders: number }>();
  rows.forEach((row) => {
    const name = String(row[key]);
    const current = grouped.get(name) ?? { name, value: 0, orders: 0 };
    current.value += row["Price (INR)"];
    current.orders += 1;
    grouped.set(name, current);
  });
  return Array.from(grouped.values()).sort((a, b) => b.value - a.value);
}
