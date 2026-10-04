"use client";

import { useState, useEffect } from "react";
import {
  UserCheck,
  Zap,
  Target,
  Activity,
  Shield,
  Flame,
  Apple,
  Search,
  ChevronRight,
} from "lucide-react";

/* ── Stat mini-card ───────────────────────────────────────────────── */
function StatCard({
  icon,
  label,
  value,
  valueColor,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  valueColor?: string;
}) {
  return (
    <div
      className="rf-card"
      style={{ padding: "var(--space-9)", display: "flex", flexDirection: "column", gap: "var(--space-3)" }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "var(--space-4)", color: "var(--color-4)", fontSize: "var(--text-xs)", fontWeight: 500 }}>
        {icon} {label}
      </div>
      <p style={{ fontSize: "var(--text-lg)", fontWeight: 300, color: valueColor || "var(--color-3)", margin: 0 }}>
        {value}
      </p>
    </div>
  );
}

/* ── Insight panel ────────────────────────────────────────────────── */
function InsightPanel({
  icon,
  title,
  items,
}: {
  icon: React.ReactNode;
  title: string;
  items: string[];
}) {
  return (
    <div className="rf-card" style={{ padding: "var(--space-9)" }}>
      <h4
        style={{
          fontSize: "var(--text-sm)",
          fontWeight: 500,
          color: "var(--color-7)",
          margin: "0 0 var(--space-8)",
          display: "flex",
          alignItems: "center",
          gap: "var(--space-5)",
        }}
      >
        {icon} {title}
      </h4>
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-5)" }}>
        {items.map((item, i) => (
          <p key={i} style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0, lineHeight: "19.5px" }}>
            {item}
          </p>
        ))}
      </div>
    </div>
  );
}

