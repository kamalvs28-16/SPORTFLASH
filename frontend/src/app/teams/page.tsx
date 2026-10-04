"use client";

import { useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";

function TeamCard({
  title,
  emoji,
  colorHex,
  players,
}: {
  title: string;
  emoji: string;
  colorHex: string;
  players: any[];
}) {
  return (
    <div
      className="rf-card"
      style={{ padding: "var(--space-10)", display: "flex", flexDirection: "column", gap: "var(--space-9)" }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: "1px solid rgba(225,223,220,0.1)",
          paddingBottom: "var(--space-9)",
        }}
      >
        <h3
          style={{
            fontSize: "var(--text-base)",
            fontWeight: 500,
            color: "var(--color-7)",
            margin: 0,
            display: "flex",
            alignItems: "center",
            gap: "var(--space-6)",
          }}
        >
          {emoji} {title} ({players.length} Players)
        </h3>
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "var(--text-xs)",
            background: "rgba(22,16,38,0.7)",
            border: "1px solid rgba(225,223,220,0.1)",
            borderRadius: "var(--radius-sm)",
            padding: "var(--space-3) var(--space-6)",
            color: "var(--color-4)",
          }}
        >
          {colorHex}
        </span>
      </div>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "var(--space-5)",
          maxHeight: 420,
          overflowY: "auto",
        }}
      >
        {players.map((p) => (
          <div
            key={p.player_id}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "var(--space-7) var(--space-8)",
              borderRadius: "var(--radius-sm)",
              background: "rgba(22,16,38,0.5)",
              border: "1px solid rgba(225,223,220,0.06)",
              transition: "border-color 0.3s cubic-bezier(0.2,0,0.2,1)",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = "rgba(128,51,235,0.25)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = "rgba(225,223,220,0.06)";
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "var(--space-8)" }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: "var(--radius-sm)",
                  backgroundColor: colorHex,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "var(--text-xs)",
                  fontWeight: 500,
                  color: "#fff",
                  border: "1px solid rgba(255,255,255,0.15)",
                }}
              >
                #{p.jersey_number}
              </div>
              <div>
                <p style={{ fontSize: "var(--text-xs)", fontWeight: 500, color: "var(--color-6)", margin: 0 }}>
                  {p.name}
                </p>
                <p style={{ fontSize: 10, color: "var(--color-4)", margin: 0 }}>{p.position}</p>
              </div>
            </div>
            <div style={{ textAlign: "right" }}>
              <p style={{ fontSize: "var(--text-xs)", fontWeight: 500, color: "var(--color-3)", margin: 0 }}>
                {p.performance_score} Score
              </p>
              <p style={{ fontSize: 10, color: "var(--color-4)", margin: 0 }}>
                {p.maximum_speed_kmh} km/h
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function TeamsPage() {
  const [data, setData] = useState<any>(null);
  const [players, setPlayers] = useState<any[]>([]);

  useEffect(() => {
    async function fetchData() {
      try {
        const [tRes, pRes] = await Promise.all([
          fetch("http://localhost:8000/api/team-classification"),
          fetch("http://localhost:8000/api/players"),
        ]);
        setData(await tRes.json());
        const pData = await pRes.json();
        setPlayers(pData.players || []);
      } catch (err) {
        console.error("Team classification fetch error:", err);
      }
    }
    fetchData();
  }, []);

  const teamAPlayers = players.filter((p) => p.team === "Team A");
  const teamBPlayers = players.filter((p) => p.team === "Team B");

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-11)" }}>
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
          <ShieldCheck style={{ width: 28, height: 28, color: "var(--color-3)" }} />
          Team Classification &amp; Positional Heatmaps
        </h1>
        <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: "var(--space-4) 0 0", lineHeight: "19.5px" }}>
          HSV Upper-Torso Jersey Color Clustering using K-Means separating players into Team A and Team B.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-11)" }}>
        <TeamCard
          title="Team A Roster"
          emoji="🔴"
          colorHex="#E63946"
          players={teamAPlayers}
        />
        <TeamCard
          title="Team B Roster"
          emoji="🔵"
          colorHex="#1D3557"
          players={teamBPlayers}
        />
      </div>
    </div>
  );
}
