import type { Metadata } from "next";

import "@/app/globals.css";
import { Sidebar } from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "Swiggy Market Intelligence",
  description: "Executive analytics dashboard powered by precomputed Python extracts.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Sidebar />
        <main className="min-h-screen bg-[var(--bg-page)] pl-40">
          <div className="mx-auto max-w-[1180px] px-5 py-5">{children}</div>
        </main>
      </body>
    </html>
  );
}
