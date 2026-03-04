"use client";
import { useState } from "react";
import { AppShell } from "@/components/AppShell";
import { usePipeline, GeneratedPost } from "@/lib/pipeline";
import { api } from "@/lib/api";

type Tab = "trends" | "generate" | "publish";

export default function InstagramPage() {
  const { idea, research, trendBrief, setTrendBrief, posts, setPosts } = usePipeline();
  const [tab, setTab] = useState<Tab>("trends");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Generate state
  const [numPosts, setNumPosts] = useState(3);
  const [stylePrefs, setStylePrefs] = useState("");

  // Publish state
  const [igUsername, setIgUsername] = useState("");
  const [igPassword, setIgPassword] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [publishResults, setPublishResults] = useState<any[]>([]);

  const runTrends = async () => {
    if (!research) return;
    setError(""); setLoading(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const result: any = await api.instagram.trends({ idea, research });
      setTrendBrief(result);
      setTab("generate");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Trend research failed");
    } finally { setLoading(false); }
  };

  const runGenerate = async () => {
    if (!trendBrief) return;
    setError(""); setLoading(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const result: any = await api.instagram.generate({ idea, trend_brief: trendBrief, num_posts: numPosts, style_preference: stylePrefs || undefined });
      setPosts(result.posts);
      setTab("publish");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Post generation failed");
    } finally { setLoading(false); }
  };

  const runPublish = async () => {
    if (!confirmed || posts.length === 0) return;
    setError(""); setLoading(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const result: any = await api.instagram.publish({
        image_urls: posts.map((p: GeneratedPost) => p.image_url),
        captions: posts.map((p: GeneratedPost) => p.caption),
        hashtags: posts.map((p: GeneratedPost) => p.hashtags),
        username: igUsername,
        password: igPassword,
      });
      setPublishResults(result.results);
      setIgUsername(""); setIgPassword(""); // clear credentials immediately
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Publish failed");
    } finally { setLoading(false); }
  };

  const TAB_ITEMS: { key: Tab; label: string }[] = [
    { key: "trends", label: "1. Trends" },
    { key: "generate", label: "2. Generate" },
    { key: "publish", label: "3. Publish" },
  ];

  return (
    <AppShell>
      <div style={{ maxWidth: 720 }}>
        <h1 style={{ fontSize: 32, fontWeight: 400, marginBottom: 4 }}>Instagram</h1>
        <p style={{ fontSize: 16, color: "var(--md-sys-color-on-surface-variant)", marginBottom: 24 }}>
          Research trends, generate posts, and publish to Instagram.
        </p>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 8, marginBottom: 28, borderBottom: "1px solid var(--md-sys-color-outline-variant)", paddingBottom: 0 }}>
          {TAB_ITEMS.map(t => (
            <button key={t.key} onClick={() => setTab(t.key)} style={{
              background: "transparent", border: "none", cursor: "pointer",
              padding: "12px 16px", fontSize: 14, fontWeight: 500,
              color: tab === t.key ? "var(--md-sys-color-primary)" : "var(--md-sys-color-on-surface-variant)",
              borderBottom: tab === t.key ? "2px solid var(--md-sys-color-primary)" : "2px solid transparent",
              marginBottom: -1,
            }}>
              {t.label}
            </button>
          ))}
        </div>

        {error && (
          <div style={{ padding: "12px 16px", background: "var(--md-sys-color-error-container)", color: "var(--md-sys-color-on-error-container)", borderRadius: "var(--md-shape-xs)", fontSize: 14, marginBottom: 20 }}>
            {error}
          </div>
        )}

        {/* Tab: Trends */}
        {tab === "trends" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {!research && (
              <div style={{ padding: "12px 16px", background: "var(--md-sys-color-tertiary-container)", color: "var(--md-sys-color-on-tertiary-container)", borderRadius: "var(--md-shape-xs)", fontSize: 14 }}>
                Complete the Research step first.
              </div>
            )}
            <button className="btn-filled" onClick={runTrends} disabled={loading || !research}>
              {loading ? "Researching trends…" : trendBrief ? "Re-run trend research" : "Research trends"}
            </button>

            {trendBrief && (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <div className="card-outlined">
                  <div className="field-label" style={{ marginBottom: 8 }}>TRENDING STYLES</div>
                  <div style={{ fontSize: 14, display: "flex", flexDirection: "column", gap: 4 }}>
                    <div><strong>Format:</strong> {trendBrief.trending_styles.format}</div>
                    <div><strong>Visual:</strong> {trendBrief.trending_styles.visual_style}</div>
                    <div><strong>Tone:</strong> {trendBrief.trending_styles.tone}</div>
                  </div>
                </div>
                <div className="card-outlined">
                  <div className="field-label" style={{ marginBottom: 8 }}>HASHTAG STRATEGY</div>
                  <div style={{ fontSize: 14, marginBottom: 8 }}>{trendBrief.hashtag_strategy.volume_mix}</div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                    {trendBrief.hashtag_strategy.top_hashtags.map((h: string) => <span key={h} className="chip">{h}</span>)}
                  </div>
                </div>
                <div className="card-outlined">
                  <div className="field-label" style={{ marginBottom: 8 }}>BRIEF</div>
                  <p style={{ fontSize: 14, color: "var(--md-sys-color-on-surface-variant)", lineHeight: 1.6 }}>{trendBrief.content_generation_brief}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab: Generate */}
        {tab === "generate" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {!trendBrief && (
              <div style={{ padding: "12px 16px", background: "var(--md-sys-color-tertiary-container)", color: "var(--md-sys-color-on-tertiary-container)", borderRadius: "var(--md-shape-xs)", fontSize: 14 }}>
                Run trend research first.
              </div>
            )}
            <div>
              <label className="field-label">Number of posts</label>
              <input className="field-input" type="number" min={1} max={5} value={numPosts} onChange={e => setNumPosts(Number(e.target.value))} style={{ maxWidth: 120 }} />
            </div>
            <div>
              <label className="field-label">Style preference (optional)</label>
              <input className="field-input" value={stylePrefs} onChange={e => setStylePrefs(e.target.value)} placeholder="e.g. Bold, dark background, motivational" />
            </div>
            <button className="btn-filled" onClick={runGenerate} disabled={loading || !trendBrief}>
              {loading ? "Generating posts… (may take a few minutes)" : "Generate posts"}
            </button>

            {posts.length > 0 && (
              <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 8 }}>
                {posts.map((post: GeneratedPost, i: number) => (
                  <div key={i} className="card-outlined" style={{ display: "flex", gap: 16 }}>
                    <img src={post.image_url} alt={`Post ${i + 1}`} style={{ width: 120, height: 120, objectFit: "cover", borderRadius: "var(--md-shape-sm)", flexShrink: 0 }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 14, marginBottom: 8, lineHeight: 1.5 }}>{post.caption}</div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                        {post.hashtags.slice(0, 5).map((h: string) => <span key={h} className="chip" style={{ fontSize: 11, height: 24, padding: "0 8px" }}>{h}</span>)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab: Publish */}
        {tab === "publish" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {posts.length === 0 && (
              <div style={{ padding: "12px 16px", background: "var(--md-sys-color-tertiary-container)", color: "var(--md-sys-color-on-tertiary-container)", borderRadius: "var(--md-shape-xs)", fontSize: 14 }}>
                Generate posts first.
              </div>
            )}

            {posts.length > 0 && !confirmed && (
              <div className="card-outlined" style={{ borderColor: "var(--md-sys-color-primary)" }}>
                <p style={{ fontSize: 15, marginBottom: 16, lineHeight: 1.6 }}>
                  You are about to post <strong>{posts.length} image(s)</strong> to your Instagram account. The top 5 hashtags will be appended to each caption. Do you want to proceed?
                </p>
                <div style={{ display: "flex", gap: 12 }}>
                  <button className="btn-filled" onClick={() => setConfirmed(true)}>Yes, post to Instagram</button>
                  <button className="btn-outlined" onClick={() => setTab("generate")}>No, go back</button>
                </div>
              </div>
            )}

            {confirmed && publishResults.length === 0 && (
              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                <div style={{ padding: "12px 16px", background: "var(--md-sys-color-primary-container)", color: "var(--md-sys-color-on-primary-container)", borderRadius: "var(--md-shape-xs)", fontSize: 14 }}>
                  Your Instagram credentials are used in-memory only and never stored.
                </div>
                <div>
                  <label className="field-label">Instagram username</label>
                  <input className="field-input" value={igUsername} onChange={e => setIgUsername(e.target.value)} autoComplete="off" />
                </div>
                <div>
                  <label className="field-label">Instagram password</label>
                  <input className="field-input" type="password" value={igPassword} onChange={e => setIgPassword(e.target.value)} autoComplete="new-password" />
                </div>
                <button className="btn-filled" onClick={runPublish} disabled={loading || !igUsername || !igPassword}>
                  {loading ? "Posting…" : "Post now"}
                </button>
              </div>
            )}

            {publishResults.length > 0 && (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <h2 style={{ fontSize: 22, fontWeight: 400 }}>Publish results</h2>
                {publishResults.map((r, i) => (
                  <div key={i} className={r.success ? "card" : "card-outlined"} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <span style={{ fontSize: 20 }}>{r.success ? "✅" : "❌"}</span>
                    <div style={{ fontSize: 14 }}>
                      {r.success ? `Posted — media ID: ${r.media_id}` : `Failed: ${r.error}`}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
