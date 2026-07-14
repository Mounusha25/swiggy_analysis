export function PageHeader({ title, eyebrow, description }: { title: string; eyebrow: string; description: string }) {
  return (
    <header className="mb-6">
      <p className="text-[11px] uppercase tracking-[0.04em] text-[var(--accent)]">{eyebrow}</p>
      <h1 className="mt-2 text-3xl font-semibold tracking-tight text-[var(--text-primary)]">{title}</h1>
      <p className="mt-2 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">{description}</p>
    </header>
  );
}
