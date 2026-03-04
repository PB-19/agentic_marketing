"use client";
import { useState } from "react";
import { AppShell } from "@/components/AppShell";
import { usePipeline } from "@/lib/pipeline";
import { api } from "@/lib/api";

export default function ResearchPage() {
  const { idea, setIdea, setResearch, research } = usePipeline();
  const [refUrl, setRefUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let result: any;
      if (file) {
        result = await api.research.runWithDoc(idea, file, refUrl || undefined);
      } else {
        result = await api.research.run(idea, refUrl || undefined);
      }
      setResearch(result);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Research failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div style={{ maxWidth: 720 }}>
        <h1 style={{ fontSize: 32, fontWeight: 400, marginBottom: 4 }}>Research</h1>
        <p style={{ fontSize: 16, color: "var(--md-sys-color-on-surface-variant)", marginBottom: 28 }}>
          Describe your product or project idea. The agent will research the market, competitors, and marketing angles.
        </p>

        <form onSubmit={run} style={{ display: "flex", flexDirection: "column", gap: 16, marginBottom: 32 }}>
          <div>
            <label className="field-label">Your idea *</label>
            <textarea className="field-textarea" value={idea} onChange={e => setIdea(e.target.value)} placeholder="e.g. An AI-powered football training app that creates personalised drills based on player stats" required />
          </div>
          <div>
            <label className="field-label">Reference URL (optional)</label>
            <input className="field-input" value={refUrl} onChange={e => setRefUrl(e.target.value)} placeholder="https://competitor.com" />
          </div>
          <div>
            <label className="field-label">Upload document (optional — .txt, .md, .pdf, max 2MB)</label>
            <input
              type="file" accept=".txt,.md,.pdf"
              onChange={e => setFile(e.target.files?.[0] ?? null)}
              style={{ marginTop: 4, fontSize: 14, color: "var(--md-sys-color-on-surface-variant)" }}
            />
            {file && <div style={{ fontSize: 12, marginTop: 4, color: "var(--md-sys-color-primary)" }}>{file.name}</div>}
          </div>

          {error && (
            <div style={{ padding: "12px 16px", background: "var(--md-sys-color-error-container)", color: "var(--md-sys-color-on-error-container)", borderRadius: "var(--md-shape-xs)", fontSize: 14 }}>
              {error}
            </div>
          )}
          <button className="btn-filled" type="submit" disabled={loading || !idea.trim()}>
            {loading ? "Researching…" : "Run research"}
          </button>
        </form>

        {research && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <h2 style={{ fontSize: 22, fontWeight: 400 }}>Results</h2>
            <div className="card-outlined" style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
              <span className="chip chip-selected">{research.domain_primary}</span>
              <span className="chip chip-selected">{research.novelty_verdict}</span>
              {research.domain_secondary.map((d: string) => <span key={d} className="chip">{d}</span>)}
            </div>

            <div className="card-outlined">
              <div style={{ fontSize: 12, fontWeight: 500, letterSpacing: 0.5, color: "var(--md-sys-color-on-surface-variant)", marginBottom: 8 }}>DIFFERENTIATING ASPECTS</div>
              <ul style={{ paddingLeft: 20, fontSize: 14, display: "flex", flexDirection: "column", gap: 4 }}>
                {research.differentiating_aspects.map((a: string, i: number) => <li key={i}>{a}</li>)}
              </ul>
            </div>

            <div className="card-outlined">
              <div style={{ fontSize: 12, fontWeight: 500, letterSpacing: 0.5, color: "var(--md-sys-color-on-surface-variant)", marginBottom: 8 }}>COMPETITORS</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {research.competitors.map((c: { name: string; strengths: string; weaknesses: string; positioning: string }, i: number) => (
                  <div key={i} style={{ paddingBottom: 12, borderBottom: i < research.competitors.length - 1 ? "1px solid var(--md-sys-color-outline-variant)" : "none" }}>
                    <div style={{ fontWeight: 500, marginBottom: 4 }}>{c.name}</div>
                    <div style={{ fontSize: 13, color: "var(--md-sys-color-on-surface-variant)" }}>
                      <span style={{ color: "var(--md-sys-color-primary)" }}>+</span> {c.strengths} &nbsp;·&nbsp;
                      <span style={{ color: "var(--md-sys-color-error)" }}>−</span> {c.weaknesses}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card-outlined">
              <div style={{ fontSize: 12, fontWeight: 500, letterSpacing: 0.5, color: "var(--md-sys-color-on-surface-variant)", marginBottom: 8 }}>MARKETING IMPLICATIONS</div>
              <ul style={{ paddingLeft: 20, fontSize: 14, display: "flex", flexDirection: "column", gap: 4 }}>
                {research.marketing_implications.map((m: string, i: number) => <li key={i}>{m}</li>)}
              </ul>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
