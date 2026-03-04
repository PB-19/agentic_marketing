"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import Link from "next/link";

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) router.replace("/dashboard");
  }, [user, loading, router]);

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 24, padding: 24 }}>
      <div style={{ textAlign: "center", maxWidth: 480 }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>✦</div>
        <h1 style={{ fontSize: 32, fontWeight: 400, color: "var(--md-sys-color-on-surface)", marginBottom: 12 }}>
          Agentic Marketing
        </h1>
        <p style={{ fontSize: 16, color: "var(--md-sys-color-on-surface-variant)", marginBottom: 32, lineHeight: 1.6 }}>
          AI-powered market research, landing pages, and Instagram content — all from a single idea.
        </p>
        <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
          <Link href="/login" className="btn-filled">Login</Link>
          <Link href="/register" className="btn-outlined">Register</Link>
        </div>
      </div>
    </div>
  );
}
