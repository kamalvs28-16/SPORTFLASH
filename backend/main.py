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
