"use client";

import { useState, useEffect } from "react";
import { Users, Save, Upload, Shield, Check, Trash2, Plus, ArrowRight, UserCheck, RefreshCw, Zap, Sparkles } from "lucide-react";

export default function RosterCalibrationPage() {
  const [teamSize, setTeamSize] = useState<string>("5v5");
  const [playersPerTeam, setPlayersPerTeam] = useState<number>(5);
  const [customNum, setCustomNum] = useState<number>(5);

  const [teamA, setTeamA] = useState({
    name: "Team A",
    primary_color: "#E63946",
    secondary_color: "#FFFFFF",
    formation: "2-2-1",
    coach: "",
  });

  const [teamB, setTeamB] = useState({
    name: "Team B",
    primary_color: "#1D3557",
    secondary_color: "#F1FAEE",
    formation: "2-2-1",
    coach: "",
  });

  const [players, setPlayers] = useState<Record<string, any>>({});
  const [activeTeamTab, setActiveTeamTab] = useState<"Team A" | "Team B">("Team A");
  const [selectedSlot, setSelectedSlot] = useState<number>(1);

  // Active form state for the selected member slot
  const [memberForm, setMemberForm] = useState({
    name: "",
    jersey_number: 10,
    position: "Midfielder",
    notes: "",
    photo_path: "",
  });

  const [saving, setSaving] = useState(false);
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [message, setMessage] = useState("");
  const [photoUploading, setPhotoUploading] = useState(false);

  useEffect(() => {
    fetchRoster();
  }, []);

  const fetchRoster = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/roster");
      const data = await res.json();
      if (data) {
        setTeamSize(data.team_size || "5v5");
        setPlayersPerTeam(data.players_per_team || 5);
        if (data.team_a) setTeamA(data.team_a);
        if (data.team_b) setTeamB(data.team_b);
        if (data.players) setPlayers(data.players);
      }
    } catch (err) {
      console.error("Error fetching roster:", err);
    }
  };

  const handleLoadDemo = async () => {
    setLoadingDemo(true);
    try {
      const res = await fetch("http://localhost:8000/api/roster/load-demo", { method: "POST" });
      const data = await res.json();
      if (data && data.config) {
        setTeamSize(data.config.team_size || "5v5");
        setPlayersPerTeam(data.config.players_per_team || 5);
        if (data.config.team_a) setTeamA(data.config.team_a);
        if (data.config.team_b) setTeamB(data.config.team_b);
        if (data.config.players) setPlayers(data.config.players);
        setSelectedSlot(1);
        setMessage("⚡ Portugal vs Spain (5v5) Match Demo Loaded! (Cristiano Ronaldo, Bruno Fernandes, Rodri, Lamine Yamal & all 10 players configured)");
        setTimeout(() => setMessage(""), 5000);
      }
    } catch (err) {
      console.error("Demo load error:", err);
      setMessage("Failed to load demo data. Please verify the backend is running on port 8000.");
      setTimeout(() => setMessage(""), 4000);
    } finally {
      setLoadingDemo(false);
    }
  };

  // Helper to get key for player ID slot (e.g. Team A slot 1 -> "1", slot 2 -> "2", Team B slot 1 -> "6", etc.)
  const getSlotPlayerId = (team: "Team A" | "Team B", slotIndex: number): string => {
    if (team === "Team A") {
      return slotIndex.toString();
    } else {
      return (playersPerTeam + slotIndex).toString();
    }
  };

  // Load slot form data whenever slot or team changes
  useEffect(() => {
    const pid = getSlotPlayerId(activeTeamTab, selectedSlot);
    const existing = players[pid];
    if (existing) {
      setMemberForm({
        name: existing.name || "",
        jersey_number: existing.jersey_number || (activeTeamTab === "Team A" ? selectedSlot : selectedSlot + playersPerTeam),
        position: existing.position || "Midfielder",
        notes: existing.notes || "",
        photo_path: existing.photo_path || "",
      });
    } else {
      setMemberForm({
        name: "",
        jersey_number: activeTeamTab === "Team A" ? selectedSlot : selectedSlot + playersPerTeam,
        position: "Midfielder",
        notes: "",
        photo_path: "",
      });
    }
  }, [activeTeamTab, selectedSlot, playersPerTeam, players]);

  const handleTeamSizeChange = (newSize: string) => {
    setTeamSize(newSize);
    let count = 5;
    if (newSize === "5v5") count = 5;
    else if (newSize === "7v7") count = 7;
    else if (newSize === "11v11") count = 11;
    else if (newSize === "custom") count = customNum;
    setPlayersPerTeam(count);
    setSelectedSlot(1);
  };

  const handleCustomNumChange = (val: number) => {
    const num = Math.max(1, Math.min(25, val));
    setCustomNum(num);
    if (teamSize === "custom") {
      setPlayersPerTeam(num);
    }
  };

  const handleSaveMember = () => {
    const pid = getSlotPlayerId(activeTeamTab, selectedSlot);
    const updatedPlayers = {
      ...players,
      [pid]: {
        name: memberForm.name || `Player #${memberForm.jersey_number}`,
        jersey_number: Number(memberForm.jersey_number) || 1,
        team: activeTeamTab,
        position: memberForm.position,
        notes: memberForm.notes,
        photo_path: memberForm.photo_path,
      },
    };
    setPlayers(updatedPlayers);
    saveFullRoster(updatedPlayers, teamA, teamB, teamSize, playersPerTeam);

    setMessage(`Saved ${activeTeamTab} Member #${selectedSlot} (${memberForm.name || "Player"})`);
    setTimeout(() => setMessage(""), 3000);

    // Auto-advance to next slot if available
    if (selectedSlot < playersPerTeam) {
      setSelectedSlot(selectedSlot + 1);
    }
  };

  const saveFullRoster = async (
    currentPlayers = players,
    cTeamA = teamA,
    cTeamB = teamB,
    cTeamSize = teamSize,
    cPpt = playersPerTeam
  ) => {
    setSaving(true);
    try {
      const payload = {
        team_size: cTeamSize,
        players_per_team: cPpt,
        team_a: cTeamA,
        team_b: cTeamB,
        players: currentPlayers,
      };
      const res = await fetch("http://localhost:8000/api/roster", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setMessage("Team identity & roster calibration saved successfully!");
        setTimeout(() => setMessage(""), 4000);
      }
    } catch (err) {
      console.error("Save error:", err);
    } finally {
      setSaving(false);
    }
  };

  const handleResetAllData = async () => {
    if (!confirm("Are you sure you want to clear all team roster calibration data and start clean?")) return;
    try {
      const res = await fetch("http://localhost:8000/api/roster/reset", { method: "POST" });
      if (res.ok) {
        setPlayers({});
        setTeamA({ name: "Team A", primary_color: "#E63946", secondary_color: "#FFFFFF", formation: "2-2-1", coach: "" });
        setTeamB({ name: "Team B", primary_color: "#1D3557", secondary_color: "#F1FAEE", formation: "2-2-1", coach: "" });
        setTeamSize("5v5");
        setPlayersPerTeam(5);
        setSelectedSlot(1);
        setMessage("All roster calibration data cleared. Ready for new team input.");
        setTimeout(() => setMessage(""), 4000);
      }
    } catch (err) {
      console.error("Reset error:", err);
    }
  };

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    const pid = getSlotPlayerId(activeTeamTab, selectedSlot);
    const formData = new FormData();
    formData.append("file", file);

    setPhotoUploading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/roster/player-photo/${pid}`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.status === "success") {
        setMemberForm({ ...memberForm, photo_path: data.photo_url });
        const updatedPlayers = {
          ...players,
          [pid]: {
            ...players[pid],
            name: memberForm.name || `Player #${memberForm.jersey_number}`,
            jersey_number: Number(memberForm.jersey_number) || 1,
            team: activeTeamTab,
            position: memberForm.position,
            notes: memberForm.notes,
            photo_path: data.photo_url,
          },
        };
        setPlayers(updatedPlayers);
        saveFullRoster(updatedPlayers);
      }
    } catch (err) {
      console.error("Photo upload error:", err);
    } finally {
      setPhotoUploading(false);
    }
  };

  // Count calibrated members per team
  const getCalibratedCount = (team: "Team A" | "Team B") => {
    let count = 0;
    for (let i = 1; i <= playersPerTeam; i++) {
      const pid = getSlotPlayerId(team, i);
      if (players[pid] && players[pid].name) count++;
    }
    return count;
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-11)" }}>
      {/* ── Header Banner ─────────────────────────────────────────── */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "var(--space-8)",
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
            <Shield style={{ width: 28, height: 28, color: "var(--color-3)" }} />
            Team &amp; Player Roster Calibration Studio
          </h1>
          <p
            style={{
              fontSize: "var(--text-xs)",
              color: "var(--color-4)",
              margin: "var(--space-4) 0 0",
              lineHeight: "19.5px",
            }}
          >
            Select team sizes, configure team names &amp; colors, and add each member's photo, jersey number, and position for AI team-by-team detection.
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-6)", flexWrap: "wrap" }}>
          <button
            onClick={handleLoadDemo}
            disabled={loadingDemo}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "var(--space-4)",
              background: "linear-gradient(135deg, rgba(128,51,235,0.9) 0%, rgba(99,102,241,0.9) 100%)",
              color: "#FFFFFF",
              border: "1px solid rgba(128,51,235,0.6)",
              borderRadius: "var(--radius-md)",
              padding: "var(--space-5) var(--space-8)",
              fontSize: "var(--text-xs)",
              fontWeight: 600,
              cursor: loadingDemo ? "not-allowed" : "pointer",
              boxShadow: "0 2px 8px rgba(128,51,235,0.3)",
              transition: "all 0.2s ease",
            }}
          >
            <Zap style={{ width: 14, height: 14 }} />
            {loadingDemo ? "Loading Demo…" : "⚡ Load Portugal vs Spain Demo"}
          </button>

          <button
            onClick={handleResetAllData}
            className="rf-btn-secondary"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "var(--space-4)",
              fontSize: "var(--text-xs)",
              borderColor: "rgba(230,57,70,0.4)",
              color: "#E63946",
            }}
          >
            <Trash2 style={{ width: 14, height: 14 }} />
            Clear Old Data
          </button>

          <button
            onClick={() => saveFullRoster()}
            disabled={saving}
            className="rf-btn-primary"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "var(--space-4)",
              fontSize: "var(--text-xs)",
            }}
          >
            <Save style={{ width: 14, height: 14 }} />
            <span>{saving ? "Saving Roster…" : "Save Team Calibration"}</span>
          </button>
        </div>
      </div>

      {/* ── Demo Preset Quick Action Callout ── */}
      <div
        style={{
          background: "linear-gradient(135deg, rgba(128,51,235,0.14) 0%, rgba(29,53,87,0.18) 100%)",
          border: "1px solid rgba(128,51,235,0.35)",
          borderRadius: "var(--radius-md)",
          padding: "var(--space-7) var(--space-9)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "var(--space-6)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-6)" }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: "50%",
              background: "rgba(128,51,235,0.25)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#a855f7",
            }}
          >
            <Sparkles style={{ width: 20, height: 20 }} />
          </div>
          <div>
            <div style={{ fontSize: "var(--text-xs)", fontWeight: 600, color: "var(--color-7)" }}>
              Presentation Demo Mode Available
            </div>
            <div style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", marginTop: 2 }}>
              1-click pre-populates <strong>Portugal (Red #E63946, 5 Players)</strong> vs <strong>Spain (White #DEDEDE, 5 Players)</strong> with player names, numbers, and tactical positions.
            </div>
          </div>
        </div>

        <button
          onClick={handleLoadDemo}
          disabled={loadingDemo}
          className="rf-btn-secondary"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "var(--space-4)",
            fontSize: "var(--text-xs)",
            borderColor: "rgba(128,51,235,0.5)",
            color: "var(--color-7)",
            background: "rgba(128,51,235,0.15)",
          }}
        >
          <Zap style={{ width: 14, height: 14, color: "#a855f7" }} />
          {loadingDemo ? "Populating Demo…" : "Populate Demo Roster"}
        </button>
      </div>

      {message && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "var(--space-5)",
            background: "rgba(128,51,235,0.12)",
            border: "1px solid rgba(128,51,235,0.35)",
            borderRadius: "var(--radius-sm)",
            padding: "var(--space-6) var(--space-9)",
            fontSize: "var(--text-xs)",
            fontWeight: 500,
            color: "var(--color-3)",
          }}
        >
          <Check style={{ width: 15, height: 15 }} />
          {message}
        </div>
      )}

      {/* ── STEP 1: SELECT TEAM SIZE & TEAM NAMES ─────────────────── */}
      <div className="rf-card" style={{ padding: "var(--space-10)" }}>
        <h3
          style={{
            fontSize: "var(--text-base)",
            fontWeight: 500,
            color: "var(--color-7)",
            margin: "0 0 var(--space-9)",
            display: "flex",
            alignItems: "center",
            gap: "var(--space-5)",
          }}
        >
          <Users style={{ width: 18, height: 18, color: "var(--color-3)" }} />
          Step 1: Select Match Format &amp; Team Configurations
        </h3>

        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-9)" }}>
          {/* Format Selection Buttons */}
          <div>
            <label
              style={{
                display: "block",
                fontSize: "var(--text-xs)",
                fontWeight: 500,
                color: "var(--color-4)",
                textTransform: "uppercase",
                letterSpacing: "0.06em",
                marginBottom: "var(--space-5)",
              }}
            >
              Select Team Size (Players Per Team)
            </label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-6)" }}>
              {[
                { id: "5v5", label: "5 vs 5 (Futsal / Mini)", count: 5 },
                { id: "7v7", label: "7 vs 7 (Junior / Turf)", count: 7 },
                { id: "11v11", label: "11 vs 11 (Full Pitch)", count: 11 },
                { id: "custom", label: "Custom Team Size", count: customNum },
              ].map((fmt) => (
                <button
                  key={fmt.id}
                  onClick={() => handleTeamSizeChange(fmt.id)}
                  style={{
                    padding: "var(--space-6) var(--space-9)",
                    borderRadius: "var(--radius-md)",
                    fontSize: "var(--text-xs)",
                    fontWeight: 500,
                    cursor: "pointer",
                    border: `1px solid ${teamSize === fmt.id ? "rgba(128,51,235,0.5)" : "rgba(225,223,220,0.1)"}`,
                    background: teamSize === fmt.id ? "rgba(128,51,235,0.18)" : "rgba(22,16,38,0.6)",
                    color: teamSize === fmt.id ? "var(--color-7)" : "var(--color-4)",
                    transition: "all 0.3s cubic-bezier(0.2,0,0.2,1)",
                  }}
                >
                  {fmt.label}
                </button>
              ))}
            </div>

            {teamSize === "custom" && (
              <div style={{ marginTop: "var(--space-6)", display: "flex", alignItems: "center", gap: "var(--space-6)" }}>
                <span style={{ fontSize: "var(--text-xs)", color: "var(--color-4)" }}>Number of players per team:</span>
                <input
                  type="number"
                  min="1"
                  max="25"
                  value={customNum}
                  onChange={(e) => handleCustomNumChange(parseInt(e.target.value) || 1)}
                  className="rf-input"
                  style={{ width: 90, padding: "var(--space-3) var(--space-6)" }}
                />
              </div>
            )}
          </div>

          {/* Team 1 & Team 2 Config Grid */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-9)" }}>
            {/* Team A */}
            <div
              style={{
                background: "rgba(230,57,70,0.06)",
                border: "1px solid rgba(230,57,70,0.25)",
                borderRadius: "var(--radius-md)",
                padding: "var(--space-9)",
                display: "flex",
                flexDirection: "column",
                gap: "var(--space-6)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span style={{ fontSize: "var(--text-xs)", fontWeight: 500, color: "#E63946" }}>
                  🔴 Team 1 Configuration
                </span>
                <span style={{ fontSize: 10, color: "var(--color-4)" }}>
                  {getCalibratedCount("Team A")} / {playersPerTeam} Members Added
                </span>
              </div>

              <div>
                <label style={{ display: "block", fontSize: 10, color: "var(--color-4)", marginBottom: 4 }}>
                  TEAM 1 NAME
                </label>
                <input
                  type="text"
                  value={teamA.name}
                  onChange={(e) => setTeamA({ ...teamA, name: e.target.value })}
                  className="rf-input"
                  placeholder="e.g. Red Warriors FC"
                />
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "var(--space-6)" }}>
                <label style={{ fontSize: 10, color: "var(--color-4)" }}>Primary Jersey Color:</label>
                <input
                  type="color"
                  value={teamA.primary_color}
                  onChange={(e) => setTeamA({ ...teamA, primary_color: e.target.value })}
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid rgba(225,223,220,0.15)",
                    background: "transparent",
                    cursor: "pointer",
                  }}
                />
                <span style={{ fontSize: "var(--text-xs)", fontFamily: "var(--font-mono)", color: "var(--color-3)" }}>
                  {teamA.primary_color}
                </span>
              </div>
            </div>

            {/* Team B */}
            <div
              style={{
                background: "rgba(29,53,87,0.15)",
                border: "1px solid rgba(59,130,246,0.25)",
                borderRadius: "var(--radius-md)",
                padding: "var(--space-9)",
                display: "flex",
                flexDirection: "column",
                gap: "var(--space-6)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span style={{ fontSize: "var(--text-xs)", fontWeight: 500, color: "#3B82F6" }}>
                  🔵 Team 2 Configuration
                </span>
                <span style={{ fontSize: 10, color: "var(--color-4)" }}>
                  {getCalibratedCount("Team B")} / {playersPerTeam} Members Added
                </span>
              </div>

              <div>
                <label style={{ display: "block", fontSize: 10, color: "var(--color-4)", marginBottom: 4 }}>
                  TEAM 2 NAME
                </label>
                <input
                  type="text"
                  value={teamB.name}
                  onChange={(e) => setTeamB({ ...teamB, name: e.target.value })}
                  className="rf-input"
                  placeholder="e.g. Blue Strikers FC"
                />
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "var(--space-6)" }}>
                <label style={{ fontSize: 10, color: "var(--color-4)" }}>Primary Jersey Color:</label>
                <input
                  type="color"
                  value={teamB.primary_color}
                  onChange={(e) => setTeamB({ ...teamB, primary_color: e.target.value })}
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid rgba(225,223,220,0.15)",
                    background: "transparent",
                    cursor: "pointer",
                  }}
                />
                <span style={{ fontSize: "var(--text-xs)", fontFamily: "var(--font-mono)", color: "var(--color-3)" }}>
                  {teamB.primary_color}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── STEP 2: MEMBER-BY-MEMBER PHOTO & JERSEY CALIBRATION ─────── */}
      <div className="rf-card" style={{ padding: "var(--space-10)" }}>
        <h3
          style={{
            fontSize: "var(--text-base)",
            fontWeight: 500,
            color: "var(--color-7)",
            margin: "0 0 var(--space-9)",
            display: "flex",
            alignItems: "center",
            gap: "var(--space-5)",
          }}
        >
          <UserCheck style={{ width: 18, height: 18, color: "var(--color-3)" }} />
          Step 2: Calibrate Each Team Member (Photo, Jersey # &amp; Identity)
        </h3>

        {/* Team Selector Tabs */}
        <div style={{ display: "flex", gap: "var(--space-6)", marginBottom: "var(--space-9)" }}>
          <button
            onClick={() => {
              setActiveTeamTab("Team A");
              setSelectedSlot(1);
            }}
            style={{
              padding: "var(--space-6) var(--space-10)",
              borderRadius: "var(--radius-md)",
              fontSize: "var(--text-sm)",
              fontWeight: 500,
              cursor: "pointer",
              border: `1px solid ${activeTeamTab === "Team A" ? "rgba(230,57,70,0.5)" : "rgba(225,223,220,0.1)"}`,
              background: activeTeamTab === "Team A" ? "rgba(230,57,70,0.15)" : "rgba(22,16,38,0.6)",
              color: activeTeamTab === "Team A" ? "#E63946" : "var(--color-4)",
              display: "flex",
              alignItems: "center",
              gap: "var(--space-5)",
            }}
          >
            <span>🔴 {teamA.name || "Team 1"}</span>
            <span style={{ fontSize: 10, opacity: 0.8 }}>({getCalibratedCount("Team A")}/{playersPerTeam})</span>
          </button>

          <button
            onClick={() => {
              setActiveTeamTab("Team B");
              setSelectedSlot(1);
            }}
            style={{
              padding: "var(--space-6) var(--space-10)",
              borderRadius: "var(--radius-md)",
              fontSize: "var(--text-sm)",
              fontWeight: 500,
              cursor: "pointer",
              border: `1px solid ${activeTeamTab === "Team B" ? "rgba(59,130,246,0.5)" : "rgba(225,223,220,0.1)"}`,
              background: activeTeamTab === "Team B" ? "rgba(59,130,246,0.15)" : "rgba(22,16,38,0.6)",
              color: activeTeamTab === "Team B" ? "#3B82F6" : "var(--color-4)",
              display: "flex",
              alignItems: "center",
              gap: "var(--space-5)",
            }}
          >
            <span>🔵 {teamB.name || "Team 2"}</span>
            <span style={{ fontSize: 10, opacity: 0.8 }}>({getCalibratedCount("Team B")}/{playersPerTeam})</span>
          </button>
        </div>

        {/* Layout: Member Slots (Left) + Member Editor (Right) */}
        <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: "var(--space-10)" }}>
          {/* Slot Picker List */}
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
            <p
              style={{
                fontSize: 10,
                fontWeight: 500,
                color: "var(--color-4)",
                textTransform: "uppercase",
                letterSpacing: "0.06em",
                margin: "0 0 var(--space-2)",
              }}
            >
              Select Slot (Member 1 to {playersPerTeam})
            </p>

            {Array.from({ length: playersPerTeam }, (_, idx) => idx + 1).map((slotNum) => {
              const pid = getSlotPlayerId(activeTeamTab, slotNum);
              const isCalibrated = Boolean(players[pid] && players[pid].name);
              const isSelected = selectedSlot === slotNum;
              const pData = players[pid];

              return (
                <button
                  key={slotNum}
                  onClick={() => setSelectedSlot(slotNum)}
                  style={{
                    width: "100%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "var(--space-5) var(--space-8)",
                    borderRadius: "var(--radius-sm)",
                    border: `1px solid ${isSelected ? "rgba(128,51,235,0.5)" : "rgba(225,223,220,0.08)"}`,
                    background: isSelected
                      ? "rgba(128,51,235,0.18)"
                      : isCalibrated
                      ? "rgba(128,51,235,0.06)"
                      : "rgba(22,16,38,0.4)",
                    color: isSelected ? "var(--color-7)" : isCalibrated ? "var(--color-3)" : "var(--color-4)",
                    textAlign: "left",
                    cursor: "pointer",
                    fontSize: "var(--text-xs)",
                    transition: "all 0.3s cubic-bezier(0.2,0,0.2,1)",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "var(--space-4)" }}>
                    <span style={{ fontWeight: 500, fontFamily: "var(--font-mono)" }}>#{slotNum}</span>
                    <span style={{ fontWeight: isSelected ? 500 : 400 }}>
                      {pData?.name ? pData.name : `Member ${slotNum}`}
                    </span>
                  </div>
                  {isCalibrated ? (
                    <Check style={{ width: 13, height: 13, color: "var(--color-3)" }} />
                  ) : (
                    <span style={{ fontSize: 10, color: "var(--color-4)" }}>Empty</span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Member Editor Box */}
          <div
            style={{
              background: "rgba(22,16,38,0.8)",
              border: "1px solid rgba(225,223,220,0.12)",
              borderRadius: "var(--radius-md)",
              padding: "var(--space-10)",
              display: "flex",
              flexDirection: "column",
              gap: "var(--space-9)",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                borderBottom: "1px solid rgba(225,223,220,0.1)",
                paddingBottom: "var(--space-6)",
              }}
            >
              <h4 style={{ fontSize: "var(--text-base)", fontWeight: 500, color: "var(--color-7)", margin: 0 }}>
                Calibrating {activeTeamTab === "Team A" ? teamA.name : teamB.name} — Member #{selectedSlot}
              </h4>
              <span className="rf-badge">
                ID #{getSlotPlayerId(activeTeamTab, selectedSlot)}
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "180px 1fr", gap: "var(--space-10)" }}>
              {/* Photo Upload & Jersey Preview */}
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "var(--space-6)" }}>
                {memberForm.photo_path ? (
                  <div
                    style={{
                      width: 150,
                      height: 180,
                      borderRadius: "var(--radius-md)",
                      overflow: "hidden",
                      border: "2px solid rgba(128,51,235,0.4)",
                      boxShadow: "0 0 20px rgba(128,51,235,0.2)",
                    }}
                  >
                    <img
                      src={`http://localhost:8000${memberForm.photo_path}`}
                      alt={memberForm.name || "Member"}
                      style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                  </div>
                ) : (
                  <div
                    style={{
                      width: 150,
                      height: 180,
                      borderRadius: "var(--radius-md)",
                      padding: "var(--space-8)",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "#fff",
                      border: "2px solid rgba(255,255,255,0.15)",
                      backgroundColor:
                        activeTeamTab === "Team A" ? teamA.primary_color : teamB.primary_color,
                    }}
                  >
                    <span style={{ fontSize: 10, textTransform: "uppercase", fontWeight: 500, opacity: 0.8 }}>
                      {activeTeamTab === "Team A" ? teamA.name : teamB.name}
                    </span>
                    <span style={{ fontSize: 48, fontWeight: 300, margin: "var(--space-2) 0", lineHeight: 1 }}>
                      #{memberForm.jersey_number || selectedSlot}
                    </span>
                    <span style={{ fontSize: "var(--text-xs)", fontWeight: 500, textAlign: "center" }}>
                      {memberForm.name || `Member #${selectedSlot}`}
                    </span>
                  </div>
                )}

                <label
                  className="rf-btn-secondary"
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "var(--space-4)",
                    cursor: "pointer",
                    width: "100%",
                    fontSize: "var(--text-xs)",
                    padding: "var(--space-5)",
                  }}
                >
                  <Upload style={{ width: 13, height: 13, color: "var(--color-3)" }} />
                  <span>{photoUploading ? "Uploading…" : "Add Member Photo"}</span>
                  <input type="file" accept="image/*" onChange={handlePhotoUpload} style={{ display: "none" }} />
                </label>
              </div>

              {/* Form Input Fields */}
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-8)" }}>
                <div>
                  <label
                    style={{
                      display: "block",
                      fontSize: "var(--text-xs)",
                      fontWeight: 500,
                      color: "var(--color-4)",
                      marginBottom: "var(--space-3)",
                    }}
                  >
                    MEMBER FULL NAME *
                  </label>
                  <input
                    type="text"
                    value={memberForm.name}
                    onChange={(e) => setMemberForm({ ...memberForm, name: e.target.value })}
                    className="rf-input"
                    placeholder="e.g. Kamalesh"
                  />
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-6)" }}>
                  <div>
                    <label
                      style={{
                        display: "block",
                        fontSize: "var(--text-xs)",
                        fontWeight: 500,
                        color: "var(--color-4)",
                        marginBottom: "var(--space-3)",
                      }}
                    >
                      JERSEY NUMBER *
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="99"
                      value={memberForm.jersey_number}
                      onChange={(e) =>
                        setMemberForm({
                          ...memberForm,
                          jersey_number: parseInt(e.target.value) || 1,
                        })
                      }
                      className="rf-input"
                    />
                  </div>

                  <div>
                    <label
                      style={{
                        display: "block",
                        fontSize: "var(--text-xs)",
                        fontWeight: 500,
                        color: "var(--color-4)",
                        marginBottom: "var(--space-3)",
                      }}
                    >
                      PLAYING POSITION *
                    </label>
                    <select
                      value={memberForm.position}
                      onChange={(e) => setMemberForm({ ...memberForm, position: e.target.value })}
                      className="rf-input"
                    >
                      {[
                        "Attacking Midfielder",
                        "Forward / Winger",
                        "Striker",
                        "Center Forward",
                        "Central Midfielder",
                        "Defensive Midfielder",
                        "Left Back",
                        "Right Back",
                        "Center Back",
                        "Goalkeeper",
                      ].map((pos) => (
                        <option key={pos} value={pos}>
                          {pos}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label
                    style={{
                      display: "block",
                      fontSize: "var(--text-xs)",
                      fontWeight: 500,
                      color: "var(--color-4)",
                      marginBottom: "var(--space-3)",
                    }}
                  >
                    TACTICAL NOTES (OPTIONAL)
                  </label>
                  <input
                    type="text"
                    value={memberForm.notes}
                    onChange={(e) => setMemberForm({ ...memberForm, notes: e.target.value })}
                    className="rf-input"
                    placeholder="e.g. Team Captain, Fast Sprinter, Penalty Taker"
                  />
                </div>

                <button
                  onClick={handleSaveMember}
                  className="rf-btn-primary"
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "var(--space-5)",
                    padding: "var(--space-8)",
                    marginTop: "var(--space-4)",
                  }}
                >
                  <Save style={{ width: 15, height: 15 }} />
                  <span>
                    Save {activeTeamTab === "Team A" ? teamA.name : teamB.name} Member #{selectedSlot}
                  </span>
                  <ArrowRight style={{ width: 14, height: 14 }} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── STEP 3: FULL TEAM ROSTER SUMMARY PREVIEW ───────────────── */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-10)" }}>
        {/* Team A Roster Summary */}
        <div className="rf-card" style={{ padding: "var(--space-9)" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              borderBottom: "1px solid rgba(225,223,220,0.1)",
              paddingBottom: "var(--space-6)",
              marginBottom: "var(--space-6)",
            }}
          >
            <h4 style={{ fontSize: "var(--text-sm)", fontWeight: 500, color: "#E63946", margin: 0 }}>
              🔴 {teamA.name || "Team 1"} Roster ({getCalibratedCount("Team A")}/{playersPerTeam} Members)
            </h4>
            <span className="rf-badge">{teamA.primary_color}</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
            {Array.from({ length: playersPerTeam }, (_, idx) => idx + 1).map((sNum) => {
              const pid = getSlotPlayerId("Team A", sNum);
              const p = players[pid];
              return (
                <div
                  key={pid}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "var(--space-5) var(--space-8)",
                    borderRadius: "var(--radius-sm)",
                    background: "rgba(22,16,38,0.5)",
                    border: "1px solid rgba(225,223,220,0.06)",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "var(--space-6)" }}>
                    <div
                      style={{
                        width: 28,
                        height: 28,
                        borderRadius: "var(--radius-sm)",
                        background: teamA.primary_color,
                        color: "#fff",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "var(--text-xs)",
                        fontWeight: 500,
                      }}
                    >
                      #{p?.jersey_number || sNum}
                    </div>
                    <div>
                      <p style={{ fontSize: "var(--text-xs)", fontWeight: 500, color: "var(--color-6)", margin: 0 }}>
                        {p?.name ? p.name : `Unregistered Member #${sNum}`}
                      </p>
                      <p style={{ fontSize: 10, color: "var(--color-4)", margin: 0 }}>
                        {p?.position || "Position not set"}
                      </p>
                    </div>
                  </div>
                  {p?.name ? (
                    <span className="rf-badge">Calibrated</span>
                  ) : (
                    <span style={{ fontSize: 10, color: "var(--color-4)" }}>Pending</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Team B Roster Summary */}
        <div className="rf-card" style={{ padding: "var(--space-9)" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              borderBottom: "1px solid rgba(225,223,220,0.1)",
              paddingBottom: "var(--space-6)",
              marginBottom: "var(--space-6)",
            }}
          >
            <h4 style={{ fontSize: "var(--text-sm)", fontWeight: 500, color: "#3B82F6", margin: 0 }}>
              🔵 {teamB.name || "Team 2"} Roster ({getCalibratedCount("Team B")}/{playersPerTeam} Members)
            </h4>
            <span className="rf-badge">{teamB.primary_color}</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
            {Array.from({ length: playersPerTeam }, (_, idx) => idx + 1).map((sNum) => {
              const pid = getSlotPlayerId("Team B", sNum);
              const p = players[pid];
              return (
                <div
                  key={pid}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "var(--space-5) var(--space-8)",
                    borderRadius: "var(--radius-sm)",
                    background: "rgba(22,16,38,0.5)",
                    border: "1px solid rgba(225,223,220,0.06)",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "var(--space-6)" }}>
                    <div
                      style={{
                        width: 28,
                        height: 28,
                        borderRadius: "var(--radius-sm)",
                        background: teamB.primary_color,
                        color: "#fff",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "var(--text-xs)",
                        fontWeight: 500,
                      }}
                    >
                      #{p?.jersey_number || (sNum + playersPerTeam)}
                    </div>
                    <div>
                      <p style={{ fontSize: "var(--text-xs)", fontWeight: 500, color: "var(--color-6)", margin: 0 }}>
                        {p?.name ? p.name : `Unregistered Member #${sNum}`}
                      </p>
                      <p style={{ fontSize: 10, color: "var(--color-4)", margin: 0 }}>
                        {p?.position || "Position not set"}
                      </p>
                    </div>
                  </div>
                  {p?.name ? (
                    <span className="rf-badge">Calibrated</span>
                  ) : (
                    <span style={{ fontSize: 10, color: "var(--color-4)" }}>Pending</span>
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
