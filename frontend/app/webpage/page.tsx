"use client";
import { useState } from "react";
import { AppShell } from "@/components/AppShell";
import { usePipeline } from "@/lib/pipeline";
import { api } from "@/lib/api";

export default function WebpagePage() {
  const { idea, research, setDeploy, deploy } = usePipeline();
  const [refUrl, setRefUrl] = useState("");
  const [prefs, setPrefs] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const noResearch = !research;

  const run = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!research) return;
    setError(""); setLoading(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let result: any;
      if (file || refUrl) {
        result = await api.webpage.designAndDeployWithRef(idea, research, refUrl || undefined, prefs || undefined, file || undefined);
      } else {
        result = await api.webpage.designAndDeploy({ idea, research, reference_url: refUrl || undefined, text_preferences: prefs || undefined });
      }
      setDeploy(result);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Design failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div style={{ maxWidth: 720 }}>
        <h1 style={{ fontSize: 32, fontWeight: 400, marginBottom: 4 }}>Landing Page</h1>
        <p style={{ fontSize: 16, color: "var(--md-sys-color-on-surface-variant)", marginBottom: 28 }}>
          Design and deploy a Material Design 3 landing page. Complete Research first.
        </p>

        {noResearch && (
          <div style={{ padding: "12px 16px", background: "var(--md-sys-color-tertiary-container)", color: "var(--md-sys-color-on-tertiary-container)", borderRadius: "var(--md-shape-xs)", fontSize: 14, marginBottom: 20 }}>
            Complete the Research step first — the agent needs market context to design your page.
          </div>
        )}

        <form onSubmit={run} style={{ display: "flex", flexDirection: "column", gap: 16, marginBottom: 32 }}>
          <div>
            <label className="field-label">Style preferences (optional)</label>
            <textarea className="field-textarea" value={prefs} onChange={e => setPrefs(e.target.value)} placeholder="e.g. Dark theme, minimalist, bold typography, startup feel" style={{ minHeight: 80 }} />
          </div>
          <div>
            <label className="field-label">Reference URL (optional — agent will treat it as design constraint)</label>
            <input className="field-input" value={refUrl} onChange={e => setRefUrl(e.target.value)} placeholder="https://example.com" />
          </div>
          <div>
            <label className="field-label">Upload design reference (optional — image or PDF, max 2MB)</label>
            <input
              type="file" accept=".jpg,.jpeg,.png,.webp,.pdf"
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
          <button className="btn-filled" type="submit" disabled={loading || noResearch}>
            {loading ? "Designing & deploying… (this may take a minute)" : "Design & deploy"}
          </button>
        </form>

        {deploy && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <h2 style={{ fontSize: 22, fontWeight: 400 }}>Deployed ✓</h2>
            <div className="card-outlined" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div>
                <div className="field-label">Short URL</div>
                <a href={deploy.tiny_url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--md-sys-color-primary)", fontWeight: 500 }}>{deploy.tiny_url}</a>
              </div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <span className="chip">Iteration {deploy.iteration}</span>
                {deploy.notes && <span className="chip">{deploy.notes}</span>}
              </div>
              <a href={deploy.gcs_url} target="_blank" rel="noopener noreferrer" className="btn-tonal" style={{ alignSelf: "flex-start" }}>
                View full page ↗
              </a>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
