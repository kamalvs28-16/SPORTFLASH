# ⚽ SPORTFLASH: AI-Powered Football Video Analytics & Performance Intelligence Engine

SPORTFLASH is an enterprise-grade Computer Vision and AI analytics platform for football (soccer). It converts raw match and training video footage into deep tactical intelligence, player tracking telemetry, high-precision sprint metrics, defensive duel statistics, automated coaching insights, and personalized sports nutrition recommendations.

---

## 📑 Table of Contents
1. [System Architecture](#-system-architecture)
2. [End-to-End Pipeline & Workflow](#-end-to-end-pipeline--workflow)
3. [Key Modules & Platform Features](#-key-modules--platform-features)
4. [Project Structure](#-project-structure)
5. [Technology Stack](#-technology-stack)
6. [Quickstart & Demo Mode](#-quickstart--demo-mode)
7. [Installation & Setup](#-installation--setup)
8. [API Reference Guide](#-api-reference-guide)
9. [Troubleshooting & Robust Fallbacks](#-troubleshooting--robust-fallbacks)

---

## 🏛 System Architecture

```
                                  ┌────────────────────────┐
                                  │   Match Video (.mp4)   │
                                  └───────────┬────────────┘
                                              │
                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               SPORTFLASH AI ENGINE (Python)                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  1. Detection & Tracking    │ YOLOv11 / ByteTrack + OpenCV Optical Motion Fallback     │
│  2. Team Classification     │ Torso ROI Extraction + HSV Space + K-Means Clustering    │
│  3. Spatial Metric Engine   │ Pitch Homography Matrix Calibration + Speed / Accel      │
│  4. Defensive Analytics     │ Dual Proximity Modeling -> Tackles, Duels, Interceptions │
│  5. Tactical & Event Engine │ Heatmap Generation, Event Detection & Match Synthesis    │
│  6. AI Insights & Nutrition │ Algorithmic Scoring, Tactical Advice & Nutrition Plan    │
└─────────────────────────────────────────────┬──────────────────────────────────────────┘
                                              │
                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                            FASTAPI BACKEND SERVICE (:8000)                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  REST API Endpoints: Pipeline State, Telemetry, Roster Store, Static Media Streaming   │
└─────────────────────────────────────────────┬──────────────────────────────────────────┘
                                              │ JSON / HTTP
                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        NEXT.JS 16 & REACT 19 FRONTEND (:3000)                          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  • Executive Overview (/)             • Team Tactical Analysis (/teams)                │
│  • Video & AI Studio (/studio)        • Individual Speed Lab (/speed)                  │
│  • Team & Player Roster (/roster)     • Chronological Match Events (/events)           │
│  • Squad Intelligence (/players)      • Comprehensive Match Report (/report)           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 End-to-End Pipeline & Workflow

SPORTFLASH operates through a structured multi-phase workflow:

### Phase 1: Team & Roster Calibration (`/roster`)
- **Format Selection**: Choose between standard formats (`5v5`, `7v7`, `11v11`) or configure a `Custom` squad size.
- **Kit Color & Team Identity**: Set primary and secondary jersey colors and coach names for both competing teams.
- **Player Profiling**: Assign player names, jersey numbers, tactical roles, player notes, and upload player photos.
- **⚡ Instant 1-Click Demo**: Pre-loads Portugal (Red kit, 5 players) vs Spain (White kit, 5 players) for zero-setup presentations.

### Phase 2: Video Ingestion & AI Processing (`/studio`)
- **Video Input**: Upload any match or training drill video (`.mp4`, `.mov`, `.avi`, `.mkv`).
- **AI Model Selection**:
  - `YOLOv11 Nano / Small / Medium / Large` for high-accuracy bounding box detection.
  - Native **OpenCV Computer Vision Tracker** fallback when running in lightweight environments.
- **Automated Pipeline Execution**:
  1. Multi-Object Player Tracking across consecutive frames.
  2. Jersey torso color extraction and automated team clustering.
  3. Pitch homography mapping to convert pixel displacements into real-world meters.
  4. Real-time speed, acceleration, and distance telemetry calculation.
  5. Defensive engagement detection (tackles won, pressures, interceptions).
  6. Annotated output video generation with bounding boxes, player labels, and speed badges.

### Phase 3: Tactical & Performance Analytics
- **Executive Dashboard (`/`)**: High-level match summary, team comparison radar, top performers, and possession distribution.
- **Team Analysis (`/teams`)**: Spatial dominance heatmaps, pitch third breakdown (Defensive / Midfield / Attacking), and team passing/duel stats.
- **Player Intelligence (`/players`)**: Full squad roster cards, individual player deep-dive modal (radar charts, speed zones, defensive metrics, AI coaching feedback, and personalized recovery nutrition).
- **Sprint & Speed Test Lab (`/speed`)**: Dedicated sprint testing module for 10m, 30m, and 50m sprint drills with velocity curves and split times.
- **Match Events Timeline (`/events`)**: Timestamped log of key plays, fast breaks, key tackles, and tactical transitions.
- **Match Report (`/report`)**: Complete executive match dossier with AI summary, ready for review or export.

---

## 🧩 Key Modules & Platform Features

| Module | Location | Description |
| :--- | :--- | :--- |
| **Pipeline Orchestrator** | `AI/pipeline_orchestrator.py` | Central controller managing video ingestion, tracking, metric generation, and annotated video rendering. |
| **Roster Manager** | `AI/roster_manager.py` | Manages team configurations, player slot bindings, persistence in `results/roster_config.json`, and 1-click demo setups. |
| **Speed & Homography Engine** | `AI/speed_analysis.py`, `AI/homography.py` | Perspective transformation from camera plane to 2D pitch coordinates; computes instant & average km/h. |
| **Sprint Test Engine** | `AI/speed_test_engine.py` | Specialized high-frequency telemetry calculator for individual sprint drills. |
| **Tackle & Duel Analytics** | `AI/tackle_analysis.py` | Measures spatial proximity between opposing players, classifying tackles, duels, interceptions, and defensive ratings. |
| **Team Classifier & Heatmaps** | `AI/team_classifier.py`, `AI/team_heatmap.py` | HSV color histogram clustering for team classification and 2D Gaussian density heatmaps for field dominance. |
| **AI Insights & Nutrition** | `AI/ai_insights.py`, `AI/nutrition_recommendation.py` | Rule-based and generative AI recommendations for tactical improvement and energy replenishment. |
| **FastAPI Backend** | `backend/main.py` | Asynchronous REST API serving analytical payloads, background task status, and static media. |
| **Next.js Frontend** | `frontend/src/app/` | 7 dedicated analytics pages styled with the Roboflow design system, Chart.js, and interactive canvas overlays. |

---

## 📂 Project Structure

```
SPORTFLASH/
├── AI/                                  # AI & Computer Vision Analytics Core
│   ├── acceleration_analysis.py         # Player acceleration and deceleration profiling
│   ├── ai_insights.py                   # Automated tactical feedback generation
│   ├── ball_analysis.py                 # Ball movement and trajectory analysis
│   ├── ball_detection.py                # Ball localization module
│   ├── ball_speed.py                    # Ball velocity calculation
│   ├── calibrate_field.py               # Manual and automatic field calibration
│   ├── camera_motion.py                 # Optical flow background compensation
│   ├── detect_players.py                # Object detection wrapper
│   ├── distance_analysis.py             # Total distance & stamina metrics
│   ├── dynamic_calibration.py           # Adaptive pitch perspective mapping
│   ├── event_detection.py               # Key match event extraction
│   ├── heatmap.py                       # Individual player spatial heatmap generation
│   ├── homography.py                    # Pitch 2D projection transformation
│   ├── match_report.py                  # Tactical report synthesis
│   ├── movement_analysis.py             # Player movement vectors and directions
│   ├── nutrition_recommendation.py      # Personalized post-match sports nutrition
│   ├── performance_score.py             # Composite player performance index (0-100)
│   ├── pipeline_orchestrator.py         # End-to-end processing pipeline orchestrator
│   ├── player_comparison.py             # Head-to-head player statistical comparison
│   ├── player_ranking.py                # Positional squad rankings
│   ├── roster_manager.py                # Team & player configuration management
│   ├── speed_analysis.py                # In-match player speed calculation
│   ├── speed_test_engine.py             # Dedicated sprint test analysis
│   ├── tackle_analysis.py               # Defensive duels and tackle detection
│   ├── team_analysis.py                 # Team-level possession and tactical metrics
│   ├── team_classifier.py               # Color clustering for jersey detection
│   ├── team_heatmap.py                  # Dual-team comparative field heatmaps
│   ├── track_players.py                 # Multi-object tracking (ByteTrack / OpenCV)
│   └── zone_analysis.py                 # Speed zone categorization (Walk / Jog / Run / Sprint)
│
├── backend/                             # REST API Service
│   ├── main.py                          # FastAPI application and route definitions
│   └── results/                         # Active JSON results cache & player photos
│
├── frontend/                            # Next.js 16 Web Application
│   ├── src/
│   │   ├── app/
│   │   │   ├── events/page.tsx          # Match Event Timeline page
│   │   │   ├── players/page.tsx         # Player Intelligence & Squad Roster page
│   │   │   ├── report/page.tsx          # Match Analytics Report page
│   │   │   ├── roster/page.tsx          # Team & Player Roster Calibration Studio
│   │   │   ├── speed/page.tsx           # Individual Sprint & Speed Drill Testing Lab
│   │   │   ├── studio/page.tsx          # Video Upload & AI Execution Studio
│   │   │   ├── teams/page.tsx           # Team Tactical & Spatial Analysis page
│   │   │   ├── globals.css              # Roboflow design tokens & styling
│   │   │   ├── layout.tsx               # App layout with navigation sidebar
│   │   │   └── page.tsx                 # Executive Overview Dashboard
│   ├── package.json                     # Frontend dependencies
│   └── tsconfig.json                    # TypeScript configuration
│
├── results/                             # Processed match outputs & JSON telemetry
│   ├── annotated_match.mp4              # Visualized output video with tracking overlays
│   ├── roster_config.json               # Current active match roster configuration
│   ├── speed_results.json               # Player velocity and acceleration data
│   ├── tackle_results.json              # Defensive tackle and duel statistics
│   ├── performance_scores.json          # Overall player match ratings
│   └── ai_insights.json                 # Actionable player recommendations
│
├── videos/                              # Video storage for uploads & test clips
└── README.md                            # Comprehensive platform documentation
```

---

## 🛠 Technology Stack

### Computer Vision & AI
- **Python 3.10+ / 3.11**
- **OpenCV (`cv2`)**: Video decoding, background subtraction, contour extraction, optical flow, homography, and video encoding.
- **YOLOv11 (Ultralytics)**: Deep learning object detection & tracking (with graceful OpenCV fallback).
- **NumPy & SciPy**: Matrix operations, Euclidean proximity algorithms, and spatial clustering.

### Backend
- **FastAPI**: High-performance asynchronous REST API framework.
- **Uvicorn**: ASGI web server implementation.
- **Pydantic**: Request/response schema validation and type safety.

### Frontend
- **Next.js 16 (App Router)** & **React 19**
- **TypeScript**: Strict type-checking across all UI components.
- **Lucide Icons**: Modern SVG icon suite.
- **HTML5 Canvas**: Dynamic 2D pitch coordinate mapping and spatial overlays.
- **Roboflow Design System**: Dark-themed UI (`--color-1` to `--color-7`, `--radius-md`).

---

## ⚡ Quickstart & Demo Mode

For live presentations or fast testing without manual data entry:

1. Open the web interface at **`http://localhost:3000`**.
2. Navigate to **Team & Player Roster (`/roster`)**.
3. Click the **`⚡ Load Portugal vs Spain Demo`** button.
   - Automatically sets a `5v5` match format.
   - Configures **Portugal** (Red `#E63946`) with 5 players (Cristiano Ronaldo, Bruno Fernandes, Bernardo Silva, Diogo Costa, Rúben Dias).
   - Configures **Spain** (White `#DEDEDE`) with 5 players (Aymeric Laporte, Dani Olmo, Rodri, Lamine Yamal, Unai Simón).
4. Navigate to **Video & AI Studio (`/studio`)** and click **"Execute AI Video Analytics"**.

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Node.js 18.x or higher
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd SPORTFLASH
```

### 2. Python Backend Setup
```bash
# Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn opencv-python numpy pydantic
# Optional: Install YOLO for deep learning tracking
pip install ultralytics torch
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

---

## 🏃 Running the Application

### Start Backend API Server
```bash
# From the project root or backend folder:
cd backend
python -m uvicorn main:app --reload --port 8000
```
*The FastAPI documentation will be available at `http://localhost:8000/docs`.*

### Start Frontend Web Application
```bash
# In a separate terminal:
cd frontend
npm run dev
```
*The application will be accessible at `http://localhost:3000`.*

---

## 📡 API Reference Guide

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | System health check and module availability status. |
| `GET` | `/api/pipeline-status` | Current progress percentage and stage details for video analysis. |
| `POST` | `/api/process-video` | Starts the end-to-end AI analytics pipeline on an uploaded match video. |
| `GET` | `/api/roster` | Retrieves current team calibration and player profiles. |
| `POST` | `/api/roster` | Updates and persists the match roster configuration. |
| `POST` | `/api/roster/reset` | Resets the roster to a clean, blank state. |
| `POST` | `/api/roster/load-demo` | Loads the Portugal vs Spain 5v5 presentation demo preset. |
| `POST` | `/api/roster/player-photo/{player_id}` | Uploads and associates a player photo with a roster slot. |
| `POST` | `/api/speed-test` | Executes high-precision sprint analysis on an individual drill video. |
| `GET` | `/api/players` | Returns all players with aggregated speed, tackle, and performance stats. |
| `GET` | `/api/players/{player_id}` | Detailed telemetry, radar metrics, and nutrition plan for a specific player. |
| `GET` | `/api/teams` | Returns tactical metrics, possession stats, and field zone dominance. |
| `GET` | `/api/events` | Retrieves chronological match event log. |
| `GET` | `/api/report` | Returns the synthesized match analytics report. |

---

## 🛡 Troubleshooting & Robust Fallbacks

- **Zero Hard Crashes on Missing ML Libraries**: If `ultralytics` or `scikit-learn` are not present, SPORTFLASH automatically falls back to native OpenCV MOG2 background subtraction and native OpenCV K-Means clustering.
- **Windows Terminal Safe**: All terminal output uses clean ASCII status flags (`[OK]`, `[#1]`, `->`) to avoid `UnicodeEncodeError` on Windows consoles.
- **Dynamic Port Mapping**: The Next.js frontend is pre-configured to communicate with the FastAPI backend on `http://localhost:8000`.

---

© 2026 SPORTFLASH Analytics Engine. All rights reserved.