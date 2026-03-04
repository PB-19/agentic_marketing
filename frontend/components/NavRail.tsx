"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { useSidebar } from "@/lib/sidebar";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: "⬡" },
  { href: "/research", label: "Research", icon: "🔍" },
  { href: "/webpage", label: "Webpage", icon: "🌐" },
  { href: "/instagram", label: "Instagram", icon: "📸" },
  { href: "/analytics", label: "Analytics", icon: "📊" },
];

export function NavRail() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { isOpen, toggle } = useSidebar();

  return (
    <nav
      style={{
        width: isOpen ? 80 : 60,
        minHeight: "100vh",
        background: "var(--md-sys-color-surface-variant)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        paddingTop: 24,
        paddingBottom: 24,
        gap: 4,
        position: "fixed",
        left: 0,
        top: 0,
        bottom: 0,
        zIndex: 100,
        overflow: "hidden",
        transition: "width 200ms ease-in-out",
      }}
    >
        <button
          onClick={toggle}
          style={{
            width: 64,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 4,
            padding: "12px 0",
            borderRadius: "var(--md-shape-lg)",
            background: "transparent",
            color: "var(--md-sys-color-on-surface-variant)",
            border: "none",
            cursor: "pointer",
            fontSize: 20,
            marginBottom: 12,
          }}
          title="Toggle sidebar"
        >
          ✦
        </button>
        {user && (
          <div style={{ fontSize: 11, color: "var(--md-sys-color-on-surface-variant)", textAlign: "center", padding: "0 8px", wordBreak: "break-all", marginBottom: 16 }}>
            {user.username}
          </div>
        )}
        {NAV_ITEMS.map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                width: 64,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 4,
                padding: "12px 0",
                borderRadius: "var(--md-shape-lg)",
                background: active ? "var(--md-sys-color-secondary-container)" : "transparent",
                color: active ? "var(--md-sys-color-on-secondary-container)" : "var(--md-sys-color-on-surface-variant)",
                textDecoration: "none",
                fontSize: 20,
                transition: "background 150ms",
              }}
            >
              <span>{item.icon}</span>
              <span style={{ fontSize: 11, fontWeight: 500, letterSpacing: 0.5 }}>{item.label}</span>
            </Link>
          );
        })}
        <div style={{ flex: 1 }} />
        <button
          onClick={logout}
          style={{
            width: 64, display: "flex", flexDirection: "column", alignItems: "center",
            gap: 4, padding: "12px 0", borderRadius: "var(--md-shape-lg)",
            background: "transparent", color: "var(--md-sys-color-on-surface-variant)",
            border: "none", cursor: "pointer", fontSize: 20,
          }}
        >
          <span>🚪</span>
          <span style={{ fontSize: 11, fontWeight: 500 }}>Logout</span>
        </button>
      </nav>
    );
  }

