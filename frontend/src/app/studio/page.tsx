"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import {
  Video,
  Upload,
  Play,
  CheckCircle2,
  Settings,
  Zap,
  ShieldCheck,
  Target,
  ArrowRight,
  AlertCircle,
  FileText,
  UserCheck,
} from "lucide-react";

export default function StudioPage() {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string>("");
  const [confThresh, setConfThresh] = useState<number>(0.5);

  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stepText, setStepText] = useState("");
  const [stepDetails, setStepDetails] = useState("");
  const [complete, setComplete] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const pollTimerRef = useRef<NodeJS.Timeout | null>(null);

  const handleVideoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setVideoFile(file);
      setVideoPreviewUrl(URL.createObjectURL(file));
      setComplete(false);
      setErrorMsg("");
    }
  };

  const pollPipelineStatus = () => {
    pollTimerRef.current = setInterval(async () => {
      try {
        const res = await fetch("http://localhost:8000/api/pipeline-status");
        const status = await res.json();

        if (status) {
          setProgress(status.progress || 0);
          setStepText(status.step_name || "Processing AI Pipeline…");
          setStepDetails(status.details || "");

          if (status.error) {
            setErrorMsg(status.error);
            setProcessing(false);
            if (pollTimerRef.current) clearInterval(pollTimerRef.current);
          } else if (status.completed || status.progress >= 100) {
            setComplete(true);
            setProcessing(false);
            if (pollTimerRef.current) clearInterval(pollTimerRef.current);
          }
        }
      } catch (err) {
        console.error("Polling status error:", err);
      }
    }, 700);
  };

  useEffect(() => {
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, []);

  const handleUploadAndRun = async () => {
    setProcessing(true);
    setProgress(5);
    setStepText("Step 1/5: Uploading video & launching AI Computer Vision pipeline…");
    setStepDetails("Initializing pipeline orchestrator...");
    setComplete(false);
    setErrorMsg("");

    try {
      const formData = new FormData();
      if (videoFile) {
        formData.append("file", videoFile);
      }
      formData.append("conf_thresh", confThresh.toString());

      const res = await fetch("http://localhost:8000/api/process-video", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.status === "processing_started" || data.status === "success") {
        pollPipelineStatus();
      } else {
        setErrorMsg(data.message || "Failed to start pipeline");
        setProcessing(false);
      }
    } catch (err: any) {
      console.error("Processing error:", err);
      setErrorMsg(err.message || "Failed to connect to backend server");
      setProcessing(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-11)", maxWidth: 1100, margin: "0 auto" }}>
      {/* Title */}
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
          <Video style={{ width: 28, height: 28, color: "var(--color-3)" }} />
          Football Video &amp; AI Analytics Studio
        </h1>
        <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: "var(--space-4) 0 0", lineHeight: "19.5px" }}>
          Upload match recordings to execute full frame-by-frame player detection, ByteTrack tracking, team HSV jersey classification, pitch homography speed (km/h), defensive duels, and positional heatmaps.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: "var(--space-11)" }}>
        {/* Left: Upload & Preview */}
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-9)" }}>
          <div className="rf-card" style={{ padding: "var(--space-10)" }}>
            <h3
              style={{
                fontSize: "var(--text-sm)",
                fontWeight: 500,
                color: "var(--color-7)",
                margin: "0 0 var(--space-9)",
                display: "flex",
                alignItems: "center",
                gap: "var(--space-5)",
              }}
            >
              <Upload style={{ width: 15, height: 15, color: "var(--color-3)" }} />
              Select or Upload Match Video
            </h3>

            {/* Drop Zone */}
            <label
              htmlFor="video-upload-input"
              style={{
                display: "block",
                border: "1px dashed rgba(128,51,235,0.35)",
                borderRadius: "var(--radius-md)",
                padding: "var(--space-13)",
                textAlign: "center",
                cursor: "pointer",
                background: "rgba(128,51,235,0.04)",
                transition: "border-color 0.3s cubic-bezier(0.2,0,0.2,1), background-color 0.3s cubic-bezier(0.2,0,0.2,1)",
                marginBottom: "var(--space-9)",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "rgba(128,51,235,0.6)";
                (e.currentTarget as HTMLElement).style.background = "rgba(128,51,235,0.08)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "rgba(128,51,235,0.35)";
                (e.currentTarget as HTMLElement).style.background = "rgba(128,51,235,0.04)";
              }}
            >
              <input
                type="file"
                accept="video/*"
                onChange={handleVideoSelect}
                style={{ display: "none" }}
                id="video-upload-input"
              />
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: "var(--radius-md)",
                  background: "rgba(128,51,235,0.12)",
                  border: "1px solid rgba(128,51,235,0.25)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "0 auto var(--space-8)",
                }}
              >
                <Video style={{ width: 22, height: 22, color: "var(--color-3)" }} />
              </div>
              <p style={{ fontSize: "var(--text-sm)", fontWeight: 500, color: "var(--color-6)", margin: "0 0 var(--space-4)" }}>
                {videoFile ? videoFile.name : "Click to select and upload match video"}
              </p>
              <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0 }}>
                Supports .mp4, .avi, .mov (HD 1080p / 60 FPS recommended)
              </p>
            </label>

            {/* Video Preview */}
            <div
              style={{
                borderRadius: "var(--radius-md)",
                overflow: "hidden",
                border: "1px solid rgba(225,223,220,0.1)",
                background: "rgba(22,16,38,0.9)",
                aspectRatio: "16/9",
              }}
            >
              <video
                controls
                style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
                src={videoPreviewUrl || "http://localhost:8000/static/videos/football.mp4"}
              />
            </div>
          </div>
        </div>

        {/* Right: Settings & Execution */}
        <div>
          <div className="rf-card" style={{ padding: "var(--space-10)", display: "flex", flexDirection: "column", gap: "var(--space-9)" }}>
            <h3
              style={{
                fontSize: "var(--text-sm)",
                fontWeight: 500,
                color: "var(--color-7)",
                margin: 0,
                display: "flex",
                alignItems: "center",
                gap: "var(--space-5)",
              }}
            >
              <Settings style={{ width: 15, height: 15, color: "var(--color-3)" }} />
              AI Engine Configuration
            </h3>

            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-9)" }}>
              {/* Confidence slider */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "var(--space-4)" }}>
                  <label style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", fontWeight: 500 }}>
                    YOLO Detection Confidence
                  </label>
                  <span style={{ fontSize: "var(--text-xs)", color: "var(--color-3)", fontFamily: "var(--font-mono)" }}>
                    {confThresh}
                  </span>
                </div>
                <input
                  type="range"
                  min="0.2"
                  max="0.9"
                  step="0.05"
                  value={confThresh}
                  onChange={(e) => setConfThresh(parseFloat(e.target.value))}
                  style={{ width: "100%", accentColor: "var(--color-2)" }}
                />
              </div>

              {/* Tracker select */}
              <div>
                <label style={{ display: "block", fontSize: "var(--text-xs)", color: "var(--color-4)", fontWeight: 500, marginBottom: "var(--space-4)" }}>
                  Player Tracker Algorithm
                </label>
                <select className="rf-input">
                  <option>ByteTrack Persistent Tracker</option>
                  <option>DeepSORT Tracker</option>
                </select>
              </div>

              {/* Classifier select */}
              <div>
                <label style={{ display: "block", fontSize: "var(--text-xs)", color: "var(--color-4)", fontWeight: 500, marginBottom: "var(--space-4)" }}>
                  Jersey Team Classifier
                </label>
                <select className="rf-input">
                  <option>HSV Upper Torso ROI + K-Means</option>
                  <option>RGB Color Histogram</option>
                </select>
              </div>

              {/* Accuracy Features Checklist */}
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "var(--space-5)",
                  paddingTop: "var(--space-8)",
                  borderTop: "1px solid rgba(225,223,220,0.1)",
                }}
              >
                <p style={{ fontSize: 10, textTransform: "uppercase", color: "var(--color-4)", fontWeight: 500, letterSpacing: "0.06em", margin: 0 }}>
                  Active Accuracy Enhancements
                </p>
                {[
                  "Rolling Median Velocity Filter (Cap False Spikes)",
                  "Modal Jersey Voting (Zero Team Flickering)",
                  "Homography 105m x 68m Real Pitch Projection",
                  "Defensive Tackle & Duel Proximity Engine",
                ].map((feat) => (
                  <div key={feat} style={{ display: "flex", alignItems: "center", gap: "var(--space-4)", fontSize: "var(--text-xs)", color: "var(--color-4)" }}>
                    <CheckCircle2 style={{ width: 13, height: 13, color: "var(--color-3)", flexShrink: 0 }} />
                    <span>{feat}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Run button */}
            <button
              onClick={handleUploadAndRun}
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
              <span>{processing ? "Executing Real-Time AI Pipeline…" : "Execute AI Video Analytics"}</span>
            </button>

            {/* Progress */}
            {processing && (
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-5)" }}>
                <div
                  style={{
                    width: "100%",
                    height: 6,
                    background: "rgba(225,223,220,0.08)",
                    borderRadius: "var(--radius-sm)",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: `${progress}%`,
                      height: "100%",
                      background: "linear-gradient(90deg, var(--color-2) 0%, var(--color-3) 100%)",
                      borderRadius: "var(--radius-sm)",
                      transition: "width 0.4s cubic-bezier(0.2,0,0.2,1)",
                    }}
                  />
                </div>
                <div style={{ textAlign: "center" }}>
                  <p style={{ fontSize: "var(--text-xs)", fontWeight: 500, color: "var(--color-3)", margin: "0 0 4px" }}>
                    {stepText} ({progress}%)
                  </p>
                  <p style={{ fontSize: 10, color: "var(--color-4)", margin: 0 }}>
                    {stepDetails}
                  </p>
                </div>
              </div>
            )}

            {/* Error Message */}
            {errorMsg && (
              <div
                style={{
                  background: "rgba(230,57,70,0.1)",
                  border: "1px solid rgba(230,57,70,0.3)",
                  borderRadius: "var(--radius-md)",
                  padding: "var(--space-8)",
                  display: "flex",
                  alignItems: "center",
                  gap: "var(--space-5)",
                  color: "#E63946",
                  fontSize: "var(--text-xs)",
                }}
              >
                <AlertCircle style={{ width: 16, height: 16, flexShrink: 0 }} />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Complete Card with Action Links */}
            {complete && !processing && (
              <div
                style={{
                  background: "rgba(128,51,235,0.12)",
                  border: "1px solid rgba(128,51,235,0.35)",
                  borderRadius: "var(--radius-md)",
                  padding: "var(--space-9)",
                  display: "flex",
                  flexDirection: "column",
                  gap: "var(--space-6)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-4)", fontSize: "var(--text-sm)", fontWeight: 500, color: "var(--color-3)" }}>
                  <CheckCircle2 style={{ width: 16, height: 16 }} />
                  AI Pipeline Complete!
                </div>
                <p style={{ fontSize: "var(--text-xs)", color: "var(--color-4)", margin: 0, lineHeight: "19.5px" }}>
                  Player detection, tracking IDs, speeds, defensive tackles, and positional heatmaps have been processed and synced across the platform.
                </p>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-4)", paddingTop: "var(--space-4)" }}>
                  <Link
                    href="/players"
                    className="rf-btn-secondary"
                    style={{ fontSize: 11, textAlign: "center", textDecoration: "none", padding: "var(--space-4)" }}
                  >
                    View Player Stats
                  </Link>
                  <Link
                    href="/report"
                    className="rf-btn-primary"
                    style={{ fontSize: 11, textAlign: "center", textDecoration: "none", padding: "var(--space-4)" }}
                  >
                    View Match Report
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
