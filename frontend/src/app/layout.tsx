import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"], weight: ["300", "400", "500"] });

export const metadata: Metadata = {
  title: "SPORTFLASH AI — Football Performance Analytics Studio",
  description: "Computer Vision & AI-Powered Football Analytics Platform: Player Tracking, Jersey Team Classification, Running Speed, Defensive Tackles & Heatmaps",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <body
        className={inter.className}
        style={{
          background: "var(--color-1)",
          color: "var(--color-6)",
          display: "flex",
          minHeight: "100vh",
        }}
      >
        <Sidebar />
        <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
          <Navbar />
          <main style={{ flex: 1, padding: "var(--space-11)", overflowY: "auto" }}>
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
