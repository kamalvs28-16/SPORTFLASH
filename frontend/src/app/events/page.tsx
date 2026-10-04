"use client";

import { useEffect, useState } from "react";
import { Target, Zap, Activity } from "lucide-react";

export default function EventsPage() {
  const [eventsData, setEventsData] = useState<any>(null);
  const [players, setPlayers] = useState<any[]>([]);

  useEffect(() => {
    async function fetchData() {
      try {
        const [eRes, pRes] = await Promise.all([
          fetch("http://localhost:8000/api/events"),
          fetch("http://localhost:8000/api/players"),
        ]);
        setEventsData(await eRes.json());
        const pData = await pRes.json();
        setPlayers(pData.players || []);
      } catch (err) {
        console.error("Events fetch error:", err);
      }
    }
    fetchData();
  }, []);

  const getPlayerName = (pid: number | string) => {
    const p = players.find((pl) => pl.player_id === pid.toString());
    return p ? `#${p.jersey_number} ${p.name}` : `Player ${pid}`;
  };

  const eventsList = eventsData?.events || [];

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
          <Target style={{ width: 28, height: 28, color: "var(--color-3)" }} />
          Event Detection &amp; Match Timeline Analysis
        </h1>
        <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: "var(--space-4) 0 0", lineHeight: "19.5px" }}>
          Automated event classification: High-speed sprints (&gt;25 km/h), defensive tackles, duels, and movement periods.
        </p>
      </div>

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
          <h3
            style={{
              fontSize: "var(--text-base)",
              fontWeight: 500,
              color: "var(--color-7)",
              margin: 0,
            }}
          >
            Detected match events ({eventsList.length})
          </h3>
          <span className="rf-badge">Real-time frame detection</span>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
            gap: "var(--space-8)",
          }}
        >
          {eventsList.map((evt: any, idx: number) => {
            const isSprint = evt.event_type === "potential_sprint";
            return (
              <div
                key={idx}
                style={{
                  padding: "var(--space-9)",
                  borderRadius: "var(--radius-md)",
                  border: `1px solid ${isSprint ? "rgba(194,154,246,0.25)" : "rgba(225,223,220,0.08)"}`,
                  background: isSprint
                    ? "rgba(128,51,235,0.08)"
                    : "rgba(22,16,38,0.6)",
                  display: "flex",
                  flexDirection: "column",
                  gap: "var(--space-5)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span
                    style={{
                      fontSize: "var(--text-xs)",
                      fontWeight: 500,
                      color: isSprint ? "var(--color-3)" : "var(--color-4)",
                      textTransform: "uppercase",
                      letterSpacing: "0.06em",
                      display: "flex",
                      alignItems: "center",
                      gap: "var(--space-4)",
                    }}
                  >
                    {isSprint ? (
                      <Zap style={{ width: 14, height: 14 }} />
                    ) : (
                      <Activity style={{ width: 14, height: 14 }} />
                    )}
                    {evt.event_type.replace(/_/g, " ")}
                  </span>
                  <span
                    style={{
                      fontSize: 10,
                      fontWeight: 500,
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                      padding: "2px 8px",
                      borderRadius: "var(--radius-sm)",
                      background: "rgba(22,16,38,0.8)",
                      border: "1px solid rgba(225,223,220,0.08)",
                      color: "var(--color-4)",
                    }}
                  >
                    {evt.severity || "medium"}
                  </span>
                </div>
                <p style={{ fontSize: "var(--text-sm)", fontWeight: 500, color: "var(--color-6)", margin: 0 }}>
                  {getPlayerName(evt.player_id)}
                </p>
                <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0, lineHeight: "19.5px" }}>
                  {evt.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
