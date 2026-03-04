"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { NavRail } from "./NavRail";
import { useSidebar } from "@/lib/sidebar";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const { isOpen, toggle } = useSidebar();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [user, loading, router]);

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ color: "var(--md-sys-color-on-surface-variant)", fontSize: 14 }}>Loading…</div>
      </div>
    );
  }
  if (!user) return null;

  return (
    <div style={{ display: "flex" }}>
      <NavRail />
      <main
        style={{
          marginLeft: isOpen ? 80 : 0,
          flex: 1,
          minHeight: "100vh",
          padding: "24px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          transition: "margin-left 200ms ease-in-out",
        }}
        className="md:ml-20"
      >
        <div style={{ width: "100%", maxWidth: 1000, display: "flex", flexDirection: "column" }}>
          {children}
        </div>
      </main>
    </div>
  );
}
