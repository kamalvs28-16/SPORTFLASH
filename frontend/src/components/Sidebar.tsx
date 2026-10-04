"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Video,
  UserCheck,
  ShieldCheck,
  Target,
  FileText,
  Zap,
} from "lucide-react";

const navItems = [
  { name: "Dashboard Overview", href: "/", icon: LayoutDashboard },
  { name: "Team & Player Roster", href: "/roster", icon: Users },
  { name: "Speed Calculation", href: "/speed", icon: Zap },
  { name: "Video & AI Studio", href: "/studio", icon: Video },
  { name: "Player Analytics", href: "/players", icon: UserCheck },
  { name: "Team Classification", href: "/teams", icon: ShieldCheck },
  { name: "Event Detection", href: "/events", icon: Target },
  { name: "Match Report", href: "/report", icon: FileText },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      style={{
        width: 256,
        background: "rgba(22,16,38,0.95)",
        borderRight: "1px solid rgba(225,223,220,0.1)",
        minHeight: "100vh",
        padding: "var(--space-9)",
        display: "flex",
        flexDirection: "column",
        boxShadow: "var(--shadow-sm)",
      }}
    >
      {/* Brand Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "var(--space-8)",
          paddingBottom: "var(--space-10)",
          marginBottom: "var(--space-10)",
          borderBottom: "1px solid rgba(225,223,220,0.1)",
        }}
      >
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: "var(--radius-md)",
            background: "var(--color-2)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 20,
            boxShadow: "0 0 20px rgba(128,51,235,0.4)",
          }}
        >
          ⚽
        </div>
        <div>
          <h1
            style={{
              fontWeight: 500,
              fontSize: "var(--text-lg)",
              color: "var(--color-7)",
              letterSpacing: "0.05em",
              lineHeight: 1,
              margin: 0,
            }}
          >
            SPORTFLASH
          </h1>
          <p
            style={{
              fontSize: "var(--text-xs)",
              color: "var(--color-3)",
              margin: 0,
              marginTop: 4,
            }}
          >
            AI Performance Engine
          </p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ flex: 1, display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.name}
              href={item.href}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "var(--space-8)",
                padding: "var(--space-5) var(--space-8)",
                borderRadius: "var(--radius-md)",
                fontSize: "var(--text-sm)",
                fontWeight: isActive ? 500 : 400,
                color: isActive ? "var(--color-7)" : "var(--color-4)",
                background: isActive ? "rgba(128,51,235,0.18)" : "transparent",
                border: `1px solid ${isActive ? "rgba(128,51,235,0.35)" : "transparent"}`,
                textDecoration: "none",
                transition:
                  "color 0.3s cubic-bezier(0.2,0,0.2,1), background-color 0.3s cubic-bezier(0.2,0,0.2,1), border-color 0.3s cubic-bezier(0.2,0,0.2,1)",
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  (e.currentTarget as HTMLElement).style.color = "var(--color-6)";
                  (e.currentTarget as HTMLElement).style.background =
                    "rgba(128,51,235,0.08)";
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  (e.currentTarget as HTMLElement).style.color = "var(--color-4)";
                  (e.currentTarget as HTMLElement).style.background = "transparent";
                }
              }}
            >
              <Icon
                style={{
                  width: 18,
                  height: 18,
                  color: isActive ? "var(--color-3)" : "currentColor",
                  flexShrink: 0,
                }}
              />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div
        style={{
          marginTop: "auto",
          paddingTop: "var(--space-10)",
          borderTop: "1px solid rgba(225,223,220,0.1)",
        }}
      >
        <div
          style={{
            background: "rgba(128,51,235,0.08)",
            border: "1px solid rgba(128,51,235,0.2)",
            borderRadius: "var(--radius-md)",
            padding: "var(--space-6) var(--space-8)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-5)" }}>
            <span style={{ position: "relative", display: "flex", width: 10, height: 10 }}>
              <span
                className="animate-ping"
                style={{
                  position: "absolute",
                  inset: 0,
                  borderRadius: "50%",
                  background: "var(--color-3)",
                  opacity: 0.5,
                }}
              />
              <span
                style={{
                  position: "relative",
                  display: "inline-flex",
                  width: 10,
                  height: 10,
                  borderRadius: "50%",
                  background: "var(--color-2)",
                }}
              />
            </span>
            <span style={{ fontSize: "var(--text-xs)", color: "var(--color-4)" }}>
              FastAPI Pipeline
            </span>
          </div>
          <span
            className="rf-badge"
            style={{ fontSize: 10, padding: "2px 8px" }}
          >
            Online
          </span>
        </div>
      </div>
    </aside>
  );
}
