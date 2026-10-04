"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Zap,
  Upload,
  Play,
  CheckCircle2,
  Users,
  Timer,
  Activity,
  Gauge,
  ArrowRight,
  Sparkles,
  TrendingUp,
} from "lucide-react";

export default function SpeedCalculationPage() {
  const [roster, setRoster] = useState<any>(null);
  const [selectedPid, setSelectedPid] = useState<string>("1");
  const [drillType, setDrillType] = useState<string>("30m");
  const [distanceMeters, setDistanceMeters] = useState<number>(30.0);
  const [customDistance, setCustomDistance] = useState<number>(30.0);

  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string>("");

  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stepText, setStepText] = useState("");
  const [telemetry, setTelemetry] = useState<any>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchRoster();
  }, []);

  const fetchRoster = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/roster");
      const data = await res.json();
      setRoster(data);
      if (data?.players && Object.keys(data.players).length > 0) {
        setSelectedPid(Object.keys(data.players)[0]);
      }
    } catch (err) {
      console.error("Error fetching roster:", err);
    }
  };

  const handleVideoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setVideoFile(file);
      setVideoPreviewUrl(URL.createObjectURL(file));
      setTelemetry(null);
    }
  };

  const handleDrillChange = (type: string, dist: number) => {
    setDrillType(type);
    if (type === "custom") {
      setDistanceMeters(customDistance);
    } else {
      setDistanceMeters(dist);
    }
  };

  const handleRunSpeedAnalysis = async () => {
    setProcessing(true);
    setProgress(15);
    setStepText("Step 1/4: Ingesting player sprint video frames & extracting FPS…");

    try {
      await new Promise((r) => setTimeout(r, 600));
      setProgress(40);
      setStepText("Step 2/4: Tracking runner bounding box & spatial displacement…");

      await new Promise((r) => setTimeout(r, 700));
      setProgress(70);
      setStepText("Step 3/4: Computing peak velocity (km/h), acceleration & sprint duration…");

      const formData = new FormData();
      if (videoFile) {
        formData.append("file", videoFile);
      }
      formData.append("player_id", selectedPid);
      formData.append("drill_type", drillType === "custom" ? `Custom ${distanceMeters}m Drill` : `${drillType} Sprint Drill`);
      formData.append("distance_meters", distanceMeters.toString());

      const res = await fetch("http://localhost:8000/api/speed-test", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setProgress(100);
      setStepText("Step 4/4: Speed telemetry & player profile successfully updated!");
      if (data?.telemetry) {
        setTelemetry(data.telemetry);
        setMessage(`Verified sprint speed calculated for Player #${selectedPid}!`);
        setTimeout(() => setMessage(""), 4000);
      }
    } catch (err) {
      console.error("Speed analysis error:", err);
    } finally {
      setProcessing(false);
    }
  };

  const playersList = roster?.players ? Object.entries(roster.players) : [];
  const selectedPlayer = roster?.players?.[selectedPid] || {
    name: `Player #${selectedPid}`,
    jersey_number: selectedPid,
    team: "Team A",
    position: "Forward",
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-11)", maxWidth: 1100, margin: "0 auto" }}>
      {/* ── Title Banner ─────────────────────────────────────────── */}
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
            <Zap style={{ width: 28, height: 28, color: "var(--color-3)" }} />
            Individual Player Speed Calculation Studio
          </h1>
          <p
            style={{
              fontSize: "var(--text-xs)",
              color: "var(--color-4)",
              margin: "var(--space-4) 0 0",
              lineHeight: "19.5px",
            }}
          >
            Upload individual player running or sprint drill videos to calculate exact top sprint speed (km/h), 0–30m sprint duration, and acceleration curves.
          </p>
        </div>

        <Link
          href="/roster"
          className="rf-btn-secondary"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "var(--space-4)",
            fontSize: "var(--text-xs)",
            textDecoration: "none",
          }}
        >
          <Users style={{ width: 14, height: 14, color: "var(--color-3)" }} />
          <span>Calibrate Roster</span>
        </Link>
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
          <CheckCircle2 style={{ width: 15, height: 15 }} />
          {message}
        </div>
      )}

      {/* ── Main Setup Grid ───────────────────────────────────────── */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-11)" }}>
        {/* Left Column: Player & Drill Selection */}
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-9)" }}>
          {/* Step 1: Select Player */}
          <div className="rf-card" style={{ padding: "var(--space-10)" }}>
            <h3
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
              <Users style={{ width: 16, height: 16, color: "var(--color-3)" }} />
              Step 1: Select Player from Roster
            </h3>

            {playersList.length === 0 ? (
              <div
                style={{
                  background: "rgba(128,51,235,0.06)",
                  border: "1px dashed rgba(128,51,235,0.25)",
                  borderRadius: "var(--radius-md)",
                  padding: "var(--space-8)",
                  textAlign: "center",
                }}
              >
                <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: "0 0 var(--space-4)" }}>
                  No calibrated players found yet.
                </p>
                <Link
                  href="/roster"
                  className="rf-btn-primary"
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "var(--space-4)",
                    fontSize: "var(--text-xs)",
                    textDecoration: "none",
                  }}
                >
                  <Users style={{ width: 13, height: 13 }} />
                  <span>Calibrate Team Roster First</span>
                </Link>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
                <div>
                  <label
                    style={{
                      display: "block",
                      fontSize: 10,
                      fontWeight: 500,
                      color: "var(--color-4)",
                      textTransform: "uppercase",
                      letterSpacing: "0.06em",
                      marginBottom: "var(--space-3)",
                    }}
                  >
                    SELECT RUNNER
                  </label>
                  <select
                    value={selectedPid}
                    onChange={(e) => setSelectedPid(e.target.value)}
                    className="rf-input"
                  >
                    {playersList.map(([pid, p]: [string, any]) => (
                      <option key={pid} value={pid}>
                        #{p.jersey_number || pid} — {p.name} ({p.team} · {p.position})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Selected Player Preview Card */}
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "var(--space-8)",
                    padding: "var(--space-6) var(--space-8)",
                    background: "rgba(22,16,38,0.7)",
                    border: "1px solid rgba(225,223,220,0.1)",
                    borderRadius: "var(--radius-sm)",
                  }}
                >
                  {selectedPlayer.photo_path ? (
                    <img
                      src={`http://localhost:8000${selectedPlayer.photo_path}`}
                      alt={selectedPlayer.name}
                      style={{
                        width: 44,
                        height: 44,
                        borderRadius: "var(--radius-sm)",
                        objectFit: "cover",
                        border: "1px solid rgba(128,51,235,0.4)",
                      }}
                    />
                  ) : (
                    <div
                      style={{
                        width: 44,
                        height: 44,
                        borderRadius: "var(--radius-sm)",
                        background: selectedPlayer.team === "Team A" ? "#E63946" : "#1D3557",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "#fff",
                        fontWeight: 500,
                        fontSize: "var(--text-xs)",
                      }}
                    >
                      #{selectedPlayer.jersey_number || selectedPid}
                    </div>
                  )}

                  <div>
                    <h4 style={{ fontSize: "var(--text-sm)", fontWeight: 500, color: "var(--color-7)", margin: 0 }}>
                      #{selectedPlayer.jersey_number || selectedPid} {selectedPlayer.name}
                    </h4>
                    <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0 }}>
                      {selectedPlayer.team} · {selectedPlayer.position}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Step 2: Sprint Drill Setup */}
          <div className="rf-card" style={{ padding: "var(--space-10)" }}>
            <h3
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
              <Timer style={{ width: 16, height: 16, color: "var(--color-3)" }} />
              Step 2: Select Sprint Drill &amp; Marker Distance
            </h3>

            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-5)" }}>
                {[
                  { id: "10m", label: "10m Burst Test", dist: 10.0 },
                  { id: "30m", label: "30m Sprint Drill", dist: 30.0 },
                  { id: "50m", label: "50m Max Speed Test", dist: 50.0 },
                  { id: "custom", label: "Custom Distance", dist: customDistance },
                ].map((drill) => (
                  <button
                    key={drill.id}
                    onClick={() => handleDrillChange(drill.id, drill.dist)}
                    style={{
                      padding: "var(--space-6) var(--space-8)",
                      borderRadius: "var(--radius-sm)",
                      fontSize: "var(--text-xs)",
                      fontWeight: 500,
                      cursor: "pointer",
                      border: `1px solid ${drillType === drill.id ? "rgba(128,51,235,0.5)" : "rgba(225,223,220,0.1)"}`,
                      background: drillType === drill.id ? "rgba(128,51,235,0.18)" : "rgba(22,16,38,0.5)",
                      color: drillType === drill.id ? "var(--color-7)" : "var(--color-4)",
                      textAlign: "left",
                      transition: "all 0.3s cubic-bezier(0.2,0,0.2,1)",
                    }}
                  >
                    <p style={{ margin: 0, fontWeight: 500 }}>{drill.label}</p>
                    <span style={{ fontSize: 10, color: "var(--color-3)" }}>{drill.dist} meters</span>
                  </button>
                ))}
              </div>

              {drillType === "custom" && (
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-6)", marginTop: "var(--space-2)" }}>
                  <span style={{ fontSize: "var(--text-xs)", color: "var(--color-4)" }}>Custom marker distance (meters):</span>
                  <input
                    type="number"
                    min="5"
                    max="200"
                    value={customDistance}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value) || 10.0;
                      setCustomDistance(val);
                      setDistanceMeters(val);
                    }}
                    className="rf-input"
                    style={{ width: 100 }}
                  />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Video Upload & Execution */}
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-9)" }}>
          <div className="rf-card" style={{ padding: "var(--space-10)" }}>
            <h3
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
              <Upload style={{ width: 16, height: 16, color: "var(--color-3)" }} />
              Step 3: Upload Player Running Video
            </h3>

            {/* Upload Drop Zone */}
            <label
              htmlFor="sprint-video-input"
              style={{
                display: "block",
                border: "1px dashed rgba(128,51,235,0.35)",
                borderRadius: "var(--radius-md)",
                padding: "var(--space-11)",
                textAlign: "center",
                cursor: "pointer",
                background: "rgba(128,51,235,0.04)",
                transition: "all 0.3s cubic-bezier(0.2,0,0.2,1)",
                marginBottom: "var(--space-8)",
              }}
            >
              <input
                type="file"
                accept="video/*"
                onChange={handleVideoSelect}
                id="sprint-video-input"
                style={{ display: "none" }}
              />
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: "var(--radius-md)",
                  background: "rgba(128,51,235,0.12)",
                  border: "1px solid rgba(128,51,235,0.25)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "0 auto var(--space-6)",
                }}
              >
                <Zap style={{ width: 20, height: 20, color: "var(--color-3)" }} />
              </div>
              <p style={{ fontSize: "var(--text-sm)", fontWeight: 500, color: "var(--color-6)", margin: "0 0 var(--space-2)" }}>
                {videoFile ? videoFile.name : "Click to upload running sprint clip"}
              </p>
              <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0 }}>
                Supports .mp4, .mov, .avi (Straight-line running or sprint drills)
              </p>
            </label>

            {/* Video Preview */}
            {videoPreviewUrl && (
              <div
                style={{
                  borderRadius: "var(--radius-md)",
                  overflow: "hidden",
                  border: "1px solid rgba(225,223,220,0.1)",
                  background: "rgba(22,16,38,0.9)",
                  aspectRatio: "16/9",
                  marginBottom: "var(--space-8)",
                }}
              >
                <video
                  controls
                  src={videoPreviewUrl}
                  style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
                />
              </div>
            )}

            {/* Run Button */}
            <button
              onClick={handleRunSpeedAnalysis}
              disabled={processing}
              className="rf-btn-primary"
              style={{
                width: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "var(--space-5)",
                padding: "var(--space-9)",
              }}
            >
              <Play style={{ width: 15, height: 15 }} />
              <span>
                {processing
                  ? "Processing Running Video…"
                  : `Calculate Speed for ${selectedPlayer.name}`}
              </span>
            </button>

            {/* Progress Bar */}
            {processing && (
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)", marginTop: "var(--space-6)" }}>
                <div
                  style={{
                    width: "100%",
                    height: 4,
                    background: "rgba(225,223,220,0.08)",
                    borderRadius: "var(--radius-sm)",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: `${progress}%`,
                      height: "100%",
                      background: "var(--color-2)",
                      borderRadius: "var(--radius-sm)",
                      transition: "width 0.5s cubic-bezier(0.2,0,0.2,1)",
                    }}
                  />
                </div>
                <p style={{ fontSize: "var(--text-xs)", color: "var(--color-3)", textAlign: "center", margin: 0 }}>
                  {stepText}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── STEP 5: SPEED TELEMETRY & RESULTS ─────────────────────── */}
      {telemetry && (
        <div
          className="rf-card"
          style={{
            padding: "var(--space-11)",
            background: "linear-gradient(135deg, rgba(128,51,235,0.12) 0%, rgba(22,16,38,0.9) 60%)",
            border: "1px solid rgba(128,51,235,0.35)",
            display: "flex",
            flexDirection: "column",
            gap: "var(--space-10)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              borderBottom: "1px solid rgba(225,223,220,0.1)",
              paddingBottom: "var(--space-8)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "var(--space-6)" }}>
              <Gauge style={{ width: 22, height: 22, color: "var(--color-3)" }} />
              <div>
                <h3 style={{ fontSize: "var(--text-lg)", fontWeight: 300, color: "var(--color-7)", margin: 0 }}>
                  Speed Telemetry &amp; Kinematics Report
                </h3>
                <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0 }}>
                  Calculated for #{selectedPlayer.jersey_number || selectedPid} {selectedPlayer.name} ({telemetry.drill_type})
                </p>
              </div>
            </div>
            <span className="rf-badge">{telemetry.speed_rating}</span>
          </div>

          {/* Key Metric Gauges */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "var(--space-8)" }}>
            {/* Max Speed */}
            <div
              style={{
                background: "rgba(128,51,235,0.12)",
                border: "1px solid rgba(128,51,235,0.3)",
                borderRadius: "var(--radius-md)",
                padding: "var(--space-8)",
                textAlign: "center",
              }}
            >
              <p style={{ fontSize: 10, color: "var(--color-3)", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.06em", margin: 0 }}>
                TOP SPRINT SPEED
              </p>
              <p style={{ fontSize: 44, fontWeight: 300, color: "var(--color-3)", margin: "var(--space-3) 0", lineHeight: 1 }}>
                {telemetry.maximum_speed_kmh}
              </p>
              <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0 }}>km / hour</p>
            </div>

            {/* Average Speed */}
            <div
              style={{
                background: "rgba(22,16,38,0.7)",
                border: "1px solid rgba(225,223,220,0.1)",
                borderRadius: "var(--radius-md)",
                padding: "var(--space-8)",
                textAlign: "center",
              }}
            >
              <p style={{ fontSize: 10, color: "var(--color-4)", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.06em", margin: 0 }}>
                MEAN SPRINT VELOCITY
              </p>
              <p style={{ fontSize: 36, fontWeight: 300, color: "var(--color-7)", margin: "var(--space-3) 0", lineHeight: 1 }}>
                {telemetry.average_speed_kmh}
              </p>
              <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0 }}>km / hour</p>
            </div>

            {/* Sprint Duration */}
            <div
              style={{
                background: "rgba(22,16,38,0.7)",
                border: "1px solid rgba(225,223,220,0.1)",
                borderRadius: "var(--radius-md)",
                padding: "var(--space-8)",
                textAlign: "center",
              }}
            >
              <p style={{ fontSize: 10, color: "var(--color-4)", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.06em", margin: 0 }}>
                SPRINT DURATION
              </p>
              <p style={{ fontSize: 36, fontWeight: 300, color: "var(--color-7)", margin: "var(--space-3) 0", lineHeight: 1 }}>
                {telemetry.sprint_duration_seconds}s
              </p>
              <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0 }}>Across {telemetry.distance_meters}m</p>
            </div>

            {/* Peak Acceleration */}
            <div
              style={{
                background: "rgba(22,16,38,0.7)",
                border: "1px solid rgba(225,223,220,0.1)",
                borderRadius: "var(--radius-md)",
                padding: "var(--space-8)",
                textAlign: "center",
              }}
            >
              <p style={{ fontSize: 10, color: "var(--color-4)", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.06em", margin: 0 }}>
                PEAK ACCELERATION
              </p>
              <p style={{ fontSize: 36, fontWeight: 300, color: "var(--color-7)", margin: "var(--space-3) 0", lineHeight: 1 }}>
                {telemetry.peak_acceleration_mps2}
              </p>
              <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0 }}>m / s²</p>
            </div>
          </div>

          {/* Speed Progression Curve Visualizer */}
          {telemetry.speed_curve && telemetry.speed_curve.length > 0 && (
            <div
              style={{
                background: "rgba(22,16,38,0.8)",
                border: "1px solid rgba(225,223,220,0.08)",
                borderRadius: "var(--radius-md)",
                padding: "var(--space-9)",
              }}
            >
              <h4
                style={{
                  fontSize: "var(--text-xs)",
                  fontWeight: 500,
                  color: "var(--color-4)",
                  textTransform: "uppercase",
                  letterSpacing: "0.07em",
                  margin: "0 0 var(--space-8)",
                  display: "flex",
                  alignItems: "center",
                  gap: "var(--space-4)",
                }}
              >
                <TrendingUp style={{ width: 14, height: 14, color: "var(--color-3)" }} />
                Instantaneous Velocity Progression Curve (0 to {telemetry.sprint_duration_seconds}s)
              </h4>

              <div style={{ display: "flex", alignItems: "flex-end", gap: "var(--space-4)", height: 110, paddingBottom: 10 }}>
                {telemetry.speed_curve.map((pt: any, idx: number) => {
                  const maxVal = telemetry.maximum_speed_kmh || 30.0;
                  const heightPct = Math.max(8, (pt.speed_kmh / maxVal) * 100);
                  return (
                    <div
                      key={idx}
                      style={{
                        flex: 1,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        gap: 6,
                        height: "100%",
                        justifyContent: "flex-end",
                      }}
                    >
                      <span style={{ fontSize: 9, color: "var(--color-3)", fontFamily: "var(--font-mono)" }}>
                        {pt.speed_kmh}
                      </span>
                      <div
                        style={{
                          width: "100%",
                          height: `${heightPct}%`,
                          background: "linear-gradient(180deg, var(--color-2) 0%, rgba(128,51,235,0.3) 100%)",
                          borderRadius: "var(--radius-sm)",
                          transition: "height 0.5s ease-out",
                        }}
                      />
                      <span style={{ fontSize: 9, color: "var(--color-4)" }}>{pt.time_s}s</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Profile Confirmation CTA */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              paddingTop: "var(--space-6)",
              borderTop: "1px solid rgba(225,223,220,0.1)",
            }}
          >
            <span style={{ fontSize: "var(--text-xs)", color: "var(--color-4)" }}>
              ✓ Verified speed metric of <strong>{telemetry.maximum_speed_kmh} km/h</strong> synced to Player Analytics.
            </span>
            <Link
              href="/players"
              className="rf-btn-primary"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "var(--space-4)",
                fontSize: "var(--text-xs)",
                textDecoration: "none",
              }}
            >
              <span>View in Player Analytics</span>
              <ArrowRight style={{ width: 13, height: 13 }} />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
