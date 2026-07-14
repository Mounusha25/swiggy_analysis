"use client";

import { useMemo, useState } from "react";

import type { SqlQueryResult } from "@/lib/data";

export function SqlExplorer({ queries }: { queries: SqlQueryResult[] }) {
  const [selectedSlug, setSelectedSlug] = useState(queries[0]?.slug ?? "");
  const selected = useMemo(
    () => queries.find((query) => query.slug === selectedSlug) ?? queries[0],
    [queries, selectedSlug],
  );
  const columns = useMemo(() => (selected?.rows[0] ? Object.keys(selected.rows[0]) : []), [selected]);
  const csvHref = useMemo(() => {
    if (!selected) return "#";
    const escapeCell = (value: string | number) => `"${String(value).replaceAll('"', '""')}"`;
    const header = columns.map(escapeCell).join(",");
    const body = selected.rows.map((row) => columns.map((column) => escapeCell(row[column])).join(",")).join("\n");
    return `data:text/csv;charset=utf-8,${encodeURIComponent(`${header}\n${body}`)}`;
  }, [columns, selected]);

  return (
    <div className="grid gap-4">
      <div className="grid gap-3 md:grid-cols-3">
        <PipelineStat label="SQLite Source" value="swiggy.db" helper="Materialized from Python pipeline" />
        <PipelineStat label="Queries Available" value={queries.length.toString()} helper="Precomputed JSON outputs" />
        <PipelineStat label="Selected Result Rows" value={(selected?.rows.length ?? 0).toLocaleString("en-IN")} helper="Downloadable as CSV" />
      </div>

      <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div className="flex-1">
            <label htmlFor="sql-query-select" className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
              Select an analytics query
            </label>
            <select
              id="sql-query-select"
              value={selectedSlug}
              onChange={(event) => setSelectedSlug(event.target.value)}
              className="mt-2 w-full rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card-hover)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none"
            >
              {queries.map((query) => (
                <option key={query.slug} value={query.slug}>
                  {query.name}
                </option>
              ))}
            </select>
          </div>
          <a
            href={csvHref}
            download={`${selected?.slug ?? "query-result"}.csv`}
            className="rounded-xl bg-[linear-gradient(135deg,#FF6B35,#B84A23)] px-4 py-2 text-center text-xs font-bold text-white shadow-[0_0_20px_rgba(255,107,53,0.24)]"
          >
            Download Result CSV
          </a>
        </div>
      </div>

      <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4">
        <h2 className="text-sm font-semibold">{selected.name}</h2>
        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">{selected.description}</p>
        <details className="mt-4" open>
          <summary className="cursor-pointer text-xs font-semibold uppercase tracking-wide text-[var(--accent)]">View SQL</summary>
          <pre className="mt-3 max-h-80 overflow-auto rounded-xl bg-black/30 p-4 text-[11px] leading-5 text-[var(--text-secondary)]">
            {selected.sql}
          </pre>
        </details>
      </div>

      <div className="overflow-hidden rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)]">
        <div className="border-b border-[var(--border-subtle)] px-4 py-3 text-xs text-[var(--text-secondary)]">
          Results - {selected.rows.length.toLocaleString("en-IN")} rows
        </div>
        <table className="w-full text-left text-xs">
          <thead className="bg-[var(--bg-card-hover)] text-[var(--text-secondary)]">
            <tr>
              {columns.map((column) => (
                <th key={column} className="px-3 py-2">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {selected.rows.map((row, index) => (
              <tr key={index} className="border-t border-[var(--border-subtle)]">
                {columns.map((column) => (
                  <td key={column} className="px-3 py-2">
                    {String(row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PipelineStat({ label, value, helper }: { label: string; value: string; helper: string }) {
  return (
    <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-[var(--text-secondary)]">{label}</p>
      <p className="mt-2 text-xl font-semibold text-[var(--text-primary)]">{value}</p>
      <p className="mt-1 text-xs text-[var(--text-secondary)]">{helper}</p>
    </div>
  );
}