/* ── Page ─────────────────────────────────────────────────────────── */
export default function PlayersPage() {
  const [players, setPlayers] = useState<any[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<any>(null);
  const [playerDetails, setPlayerDetails] = useState<any>(null);
  const [search, setSearch] = useState("");
  const [teamFilter, setTeamFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlayers();
  }, []);

  const fetchPlayers = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/players");
      const data = await res.json();
      const list = data.players || [];
      setPlayers(list);
      if (list.length > 0) {
        selectPlayer(list[0].player_id);
      }
    } catch (err) {
      console.error("Error fetching players:", err);
    } finally {
      setLoading(false);
    }
  };

  const selectPlayer = async (pid: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/players/${pid}`);
      const data = await res.json();
      setPlayerDetails(data);
      setSelectedPlayer(players.find((p) => p.player_id === pid) || data.roster);
    } catch (err) {
      console.error("Error fetching player details:", err);
    }
  };

  const filteredPlayers = players.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.jersey_number.toString().includes(search) ||
      p.player_id.includes(search);
    const matchesTeam = teamFilter === "ALL" || p.team === teamFilter;
    return matchesSearch && matchesTeam;
  });

  if (loading)
    return (
      <div style={{ padding: "var(--space-11)", color: "var(--color-4)", fontSize: "var(--text-sm)" }}>
        Loading player analytics…
      </div>
    );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-11)" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: "var(--space-9)",
        }}
      >
        <div>
          <h1
            style={{
              fontSize: "var(--text-xl)",
              fontWeight: 300,
              color: "var(--color-7)",
              margin: 0,
              display: "flex",
              alignItems: "center",
              gap: "var(--space-8)",
            }}
          >
            <UserCheck style={{ width: 28, height: 28, color: "var(--color-3)" }} />
            Player Performance &amp; Tactical Analytics
          </h1>
          <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: "var(--space-4) 0 0" }}>
            Individual player breakdown: running speeds, total distance, defensive tackles, duels, and AI nutrition advice.
          </p>
        </div>

        {/* Search & Team Filter */}
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-8)" }}>
          <div style={{ position: "relative" }}>
            <Search
              style={{
                width: 14,
                height: 14,
                color: "var(--color-4)",
                position: "absolute",
                left: 12,
                top: "50%",
                transform: "translateY(-50%)",
              }}
            />
            <input
              type="text"
              placeholder="Search name or jersey #…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="rf-input"
              style={{ paddingLeft: 34, width: 220 }}
            />
          </div>

          <div
            style={{
              display: "flex",
              background: "rgba(22,16,38,0.8)",
              border: "1px solid rgba(225,223,220,0.12)",
              borderRadius: "var(--radius-md)",
              padding: "var(--space-2)",
              gap: "var(--space-2)",
            }}
          >
            {["ALL", "Team A", "Team B"].map((t) => (
              <button
                key={t}
                onClick={() => setTeamFilter(t)}
                style={{
                  padding: "var(--space-3) var(--space-8)",
                  borderRadius: "var(--radius-sm)",
                  border: "none",
                  fontSize: "var(--text-xs)",
                  fontWeight: 500,
                  cursor: "pointer",
                  background: teamFilter === t ? "var(--color-2)" : "transparent",
                  color: teamFilter === t ? "var(--color-7)" : "var(--color-4)",
                  transition: "background-color 0.3s cubic-bezier(0.2,0,0.2,1), color 0.3s cubic-bezier(0.2,0,0.2,1)",
                }}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "280px 1fr",
          gap: "var(--space-11)",
          alignItems: "start",
        }}
      >
        {/* Player List */}
        <div
          className="rf-card"
          style={{
            padding: "var(--space-8)",
            maxHeight: 750,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: "var(--space-4)",
          }}
        >
          <p
            style={{
              fontSize: "var(--text-xs)",
              fontWeight: 500,
              color: "var(--color-4)",
              textTransform: "uppercase",
              letterSpacing: "0.07em",
              padding: "var(--space-3) var(--space-5)",
              margin: 0,
            }}
          >
            Tracked Players ({filteredPlayers.length})
          </p>

          {filteredPlayers.map((p) => {
            const isSelected = selectedPlayer?.player_id === p.player_id;
            return (
              <button
                key={p.player_id}
                onClick={() => selectPlayer(p.player_id)}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "var(--space-7) var(--space-8)",
                  borderRadius: "var(--radius-md)",
                  border: `1px solid ${isSelected ? "rgba(128,51,235,0.4)" : "rgba(225,223,220,0.06)"}`,
                  background: isSelected ? "rgba(128,51,235,0.15)" : "rgba(22,16,38,0.5)",
                  textAlign: "left",
                  cursor: "pointer",
                  transition: "border-color 0.3s cubic-bezier(0.2,0,0.2,1), background-color 0.3s cubic-bezier(0.2,0,0.2,1)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-8)" }}>
                  <div
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: "var(--radius-sm)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "var(--text-xs)",
                      fontWeight: 500,
                      color: "#fff",
                      backgroundColor: p.team === "Team A" ? "#E63946" : "#1D3557",
                      border: "1px solid rgba(255,255,255,0.15)",
                    }}
                  >
                    #{p.jersey_number}
                  </div>
                  <div>
                    <h4 style={{ fontSize: "var(--text-xs)", fontWeight: 500, color: "var(--color-6)", margin: 0 }}>
                      {p.name}
                    </h4>
                    <p style={{ fontSize: 10, color: "var(--color-4)", margin: 0 }}>
                      {p.team} · {p.position}
                    </p>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-6)" }}>
                  <div style={{ textAlign: "right" }}>
                    <span style={{ fontSize: 10, color: "var(--color-4)", display: "block" }}>Rating</span>
                    <span style={{ fontSize: "var(--text-xs)", fontWeight: 500, color: "var(--color-3)" }}>
                      {p.performance_score}
                    </span>
                  </div>
                  <ChevronRight
                    style={{
                      width: 14,
                      height: 14,
                      color: isSelected ? "var(--color-3)" : "var(--color-4)",
                    }}
                  />
                </div>
              </button>
            );
          })}
        </div>

        {/* Player Detail */}
        {selectedPlayer && (
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-9)" }}>
            {/* Header Card */}
            <div
              className="rf-card"
              style={{
                padding: "var(--space-10)",
                display: "flex",
                flexWrap: "wrap",
                alignItems: "center",
                gap: "var(--space-10)",
              }}
            >
              {selectedPlayer.photo_url ? (
                <img
                  src={`http://localhost:8000${selectedPlayer.photo_url}`}
                  alt={selectedPlayer.name}
                  style={{
                    width: 112,
                    height: 144,
                    borderRadius: "var(--radius-md)",
                    objectFit: "cover",
                    border: "2px solid rgba(128,51,235,0.4)",
                    boxShadow: "0 0 24px rgba(128,51,235,0.2)",
                  }}
                />
              ) : (
                <div
                  style={{
                    width: 112,
                    height: 144,
                    borderRadius: "var(--radius-md)",
                    padding: "var(--space-8)",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#fff",
                    border: "2px solid rgba(255,255,255,0.15)",
                    backgroundColor:
                      selectedPlayer.team === "Team A" ? "#E63946" : "#1D3557",
                  }}
                >
                  <span style={{ fontSize: 10, fontWeight: 500, textTransform: "uppercase" }}>
                    {selectedPlayer.team}
                  </span>
                  <span style={{ fontSize: 36, fontWeight: 300 }}>
                    #{selectedPlayer.jersey_number}
                  </span>
                  <span style={{ fontSize: "var(--text-xs)", fontWeight: 500, textAlign: "center" }}>
                    {selectedPlayer.name}
                  </span>
                </div>
              )}

              <div style={{ flex: 1, minWidth: 180 }}>
                <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "var(--space-6)", marginBottom: "var(--space-6)" }}>
                  <h2 style={{ fontSize: "var(--text-xl)", fontWeight: 300, color: "var(--color-7)", margin: 0 }}>
                    #{selectedPlayer.jersey_number} {selectedPlayer.name}
                  </h2>
                  <span className="rf-badge">{selectedPlayer.team}</span>
                </div>
                <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: "0 0 var(--space-6)" }}>
                  Position:{" "}
                  <strong style={{ color: "var(--color-6)" }}>{selectedPlayer.position}</strong>
                  {" "}| Tracking ID:{" "}
                  <strong style={{ color: "var(--color-6)" }}>#{selectedPlayer.player_id}</strong>
                </p>
                <p
                  style={{
                    fontSize: "var(--text-xs)",
                    color: "var(--color-4)",
                    fontStyle: "italic",
                    background: "rgba(22,16,38,0.6)",
                    border: "1px solid rgba(225,223,220,0.08)",
                    borderRadius: "var(--radius-sm)",
                    padding: "var(--space-6) var(--space-8)",
                    margin: 0,
                    lineHeight: "19.5px",
                  }}
                >
                  "{selectedPlayer.notes || "High tactical work rate and physical engine."}"
                </p>
              </div>

              <div
                style={{
                  background: "rgba(128,51,235,0.12)",
                  border: "1px solid rgba(128,51,235,0.3)",
                  borderRadius: "var(--radius-md)",
                  padding: "var(--space-9) var(--space-10)",
                  textAlign: "center",
                  minWidth: 120,
                }}
              >
                <p style={{ fontSize: 10, color: "var(--color-3)", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.06em", margin: 0 }}>
                  Performance Rating
                </p>
                <p style={{ fontSize: 40, fontWeight: 300, color: "var(--color-3)", margin: "var(--space-4) 0 var(--space-2)" }}>
                  {selectedPlayer.performance_score}
                </p>
                <p style={{ fontSize: 10, color: "var(--color-4)", margin: 0 }}>out of 100</p>
              </div>
            </div>

            {/* Stats Grid */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
                gap: "var(--space-8)",
              }}
            >
              <StatCard
                icon={<Zap style={{ width: 13, height: 13, color: "var(--color-3)" }} />}
                label="Top Sprint Speed"
                value={`${selectedPlayer.maximum_speed_kmh} km/h`}
              />
              <StatCard
                icon={<Activity style={{ width: 13, height: 13, color: "var(--color-3)" }} />}
                label="Total Distance"
                value={`${selectedPlayer.distance_meters} m`}
              />
              <StatCard
                icon={<Target style={{ width: 13, height: 13, color: "var(--color-3)" }} />}
                label="Tackles Won"
                value={`${selectedPlayer.tackles_won}/${selectedPlayer.tackles_attempted} (${selectedPlayer.tackle_success_rate}%)`}
              />
              <StatCard
                icon={<Shield style={{ width: 13, height: 13, color: "var(--color-3)" }} />}
                label="Defensive Rating"
                value={`${selectedPlayer.defensive_rating} / 10`}
              />
            </div>

            {/* AI Insights */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-9)" }}>
              <InsightPanel
                icon={<Flame style={{ width: 15, height: 15, color: "var(--color-3)" }} />}
                title="AI Tactical Insights"
                items={[
                  `• Primary Strength: Excellent sprint acceleration and high defensive tackle success rate (${selectedPlayer.tackle_success_rate}%).`,
                  "• Positioning: Maintains strong midfield spatial discipline and pressing interactions.",
                  "• Coach Advice: Maintain forward pressing intensity during offensive turnover transitions.",
                ]}
              />
              <InsightPanel
                icon={<Apple style={{ width: 15, height: 15, color: "var(--color-3)" }} />}
                title="Post-Match Nutrition & Recovery"
                items={[
                  "• Hydration Target: 1.5L electrolyte recovery solution within 45 mins post match.",
                  "• Carb Intake: 65g complex carbohydrates to replenish glycogen after high sprint distance.",
                  "• Protein Recovery: 30g lean protein for muscle fiber repair.",
                ]}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
