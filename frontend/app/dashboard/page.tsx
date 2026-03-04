"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { usePipeline } from "@/lib/pipeline";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

const STEPS = [
  { label: "Research", href: "/research", desc: "Analyse your idea and competitive landscape" },
  { label: "Webpage", href: "/webpage", desc: "Generate and deploy a landing page" },
  { label: "Instagram Trends", href: "/instagram", desc: "Research social media trends" },
  { label: "Generate Posts", href: "/instagram", desc: "Create AI images and captions" },
  { label: "Publish", href: "/instagram", desc: "Post to Instagram with consent" },
];

export default function DashboardPage() {
  const { user } = useAuth();
  const { research, deploy, trendBrief, posts } = usePipeline();
  const router = useRouter();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    api.analytics.summary().then(setSummary).catch(() => null);
  }, []);

  const completedSteps = [
    !!research,
    !!deploy,
    !!trendBrief,
    posts.length > 0,
    false, // publish is always action-required
  ];

  return (
    <AppShell>
      <div style={{ maxWidth: 800 }}>
        <h1 style={{ fontSize: 32, fontWeight: 400, marginBottom: 4 }}>
          Welcome back, {user?.username}
        </h1>
        <p style={{ fontSize: 16, color: "var(--md-sys-color-on-surface-variant)", marginBottom: 32 }}>
          Follow the pipeline steps below to market your idea.
        </p>

        {/* Pipeline stepper */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12, marginBottom: 40 }}>
          {STEPS.map((step, i) => (
            <Link href={step.href} key={i} style={{ textDecoration: "none" }}>
              <div className={completedSteps[i] ? "card" : "card-outlined"} style={{ display: "flex", alignItems: "center", gap: 16, cursor: "pointer" }}>
                <div style={{
                  width: 36, height: 36, borderRadius: "var(--md-shape-full)",
                  background: completedSteps[i] ? "var(--md-sys-color-primary)" : "var(--md-sys-color-surface-variant)",
                  color: completedSteps[i] ? "var(--md-sys-color-on-primary)" : "var(--md-sys-color-on-surface-variant)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontWeight: 500, fontSize: 14, flexShrink: 0,
                }}>
                  {completedSteps[i] ? "✓" : i + 1}
                </div>
                <div>
                  <div style={{ fontSize: 16, fontWeight: 500, color: "var(--md-sys-color-on-surface)" }}>{step.label}</div>
                  <div style={{ fontSize: 14, color: "var(--md-sys-color-on-surface-variant)" }}>{step.desc}</div>
                </div>
                <div style={{ marginLeft: "auto", color: "var(--md-sys-color-on-surface-variant)", fontSize: 18 }}>›</div>
              </div>
            </Link>
          ))}
        </div>

        {/* Analytics summary */}
        {summary && (
          <div>
            <h2 style={{ fontSize: 22, fontWeight: 400, marginBottom: 16 }}>Your stats</h2>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 12 }}>
              <div className="card-filled" style={{ textAlign: "center", padding: 20 }}>
                <div style={{ fontSize: 32, fontWeight: 400, color: "var(--md-sys-color-primary)" }}>{summary.total_queries}</div>
                <div style={{ fontSize: 12, color: "var(--md-sys-color-on-surface-variant)", marginTop: 4 }}>Total Research Queries</div>
              </div>
              {summary.novelty_breakdown.map((n: { verdict: string; count: number }) => (
                <div key={n.verdict} className="card-filled" style={{ textAlign: "center", padding: 20 }}>
                  <div style={{ fontSize: 32, fontWeight: 400, color: "var(--md-sys-color-secondary)" }}>{n.count}</div>
                  <div style={{ fontSize: 12, color: "var(--md-sys-color-on-surface-variant)", marginTop: 4 }}>{n.verdict}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
