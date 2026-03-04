"use client";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { api } from "@/lib/api";

interface IdeaRow {
  id: number;
  idea_text: string;
  domain_primary: string;
  novelty_verdict: string;
  created_at: string;
}

interface Page { items: IdeaRow[]; total: number; page: number; page_size: number; }

export default function AnalyticsPage() {
  const [page, setPage] = useState(1);
  const [data, setData] = useState<Page | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api.analytics.ideas(page) as Promise<any>).then(setData).finally(() => setLoading(false));
  }, [page]);

  const NOVELTY_COLOR: Record<string, string> = {
    "Novel": "var(--md-sys-color-primary)",
    "Competitive entry": "var(--md-sys-color-secondary)",
    "Hybrid": "var(--md-sys-color-tertiary)",
  };

  return (
    <AppShell>
      <div style={{ maxWidth: 800 }}>
        <h1 style={{ fontSize: 32, fontWeight: 400, marginBottom: 4 }}>Analytics</h1>
        <p style={{ fontSize: 16, color: "var(--md-sys-color-on-surface-variant)", marginBottom: 28 }}>
          Your research history.
        </p>

        {loading && <div style={{ color: "var(--md-sys-color-on-surface-variant)", fontSize: 14 }}>Loading…</div>}

        {data && (
          <>
            <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 24 }}>
              {data.items.map(row => (
                <div key={row.id} className="card-outlined" style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 14, fontWeight: 500, marginBottom: 4, lineHeight: 1.4 }}>{row.idea_text.slice(0, 120)}{row.idea_text.length > 120 ? "…" : ""}</div>
                    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                      <span className="chip" style={{ fontSize: 11, height: 24, padding: "0 8px" }}>{row.domain_primary}</span>
                      <span style={{
                        display: "inline-flex", alignItems: "center", height: 24, padding: "0 8px",
                        borderRadius: "var(--md-shape-full)", fontSize: 11, fontWeight: 500,
                        color: NOVELTY_COLOR[row.novelty_verdict] ?? "var(--md-sys-color-on-surface-variant)",
                        border: `1px solid ${NOVELTY_COLOR[row.novelty_verdict] ?? "var(--md-sys-color-outline)"}`,
                      }}>{row.novelty_verdict}</span>
                    </div>
                  </div>
                  <div style={{ fontSize: 12, color: "var(--md-sys-color-on-surface-variant)", flexShrink: 0, marginTop: 2 }}>
                    {new Date(row.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <button className="btn-outlined" onClick={() => setPage(p => p - 1)} disabled={page === 1}>Previous</button>
              <span style={{ fontSize: 14, color: "var(--md-sys-color-on-surface-variant)" }}>
                Page {data.page} · {data.total} total
              </span>
              <button className="btn-outlined" onClick={() => setPage(p => p + 1)} disabled={page * data.page_size >= data.total}>Next</button>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
