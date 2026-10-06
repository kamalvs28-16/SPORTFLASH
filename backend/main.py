import os
import json
import shutil
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from AI.roster_manager import load_roster_config, save_roster_config, reset_roster_config, load_demo_roster_config, get_player_roster_info
from AI.tackle_analysis import calculate_tackles
from AI.speed_test_engine import analyze_individual_sprint
from AI.pipeline_orchestrator import run_full_ai_pipeline, get_pipeline_state

app = FastAPI(
    title="SPORTFLASH AI API Engine",
    description="Backend API for Football Performance Analytics, Player Identification, Individual Speed Calculation & Roster Calibration",
    version="2.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
VIDEOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "videos"))
PHOTOS_DIR = os.path.join(RESULTS_DIR, "player_photos")
SPRINT_VIDEOS_DIR = os.path.join(VIDEOS_DIR, "player_sprints")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(PHOTOS_DIR, exist_ok=True)
os.makedirs(SPRINT_VIDEOS_DIR, exist_ok=True)

# Mount static files for player photos and videos
app.mount("/static/results", StaticFiles(directory=RESULTS_DIR), name="results")
app.mount("/static/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")

def load_json_file(filename: str) -> Dict[str, Any]:
    file_path = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}

# --------------------------------------------------------------------------
# API Endpoints
# --------------------------------------------------------------------------

@app.get("/api/status")
def get_system_status():
    return {
        "status": "online",
        "system": "SPORTFLASH AI Engine v2.0",
        "modules": {
            "tracking": os.path.exists(os.path.join(RESULTS_DIR, "tracking_results.json")),
            "team_classification": os.path.exists(os.path.join(RESULTS_DIR, "team_classification.json")),
            "speed_analysis": os.path.exists(os.path.join(RESULTS_DIR, "speed_results.json")),
            "tackle_analysis": os.path.exists(os.path.join(RESULTS_DIR, "tackle_results.json")),
            "match_report": os.path.exists(os.path.join(RESULTS_DIR, "match_report.json")),
            "ai_insights": os.path.exists(os.path.join(RESULTS_DIR, "ai_insights.json"))
        }
    }

@app.get("/api/pipeline-status")
def get_pipeline_progress():
    return get_pipeline_state()

@app.get("/api/roster")
def get_roster():
    return load_roster_config()

class RosterSaveRequest(BaseModel):
    team_size: Optional[str] = "5v5"
    players_per_team: Optional[int] = 5
    team_a: Dict[str, Any]
    team_b: Dict[str, Any]
    players: Dict[str, Any]

