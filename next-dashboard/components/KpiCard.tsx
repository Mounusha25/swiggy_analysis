type KpiCardProps = {
  label: string;
  value: string;
  subline?: string;
  tone?: "default" | "danger" | "warning";
  icon?: React.ReactNode;
};

export function KpiCard({ label, value, subline, tone = "default", icon }: KpiCardProps) {
  const sublineColor =
    tone === "danger"
      ? "text-[var(--tier-critical)]"
      : tone === "warning"
        ? "text-[var(--tier-at-risk)]"
        : "text-[var(--text-secondary)]";

  return (
    <div className="rounded-[14px] border border-[var(--border-subtle)] bg-[linear-gradient(180deg,#171821,#101118)] p-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.03),0_16px_30px_rgba(0,0,0,0.28)]">
      <div className="flex items-start gap-3">
        {icon ? <div className="mt-1 text-[var(--accent)] drop-shadow-[0_0_8px_rgba(255,107,53,0.6)]">{icon}</div> : null}
        <div className="min-w-0">
          <p className="text-[10px] font-semibold text-[var(--text-secondary)]">{label}</p>
          <p className="mt-1 text-[21px] font-semibold leading-none text-[var(--text-primary)]">{value}</p>
          {subline ? <p className={`mt-2 text-[10px] ${sublineColor}`}>{subline}</p> : null}
        </div>
      </div>
    </div>
  );
}

export function SectionCard({
  title,
  caption,
  children,
}: {
  title: string;
  caption?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-[15px] border border-[var(--border-subtle)] bg-[linear-gradient(180deg,#171821,#101118)] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.03),0_18px_34px_rgba(0,0,0,0.28)]">
      <div className="mb-3">
        <h2 className="text-[13px] font-black uppercase tracking-tight text-[var(--text-primary)]">{title}</h2>
        {caption ? <p className="mt-1 text-xs text-[var(--text-secondary)]">{caption}</p> : null}
      </div>
      {children}
    </section>
  );
}
