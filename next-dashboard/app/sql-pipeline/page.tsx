import { PageHeader } from "@/components/PageHeader";
import { SqlExplorer } from "@/components/SqlExplorer";
import { getSqlQueries } from "@/lib/data";

export default function SqlPipelinePage() {
  const queries = getSqlQueries();
  return (
    <>
      <PageHeader
        eyebrow="SQL Appendix"
        title="Precomputed SQL Analytics Appendix"
        description="A technical appendix for the 12 SQLite queries and their precomputed JSON outputs. No live database runs in the browser."
      />
      <SqlExplorer queries={queries} />
    </>
  );
}