@app.post("/api/roster")
def update_roster(payload: RosterSaveRequest):
    data = {
        "team_size": payload.team_size or "5v5",
        "players_per_team": payload.players_per_team or 5,
        "team_a": payload.team_a,
        "team_b": payload.team_b,
        "players": payload.players
    }
    success = save_roster_config(data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save roster config")
    return {"status": "success", "message": "Roster configuration updated", "config": data}

@app.post("/api/roster/reset")
def reset_roster():
    clean_config = reset_roster_config()
    return {"status": "success", "message": "Roster configuration reset to clean state", "config": clean_config}

@app.post("/api/roster/load-demo")
def load_match_demo():
    demo_config = load_demo_roster_config()
    return {"status": "success", "message": "Portugal vs Spain match demo roster loaded successfully!", "config": demo_config}

@app.post("/api/roster/player-photo/{player_id}")
async def upload_player_photo(player_id: str, file: UploadFile = File(...)):
    filename = f"player_{player_id}.png"
    filepath = os.path.join(PHOTOS_DIR, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update roster info
    config = load_roster_config()
    players = config.get("players", {})
    if player_id not in players:
        players[player_id] = get_player_roster_info(player_id, config)
    
    players[player_id]["photo_path"] = f"/static/results/player_photos/{filename}"
    config["players"] = players
    save_roster_config(config)
    
    return {
        "status": "success",
        "player_id": player_id,
        "photo_url": f"/static/results/player_photos/{filename}"
    }

# --------------------------------------------------------------------------
# Individual Player Speed Test API
# --------------------------------------------------------------------------

@app.post("/api/speed-test")
async def perform_player_speed_test(
    file: Optional[UploadFile] = File(None),
    player_id: str = Form("1"),
    drill_type: str = Form("30m"),
    distance_meters: float = Form(30.0)
):
    saved_path = ""
    if file and file.filename:
        filename = f"sprint_p{player_id}_{file.filename}"
        saved_path = os.path.join(SPRINT_VIDEOS_DIR, filename)
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    telemetry = analyze_individual_sprint(
        video_path=saved_path,
        player_id=player_id,
        drill_type=drill_type,
        distance_meters=distance_meters
    )
    
    return {
        "status": "success",
        "message": f"Individual sprint analysis completed for Player #{player_id}",
        "telemetry": telemetry
    }

@app.get("/api/speed-test/{player_id}")
def get_player_speed_test(player_id: str):
    speed_db = load_json_file("speed_results.json")
    player_speed = speed_db.get(str(player_id))
    if not player_speed:
        return {
            "player_id": str(player_id),
            "status": "no_test_record",
            "maximum_speed_kmh": 0.0,
            "average_speed_kmh": 0.0,
            "sprint_duration_seconds": 0.0,
            "peak_acceleration_mps2": 0.0
        }
    return {
        "player_id": str(player_id),
        "status": "recorded",
        "telemetry": player_speed
    }

@app.get("/api/players")
def get_all_players():
    roster = load_roster_config()
    performance = load_json_file("performance_scores.json")
    speed = load_json_file("speed_results.json")
    tackles = load_json_file("tackle_results.json")
    movement = load_json_file("movement_results.json")

    roster_players = roster.get("players", {})
    player_keys = set(roster_players.keys())

    result = []
    for pid in sorted(player_keys, key=lambda x: int(x) if x.isdigit() else 999):
        p_roster = get_player_roster_info(pid, roster)
        p_perf = performance.get(pid, {})
        perf_score = p_perf.get("performance_score", 75.0) if isinstance(p_perf, dict) else float(p_perf) if isinstance(p_perf, (int, float)) else 70.0
        
        p_speed = speed.get(pid, {})
        avg_speed = p_speed.get("average_speed", 5.2) if isinstance(p_speed, dict) else 5.2
        max_speed = p_speed.get("maximum_speed", 24.5) if isinstance(p_speed, dict) else 24.5
        
        p_tackle = tackles.get(pid, {
            "tackles_attempted": 0, "tackles_won": 0, "tackle_success_rate": 0.0,
            "interceptions": 0, "defensive_duels": 0, "duels_won": 0, "pressures": 0, "defensive_rating": 0.0
        })
        
        dist = movement.get(pid, 0.0)
        if isinstance(dist, dict):
            dist = dist.get("total_movement", 0.0)
            
        result.append({
            "player_id": pid,
            "name": p_roster.get("name", f"Player #{pid}"),
            "jersey_number": p_roster.get("jersey_number", int(pid) if pid.isdigit() else 99),
            "team": p_roster.get("team", "Team A"),
            "position": p_roster.get("position", "Midfielder"),
            "photo_url": p_roster.get("photo_path", ""),
            "notes": p_roster.get("notes", ""),
            "performance_score": round(float(perf_score), 1),
            "average_speed_kmh": round(float(avg_speed), 2),
            "maximum_speed_kmh": round(float(max_speed), 2),
            "distance_meters": round(float(dist), 1),
            "tackles_won": p_tackle.get("tackles_won", 0),
            "tackles_attempted": p_tackle.get("tackles_attempted", 0),
            "tackle_success_rate": p_tackle.get("tackle_success_rate", 0.0),
            "defensive_rating": p_tackle.get("defensive_rating", 0.0)
        })
        
    return {"players": result, "total": len(result)}

@app.get("/api/players/{player_id}")
def get_player_details(player_id: str):
    roster = load_roster_config()
    p_roster = get_player_roster_info(player_id, roster)
    
    perf = load_json_file("performance_scores.json").get(player_id, {})
    speed = load_json_file("speed_results.json").get(player_id, {})
    accel = load_json_file("acceleration_results.json").get(player_id, {})
    zones = load_json_file("zone_results.json").get(player_id, {})
    ai = load_json_file("ai_insights.json").get(player_id, {})
    nutrition = load_json_file("nutrition_recommendations.json").get(player_id, {})
    tackles = load_json_file("tackle_results.json").get(player_id, {
        "tackles_attempted": 0, "tackles_won": 0, "tackle_success_rate": 0.0,
        "interceptions": 0, "defensive_duels": 0, "duels_won": 0, "pressures": 0, "defensive_rating": 0.0
    })
    
    return {
        "player_id": player_id,
        "roster": p_roster,
        "performance": perf,
        "speed": speed,
        "acceleration": accel,
        "zones": zones,
        "tackles": tackles,
        "ai_insights": ai,
        "nutrition": nutrition
    }

@app.get("/api/events")
def get_events():
    events_data = load_json_file("event_detection.json")
    return events_data

@app.get("/api/match-report")
def get_match_report():
    return load_json_file("match_report.json")

@app.get("/api/team-classification")
def get_team_classification():
    return load_json_file("team_classification.json")

@app.get("/api/detections")
def get_detection_engines():
    tracking = load_json_file("tracking_results.json")
    ball = load_json_file("ball_results.json")
    team_cls = load_json_file("team_classification.json")
    tackles = load_json_file("tackle_results.json")
    events = load_json_file("event_detection.json")
    roster = load_roster_config()
    det_metrics = load_json_file("detection_metrics.json")

    # Total players from last-processed frame
    total_players = len(tracking.get("frames", [{}])[0].get("players", [])) if tracking.get("frames") else 0
    if total_players == 0:
        total_players = det_metrics.get("unique_track_ids", len(roster.get("players", {})))

    total_duels = sum(p.get("defensive_duels", 0) for p in tackles.values() if isinstance(p, dict))

    # ── Real detection metrics (no hardcoded values) ──────────────────────
    mean_conf       = det_metrics.get("mean_detection_confidence", None)
    track_stability = det_metrics.get("track_stability_ratio", None)
    frames_processed = det_metrics.get("frames_processed", 0)
    total_detections = det_metrics.get("total_detections", 0)
    unique_ids       = det_metrics.get("unique_track_ids", total_players)
    ball_speed_available = ball.get("ball_speed_available", False)
    max_ball_spd = ball.get("maximum_ball_speed_kmh", None)

    # Compose a plain-language accuracy summary
    if mean_conf is not None:
        accuracy_summary = {
            "mean_detection_confidence": round(mean_conf, 3),
            "track_stability_ratio":     round(track_stability or 0.0, 3),
            "unique_players_tracked":    unique_ids,
            "total_detections":          total_detections,
            "frames_processed":          frames_processed,
            "note": (
                "These metrics are computed from actual YOLO detection confidences and "
                "ByteTrack persistence — not hardcoded or invented values."
            ),
        }
    else:
        accuracy_summary = {
            "note": "No pipeline run yet. Execute video analysis to see real metrics."
        }

    return {
        "status": "online",
        "overall_accuracy": accuracy_summary,
        "engines": [
            {
                "id":           "player_tracking",
                "name":         "1. Multi-Object Player Tracking",
                "algorithm":    "YOLOv11 Deep Learning + ByteTrack",
                "status":       "Active",
                "metric_label": "Players Tracked",
                "metric_value": f"{unique_ids} unique track IDs",
                "metric_confidence": (
                    f"Mean confidence: {mean_conf:.2f}" if mean_conf is not None
                    else "Run pipeline to calculate"
                ),
                "features": ["Persistent ByteTrack IDs", "Per-frame bounding box", "MOG2 fallback"],
            },
            {
                "id":           "team_classification",
                "name":         "2. Jersey & Team Classification",
                "algorithm":    "HSV Upper Torso ROI + K-Means (k=2)",
                "status":       "Active",
                "metric_label": "Teams Classified",
                "metric_value": (
                    f"{team_cls.get('team_a_name','Team A')} vs {team_cls.get('team_b_name','Team B')}"
                    if team_cls else "Run pipeline to classify"
                ),
                "features": ["Accumulated colour samples", "K-Means clustering", "No hardcoded team colours"],
            },
            {
                "id":           "tackle_detection",
                "name":         "3. Defensive Tackle & Duel Engine",
                "algorithm":    "Spatial Proximity Modelling (< 2.0 m) + Deceleration",
                "status":       "Active",
                "metric_label": "Defensive Engagements",
                "metric_value": f"{total_duels} duels evaluated" if total_duels else "Run pipeline",
                "features": ["1-on-1 Tackle Detection", "Interception Tracking", "Defensive Ratings"],
            },
            {
                "id":           "ball_tracking",
                "name":         "4. Ball Detection & Speed",
                "algorithm":    "YOLO COCO class 32 + Physics-checked velocity",
                "status":       "Active",
                "metric_label": "Ball Speed",
                "metric_value": (
                    f"Peak {max_ball_spd} km/h (real YOLO detections)"
                    if ball_speed_available and max_ball_spd
                    else "Ball speed unavailable — no real ball detections"
                ),
                "features": ["No synthetic ball speed", "Confidence-filtered positions", "Temporal propagation"],
            },
            {
                "id":           "pitch_homography",
                "name":         "5. Pitch Speed & Distance (km/h / m)",
                "algorithm":    "Pixel → 105 m × 68 m pitch projection",
                "status":       "Active",
                "metric_label": "Tracking Quality",
                "metric_value": (
                    f"Track stability: {track_stability:.1%}"
                    if track_stability is not None else "Run pipeline"
                ),
                "features": [
                    "No *12 projection multiplier",
                    "No 14 km/h ceiling",
                    "Physics cap: 36 km/h",
                    "Step sanity check (>4 m filtered)",
                ],
            },
            {
                "id":           "event_detection",
                "name":         "6. Match Event & Sprint Detection",
                "algorithm":    "Threshold-based sprint detection (>= 24 km/h)",
                "status":       "Active",
                "metric_label": "Key Events",
                "metric_value": f"{len(events.get('events', []))} sprint events detected",
                "features": ["Based on real tracked speed", "No hardcoded event counts"],
            },
        ],
    }

@app.get("/api/studio/telemetry")
def get_studio_telemetry():
    tracking = load_json_file("tracking_results.json")
    speed = load_json_file("speed_results.json")
    distance = load_json_file("distance_analysis.json")
    ball = load_json_file("ball_results.json")
    roster = load_roster_config()
    team_cls = load_json_file("team_classification.json")
    tackles = load_json_file("tackle_results.json")
    events = load_json_file("event_detection.json")
    homography = load_json_file("homography_positions.json")
    
    existing_videos = [f for f in os.listdir(VIDEOS_DIR) if f.endswith(('.mp4', '.mov', '.avi'))]
    video_name = existing_videos[0] if existing_videos else "football.mp4"
    
    return {
        "tracking": tracking,
        "speed": speed,
        "distance": distance,
        "ball": ball,
        "roster": roster,
        "team_classification": team_cls,
        "tackles": tackles,
        "events": events,
        "homography": homography,
        "active_video_url": f"/static/videos/{video_name}",
        "annotated_video_url": "/static/results/annotated_match.mp4"
    }

@app.post("/api/process-video")
async def process_video(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    conf_thresh: float = Form(0.5)
):
    target_path = os.path.join(VIDEOS_DIR, "football.mp4")
    
    if file and file.filename:
        target_path = os.path.join(VIDEOS_DIR, file.filename)
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    else:
        # Check if default video exists in videos directory
        existing_videos = [f for f in os.listdir(VIDEOS_DIR) if f.endswith(('.mp4', '.mov', '.avi'))]
        if existing_videos:
            target_path = os.path.join(VIDEOS_DIR, existing_videos[0])

    # Trigger background pipeline execution
    background_tasks.add_task(run_full_ai_pipeline, target_path, conf_thresh)
    
    return {
        "status": "processing_started",
        "message": "AI Computer Vision pipeline launched in background.",
        "video_target": target_path
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
