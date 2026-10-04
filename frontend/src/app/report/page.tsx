"use client";

import { useEffect, useState } from "react";
import { FileText, Trophy, Zap, Target } from "lucide-react";

function SummaryCard({
  label,
  value,
  note,
  valueColor,
}: {
  label: string;
  value: string;
  note: string;
  valueColor?: string;
}) {
  return (
    <div className="rf-card" style={{ padding: "var(--space-10)" }}>
      <span
        style={{
          fontSize: "var(--text-xs)",
          fontWeight: 500,
          color: "var(--color-4)",
          textTransform: "uppercase",
          letterSpacing: "0.07em",
          display: "block",
          marginBottom: "var(--space-6)",
        }}
      >
        {label}
      </span>
      <p
        style={{
          fontSize: "var(--text-lg)",
          fontWeight: 300,
          color: valueColor || "var(--color-3)",
          margin: "0 0 var(--space-4)",
          lineHeight: 1.2,
        }}
      >
        {value}
      </p>
      <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0 }}>{note}</p>
    </div>
  );
}

export default function MatchReportPage() {
  const [report, setReport] = useState<any>(null);
  const [players, setPlayers] = useState<any[]>([]);

  useEffect(() => {
    async function fetchData() {
      try {
        const [rRes, pRes] = await Promise.all([
          fetch("http://localhost:8000/api/match-report"),
          fetch("http://localhost:8000/api/players"),
        ]);
        setReport(await rRes.json());
        const pData = await pRes.json();
        setPlayers(pData.players || []);
      } catch (err) {
        console.error("Match report fetch error:", err);
      }
    }
    fetchData();
  }, []);

  const sortedRankings = [...players].sort(
    (a, b) => b.performance_score - a.performance_score
  );

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
          <FileText style={{ width: 28, height: 28, color: "var(--color-3)" }} />
          Automated Match Executive Report &amp; Rankings
        </h1>
        <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: "var(--space-4) 0 0", lineHeight: "19.5px" }}>
          Full match tactical overview, top player rankings, team work-rate metrics, and defensive
          tackle summaries.
        </p>
      </div>

      {/* Summary Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "var(--space-9)" }}>
        <SummaryCard
          label="Match top sprinter"
          value={
            sortedRankings.length > 0
              ? `#${sortedRankings[0].jersey_number} ${sortedRankings[0].name}`
              : "Kamalesh"
          }
          note={`Top Speed: ${sortedRankings.length > 0 ? `${sortedRankings[0].maximum_speed_kmh} km/h` : "28.4 km/h"}`}
        />
        <SummaryCard
          label="Top defensive tackler"
          value={
            sortedRankings.length > 0
              ? `#${sortedRankings[0].jersey_number} ${sortedRankings[0].name}`
              : "Alexander"
          }
          note={`Tackles Won: ${sortedRankings.length > 0 ? `${sortedRankings[0].tackles_won}/${sortedRankings[0].tackles_attempted} (${sortedRankings[0].tackle_success_rate}%)` : "5/6"}`}
        />
        <SummaryCard
          label="Match MVP"
          value={
            sortedRankings.length > 0
              ? `#${sortedRankings[0].jersey_number} ${sortedRankings[0].name}`
              : "Kamalesh"
          }
          note={`Performance Score: ${sortedRankings.length > 0 ? `${sortedRankings[0].performance_score} / 100` : "92.4"}`}
          valueColor="var(--color-3)"
        />
      </div>

      {/* Rankings Table */}
      <div className="rf-card" style={{ overflow: "hidden" }}>
        <div
          style={{
            padding: "var(--space-10)",
            borderBottom: "1px solid rgba(225,223,220,0.1)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
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
              gap: "var(--space-5)",
            }}
          >
            <Trophy style={{ width: 18, height: 18, color: "var(--color-3)" }} />
            Complete match player leaderboard &amp; rankings
          </h3>
          <span style={{ fontSize: "var(--text-xs)", color: "var(--color-4)" }}>
            Sorted by performance score
          </span>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              fontSize: "var(--text-xs)",
              color: "var(--color-4)",
            }}
          >
            <thead>
              <tr
                style={{
                  background: "rgba(22,16,38,0.8)",
                  borderBottom: "1px solid rgba(225,223,220,0.1)",
                }}
              >
                {["Rank", "Player", "Team", "Position", "Top Speed", "Tackles Won", "Distance", "Performance Score"].map(
                  (h) => (
                    <th
                      key={h}
                      style={{
                        padding: "var(--space-8) var(--space-9)",
                        textAlign: h === "Performance Score" ? "right" : "left",
                        fontSize: 10,
                        fontWeight: 500,
                        color: "var(--color-4)",
                        textTransform: "uppercase",
                        letterSpacing: "0.07em",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {h}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody>
              {sortedRankings.map((p, idx) => (
                <tr
                  key={p.player_id}
                  style={{
                    borderBottom: "1px solid rgba(225,223,220,0.05)",
                    transition: "background-color 0.3s cubic-bezier(0.2,0,0.2,1)",
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLElement).style.background = "rgba(128,51,235,0.06)";
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLElement).style.background = "transparent";
                  }}
                >
                  <td
                    style={{
                      padding: "var(--space-8) var(--space-9)",
                      fontWeight: 500,
                      color: "var(--color-3)",
                      fontFamily: "var(--font-mono)",
                    }}
                  >
                    #{idx + 1}
                  </td>
                  <td
                    style={{
                      padding: "var(--space-8) var(--space-9)",
                      fontWeight: 500,
                      color: "var(--color-6)",
                      whiteSpace: "nowrap",
                    }}
                  >
                    #{p.jersey_number} {p.name}
                  </td>
                  <td style={{ padding: "var(--space-8) var(--space-9)" }}>{p.team}</td>
                  <td style={{ padding: "var(--space-8) var(--space-9)", color: "var(--color-4)" }}>
                    {p.position}
                  </td>
                  <td
                    style={{
                      padding: "var(--space-8) var(--space-9)",
                      fontWeight: 500,
                      color: "var(--color-3)",
                    }}
                  >
                    {p.maximum_speed_kmh} km/h
                  </td>
                  <td
                    style={{
                      padding: "var(--space-8) var(--space-9)",
                      fontWeight: 500,
                      color: "var(--color-3)",
                    }}
                  >
                    {p.tackles_won}/{p.tackles_attempted} ({p.tackle_success_rate}%)
                  </td>
                  <td style={{ padding: "var(--space-8) var(--space-9)" }}>
                    {p.distance_meters} m
                  </td>
                  <td
                    style={{
                      padding: "var(--space-8) var(--space-9)",
                      textAlign: "right",
                      fontWeight: 500,
                      fontSize: "var(--text-sm)",
                      color: "var(--color-3)",
                      fontFamily: "var(--font-mono)",
                    }}
                  >
                    {p.performance_score}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
