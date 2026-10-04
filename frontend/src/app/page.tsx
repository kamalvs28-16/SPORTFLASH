"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Users,
  Video,
  Activity,
  ShieldCheck,
  Zap,
  Target,
  FileText,
  ArrowRight,
  Trophy,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";

/* ── Shared sub-components ──────────────────────────────────────────── */

function MetricCard({
  label,
  icon,
  children,
  note,
}: {
  label: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  note: string;
}) {
  return (
    <div className="rf-card" style={{ padding: "var(--space-10)" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "var(--space-5)",
        }}
      >
        <span
          style={{
            fontSize: "var(--text-xs)",
            fontWeight: 500,
            color: "var(--color-4)",
            textTransform: "uppercase",
            letterSpacing: "0.07em",
          }}
        >
          {label}
        </span>
        {icon}
      </div>
      {children}
      <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", marginTop: "var(--space-4)" }}>
        {note}
      </p>
    </div>
  );
}

/* ── Page ───────────────────────────────────────────────────────────── */

export default function DashboardOverview() {
  const [players, setPlayers] = useState<any[]>([]);
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [playersRes, statusRes] = await Promise.all([
          fetch("http://localhost:8000/api/players"),
          fetch("http://localhost:8000/api/status"),
        ]);
        const pData = await playersRes.json();
        const sData = await statusRes.json();
        setPlayers(pData.players || []);
        setStatus(sData);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const teamA = players.filter((p) => p.team === "Team A");
  const teamB = players.filter((p) => p.team === "Team B");
  const topPlayers = [...players]
    .sort((a, b) => b.performance_score - a.performance_score)
    .slice(0, 5);

  const iconStyle = { width: 18, height: 18, color: "var(--color-3)" };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-11)" }}>
      {/* ── Hero Banner ─────────────────────────────────────────────── */}
      <div
        style={{
          position: "relative",
          overflow: "hidden",
          borderRadius: "var(--radius-md)",
          background:
            "linear-gradient(135deg, rgba(128,51,235,0.15) 0%, rgba(22,16,38,0.9) 50%, rgba(128,51,235,0.08) 100%)",
          border: "1px solid rgba(128,51,235,0.25)",
          padding: "var(--space-13)",
          boxShadow: "var(--shadow-sm)",
        }}
      >
        {/* Decorative glow */}
        <div
          aria-hidden
          style={{
            position: "absolute",
            top: -60,
            right: -60,
            width: 300,
            height: 300,
            borderRadius: "50%",
            background: "rgba(128,51,235,0.12)",
            filter: "blur(60px)",
            pointerEvents: "none",
          }}
        />

        <div style={{ position: "relative", zIndex: 1, maxWidth: 640 }}>
          <div className="rf-badge" style={{ marginBottom: "var(--space-8)", display: "inline-flex" }}>
            ⚽ SPORTFLASH Next.js Engine Ready
          </div>

          <h1
            style={{
              fontSize: "clamp(28px, 4vw, 56px)",
              fontWeight: 500,
              color: "var(--color-7)",
              lineHeight: 1.15,
              margin: "0 0 var(--space-8)",
            }}
          >
            Football AI Performance &amp; Player Identification Studio
          </h1>

          <p
            style={{
              fontSize: "var(--text-sm)",
              color: "var(--color-4)",
              lineHeight: "24px",
              margin: "0 0 var(--space-10)",
            }}
          >
            Real-time player tracking, HSV jersey team classification, homography pitch speed
            (km/h), defensive tackles &amp; duels, positional heatmaps, and automated match
            reports.
          </p>

          <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-8)" }}>
            <Link
              href="/studio"
              className="rf-btn-primary"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "var(--space-5)",
                textDecoration: "none",
              }}
            >
              <Video style={{ width: 15, height: 15 }} />
              <span>Launch Video AI Studio</span>
              <ArrowRight style={{ width: 15, height: 15 }} />
            </Link>

            <Link
              href="/roster"
              className="rf-btn-secondary"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "var(--space-5)",
                textDecoration: "none",
              }}
            >
              <Users style={{ width: 15, height: 15, color: "var(--color-3)" }} />
              <span>Calibrate Team Roster</span>
            </Link>
          </div>
        </div>
      </div>

      {/* ── Metrics Row ─────────────────────────────────────────────── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "var(--space-9)",
        }}
      >
        <MetricCard
          label="Players Analysed"
          icon={<Users style={iconStyle} />}
          note="Tracked with persistent ByteTrack IDs"
        >
          <p
            style={{
              fontSize: 36,
              fontWeight: 300,
              color: "var(--color-7)",
              margin: 0,
              lineHeight: 1,
            }}
          >
            {players.length}
          </p>
        </MetricCard>

        <MetricCard
          label="Team Breakdown"
          icon={<ShieldCheck style={iconStyle} />}
          note="Classified by jersey HSV color clustering"
        >
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-10)" }}>
            <div>
              <span style={{ fontSize: "var(--text-xs)", color: "#E63946", fontWeight: 500 }}>
                Team A:{" "}
              </span>
              <span style={{ fontSize: "var(--text-lg)", fontWeight: 300, color: "var(--color-7)" }}>
                {teamA.length}
              </span>
            </div>
            <div
              style={{
                width: 1,
                height: 24,
                background: "rgba(225,223,220,0.1)",
              }}
            />
            <div>
              <span style={{ fontSize: "var(--text-xs)", color: "#3B82F6", fontWeight: 500 }}>
                Team B:{" "}
              </span>
              <span style={{ fontSize: "var(--text-lg)", fontWeight: 300, color: "var(--color-7)" }}>
                {teamB.length}
              </span>
            </div>
          </div>
        </MetricCard>

        <MetricCard
          label="Top Sprint Speed"
          icon={<Zap style={iconStyle} />}
          note="Calculated via Pitch Homography"
        >
          <p
            style={{
              fontSize: 36,
              fontWeight: 300,
              color: "var(--color-3)",
              margin: 0,
              lineHeight: 1,
            }}
          >
            {players.length > 0
              ? `${Math.max(...players.map((p) => p.maximum_speed_kmh || 0))} km/h`
              : "28.4 km/h"}
          </p>
        </MetricCard>

        <MetricCard
          label="Defensive Tackles"
          icon={<Target style={iconStyle} />}
          note="Proximity engagement & duel analysis"
        >
          <p
            style={{
              fontSize: 36,
              fontWeight: 300,
              color: "var(--color-3)",
              margin: 0,
              lineHeight: 1,
            }}
          >
            {players.reduce((acc, p) => acc + (p.tackles_won || 0), 0)} Won
          </p>
        </MetricCard>
      </div>

      {/* ── Top Performers & Module Status ──────────────────────────── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: "var(--space-11)",
        }}
      >
        {/* Top Player Ratings */}
        <div className="rf-card" style={{ padding: "var(--space-10)" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              borderBottom: "1px solid rgba(225,223,220,0.1)",
              paddingBottom: "var(--space-9)",
              marginBottom: "var(--space-9)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "var(--space-5)" }}>
              <Trophy style={{ width: 18, height: 18, color: "var(--color-3)" }} />
              <h3
                style={{
                  fontSize: "var(--text-base)",
                  fontWeight: 500,
                  color: "var(--color-7)",
                  margin: 0,
                }}
              >
                Top Rated Player Performers
              </h3>
            </div>
            <Link
              href="/players"
              style={{
                fontSize: "var(--text-xs)",
                fontWeight: 500,
                color: "var(--color-3)",
                textDecoration: "none",
                transition: "color 0.3s cubic-bezier(0.2,0,0.2,1)",
              }}
            >
              View All Players →
            </Link>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
            {topPlayers.map((p, idx) => (
              <div
                key={p.player_id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "var(--space-8) var(--space-9)",
                  borderRadius: "var(--radius-md)",
                  background: "rgba(22,16,38,0.6)",
                  border: "1px solid rgba(225,223,220,0.08)",
                  transition: "border-color 0.3s cubic-bezier(0.2,0,0.2,1)",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.borderColor =
                    "rgba(128,51,235,0.3)";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.borderColor =
                    "rgba(225,223,220,0.08)";
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-9)" }}>
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: "50%",
                      background: "rgba(128,51,235,0.15)",
                      border: "1px solid rgba(128,51,235,0.3)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "var(--text-xs)",
                      fontWeight: 500,
                      color: "var(--color-3)",
                    }}
                  >
                    #{idx + 1}
                  </div>
                  <div>
                    <h4
                      style={{
                        fontSize: "var(--text-sm)",
                        fontWeight: 500,
                        color: "var(--color-7)",
                        margin: 0,
                      }}
                    >
                      #{p.jersey_number} {p.name}
                    </h4>
                    <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0 }}>
                      {p.team} · {p.position}
                    </p>
                  </div>
                </div>

                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "var(--space-11)",
                    textAlign: "right",
                  }}
                >
                  <div>
                    <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0 }}>
                      Max Speed
                    </p>
                    <p
                      style={{
                        fontSize: "var(--text-sm)",
                        fontWeight: 500,
                        color: "var(--color-6)",
                        margin: 0,
                      }}
                    >
                      {p.maximum_speed_kmh} km/h
                    </p>
                  </div>
                  <div>
                    <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0 }}>
                      Tackles
                    </p>
                    <p
                      style={{
                        fontSize: "var(--text-sm)",
                        fontWeight: 500,
                        color: "var(--color-3)",
                        margin: 0,
                      }}
                    >
                      {p.tackles_won}/{p.tackles_attempted}
                    </p>
                  </div>
                  <div
                    style={{
                      background: "rgba(128,51,235,0.12)",
                      border: "1px solid rgba(128,51,235,0.3)",
                      borderRadius: "var(--radius-sm)",
                      padding: "var(--space-3) var(--space-8)",
                      textAlign: "center",
                    }}
                  >
                    <p
                      style={{
                        fontSize: 10,
                        color: "var(--color-3)",
                        fontWeight: 500,
                        textTransform: "uppercase",
                        letterSpacing: "0.06em",
                        margin: 0,
                      }}
                    >
                      Rating
                    </p>
                    <p
                      style={{
                        fontSize: "var(--text-base)",
                        fontWeight: 500,
                        color: "var(--color-3)",
                        margin: 0,
                      }}
                    >
                      {p.performance_score}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Modules Status */}
        <div className="rf-card" style={{ padding: "var(--space-10)" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "var(--space-5)",
              borderBottom: "1px solid rgba(225,223,220,0.1)",
              paddingBottom: "var(--space-9)",
              marginBottom: "var(--space-9)",
            }}
          >
            <Activity style={{ width: 18, height: 18, color: "var(--color-3)" }} />
            <h3
              style={{
                fontSize: "var(--text-base)",
                fontWeight: 500,
                color: "var(--color-7)",
                margin: 0,
              }}
            >
              AI Computer Vision Modules
            </h3>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-5)" }}>
            {[
              { label: "YOLO Persistent Tracker", key: "tracking" },
              { label: "HSV Team Classification", key: "team_classification" },
              { label: "Homography Speed Estimator", key: "speed_analysis" },
              { label: "Defensive Tackle & Duel Engine", key: "tackle_analysis" },
              { label: "AI Tactical Insights", key: "ai_insights" },
              { label: "Automated Match Report", key: "match_report" },
            ].map((m) => {
              const isOk = status?.modules?.[m.key];
              return (
                <div
                  key={m.key}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "var(--space-6) var(--space-8)",
                    borderRadius: "var(--radius-sm)",
                    background: "rgba(22,16,38,0.6)",
                    border: "1px solid rgba(225,223,220,0.06)",
                  }}
                >
                  <span
                    style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", fontWeight: 400 }}
                  >
                    {m.label}
                  </span>
                  {isOk ? (
                    <span
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "var(--space-3)",
                        fontSize: "var(--text-xs)",
                        fontWeight: 500,
                        color: "var(--color-3)",
                        background: "rgba(128,51,235,0.1)",
                        border: "1px solid rgba(128,51,235,0.25)",
                        borderRadius: "var(--radius-sm)",
                        padding: "2px 8px",
                      }}
                    >
                      <CheckCircle2 style={{ width: 12, height: 12 }} />
                      Ready
                    </span>
                  ) : (
                    <span
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "var(--space-3)",
                        fontSize: "var(--text-xs)",
                        fontWeight: 500,
                        color: "var(--color-4)",
                        background: "rgba(202,201,200,0.08)",
                        border: "1px solid rgba(202,201,200,0.15)",
                        borderRadius: "var(--radius-sm)",
                        padding: "2px 8px",
                      }}
                    >
                      <AlertCircle style={{ width: 12, height: 12 }} />
                      Pending
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
