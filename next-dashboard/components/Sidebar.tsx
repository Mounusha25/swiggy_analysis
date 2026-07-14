"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  IconChartAreaLine,
  IconChartDots3,
  IconDatabase,
  IconFlame,
  IconMicroscope,
  IconMap2,
  IconReportAnalytics,
  IconTargetArrow,
  IconTrendingUp,
} from "@tabler/icons-react";

const navItems = [
  { href: "/", label: "Overview", icon: IconReportAnalytics },
  { href: "/geographic", label: "Geographic", icon: IconMap2 },
  { href: "/segments", label: "Segments", icon: IconChartDots3 },
  { href: "/trends", label: "Trends", icon: IconTrendingUp },
  { href: "/insights", label: "Insights", icon: IconChartAreaLine },
  { href: "/expansion", label: "Expansion", icon: IconTargetArrow },
  { href: "/advanced", label: "Advanced", icon: IconMicroscope },
  { href: "/sql-pipeline", label: "SQL Appendix", icon: IconDatabase },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-20 w-40 border-r border-[var(--border-subtle)] bg-[#101118]/95 px-3 py-5 shadow-2xl shadow-black/40">
      <div className="mb-7 flex items-center gap-2 px-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-[var(--accent)] text-black shadow-[0_0_22px_rgba(255,107,53,0.45)]">
          <IconFlame size={18} fill="currentColor" />
        </div>
        <div>
          <p className="text-sm font-black uppercase leading-tight tracking-wide text-[var(--accent)]">Swiggy</p>
          <p className="text-[9px] uppercase tracking-[0.12em] text-[var(--text-secondary)]">Market Intel</p>
        </div>
      </div>

      <nav className="space-y-2">
        {navItems.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 rounded-xl px-3 py-2.5 text-[11px] font-semibold transition ${
                active
                  ? "bg-[linear-gradient(135deg,#FF6B35,#B84A23)] text-white shadow-[0_0_24px_rgba(255,107,53,0.28)]"
                  : "text-[var(--text-secondary)] hover:bg-[var(--bg-card-hover)] hover:text-[var(--text-primary)]"
              }`}
            >
              <Icon size={16} stroke={1.8} />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
