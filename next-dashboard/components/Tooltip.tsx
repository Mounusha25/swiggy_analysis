export function Tooltip({ content }: { content: string }) {
  return (
    <span className="group relative inline-flex">
      <span
        tabIndex={0}
        title={content}
        className="inline-flex h-5 w-5 cursor-help items-center justify-center rounded-full border border-[var(--accent)] bg-[rgba(255,107,53,0.16)] text-[11px] font-black text-[var(--accent)] outline-none shadow-[0_0_12px_rgba(255,107,53,0.24)] transition hover:bg-[var(--accent)] hover:text-black focus:bg-[var(--accent)] focus:text-black"
        aria-label={content}
      >
        i
      </span>
      <span className="pointer-events-none absolute left-1/2 top-7 z-50 hidden w-72 -translate-x-1/2 rounded-xl border border-[var(--accent)] bg-[#101118] p-3 text-left text-[11px] font-medium leading-5 text-[var(--text-primary)] shadow-2xl shadow-black/50 group-hover:block group-focus-within:block">
        {content}
      </span>
    </span>
  );
}
