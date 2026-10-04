"use client";

import { Activity, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

export default function Navbar() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const checkStatus = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/status");
      const data = await res.json();
      setStatus(data);
    } catch (err) {
      console.error("Backend status check error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkStatus();
  }, []);

  return (
    <header
      style={{
        height: 64,
        borderBottom: "1px solid rgba(225,223,220,0.1)",
        background: "rgba(22,16,38,0.85)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
        padding: "0 var(--space-11)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        position: "sticky",
        top: 0,
        zIndex: 30,
        boxShadow: "var(--shadow-sm)",
      }}
    >
      {/* Title & Status */}
      <div style={{ display: "flex", alignItems: "center", gap: "var(--space-10)" }}>
        <h2
          style={{
            fontSize: "var(--text-base)",
            fontWeight: 500,
            color: "var(--color-7)",
            margin: 0,
          }}
        >
          Football Analytics Platform
        </h2>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "var(--space-4)",
            background: "rgba(128,51,235,0.1)",
            border: "1px solid rgba(128,51,235,0.25)",
            borderRadius: "var(--radius-sm)",
            padding: "3px var(--space-6)",
            fontSize: "var(--text-xs)",
            color: "var(--color-3)",
          }}
        >
          <Activity style={{ width: 12, height: 12 }} />
          <span>YOLOv11 + ByteTrack AI Engine</span>
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: "flex", alignItems: "center", gap: "var(--space-10)" }}>
        <button
          onClick={checkStatus}
          className="rf-btn-secondary"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "var(--space-4)",
            fontSize: "var(--text-xs)",
            padding: "var(--space-4) var(--space-8)",
          }}
        >
          <RefreshCw
            style={{
              width: 13,
              height: 13,
              animation: loading ? "spin 1s linear infinite" : "none",
              color: loading ? "var(--color-3)" : "currentColor",
            }}
          />
          <span>Sync API</span>
        </button>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "var(--space-8)",
            paddingLeft: "var(--space-10)",
            borderLeft: "1px solid rgba(225,223,220,0.1)",
          }}
        >
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: "50%",
              background: "var(--color-2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 500,
              color: "var(--color-7)",
              fontSize: "var(--text-xs)",
              boxShadow: "0 0 12px rgba(128,51,235,0.4)",
            }}
          >
            CO
          </div>
          <div>
            <p
              style={{
                fontSize: "var(--text-xs)",
                fontWeight: 500,
                color: "var(--color-6)",
                margin: 0,
              }}
            >
              Coach Analyst
            </p>
            <p style={{ fontSize: 10, color: "var(--color-4)", margin: 0 }}>
              Head Performance Director
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </header>
  );
}
