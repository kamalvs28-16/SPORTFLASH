import os
import json
import cv2
import time
import numpy as np
from typing import Dict, Any, Optional, List
from collections import defaultdict

from pipeline.config import RESULTS_DIR, VIDEOS_DIR, PITCH_MASK_ENABLED
from pipeline.schemas import CanonicalTrackFrame, CanonicalTrackRow
from core.detection import FootballDetector
from core.tracking import ByteTrackTracker
from core.ball import BallTracker
from core.scene_cuts import SceneCutDetector
from core.teams import TeamClassifier, RosterIdentityLinker
from core.calibration import PitchCalibrator
from tools.debug_overlay import DebugOverlayRenderer
from tools.evaluate import evaluate_phase1_metrics, evaluate_team_classification_50_crops

from analytics.kinematics import KinematicsAnalyzer
from analytics.positional import PositionalAnalyzer
from analytics.defensive import DefensiveAnalyzer
from analytics.technical import TechnicalAnalyzer
from analytics.events import MatchEventAnalyzer
from analytics.scoring import CompositeScoreEngine
from analytics.insights import CoachInsightsEngine
from analytics.nutrition import RecoveryNutritionEngine


def run_full_pipeline(
    video_path: str,
    output_video_path: str = os.path.join(RESULTS_DIR, "annotated_match.mp4"),
    output_json_path: str = os.path.join(RESULTS_DIR, "canonical_tracks.json"),
    max_frames: int = 900
) -> Dict[str, Any]:
    """
    End-to-end SPORTFLASH Rebuild Pipeline Orchestrator (Phases 1-4).
    1. Pitch-Masked YOLO11m Object Detection @ 1280px
    2. ByteTrack Multi-Object Player Tracking
    3. Dedicated Ball Detection & Kalman Filter Interpolation
    4. Scene Cut & Replay Detection
    5. Pitch Homography Calibration & Reprojection Error Filtering
    6. Torso HSV K-Means Team Clustering & Roster Identity Linking
    7. Single Source of Truth Canonical Track Export
    8. Physical, Positional, Defensive, Technical & Composite Scoring Analytics
    """
    if not os.path.exists(video_path):
        existing_videos = [f for f in os.listdir(VIDEOS_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
        if existing_videos:
            video_path = os.path.join(VIDEOS_DIR, existing_videos[0])
        else:
            raise FileNotFoundError(f"Video file not found at: {video_path}")

    print(f"[INFO] Launching SPORTFLASH End-to-End Pipeline on: {os.path.basename(video_path)}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {video_path}")

    total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1000
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720

    # Load Roster Configuration
    roster_path = os.path.join(RESULTS_DIR, "roster_config.json")
    roster_config = {}
    if os.path.exists(roster_path):
        try:
            with open(roster_path, "r", encoding="utf-8") as f:
                roster_config = json.load(f)
        except Exception:
            pass

    # Initialize Core Modules
    detector = FootballDetector(imgsz=1280)
    tracker = ByteTrackTracker()
    ball_tracker = BallTracker()
    scene_detector = SceneCutDetector()
    team_classifier = TeamClassifier()
    identity_linker = RosterIdentityLinker(roster_config)
    calibrator = PitchCalibrator()
    renderer = DebugOverlayRenderer()

    # Initialize Analytics Engines
    kinematics_engine = KinematicsAnalyzer(fps=fps)
    positional_engine = PositionalAnalyzer()
    defensive_engine = DefensiveAnalyzer()
    technical_engine = TechnicalAnalyzer()
    events_engine = MatchEventAnalyzer()
    scoring_engine = CompositeScoreEngine()
    insights_engine = CoachInsightsEngine()
    nutrition_engine = RecoveryNutritionEngine()

    # Video Writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    canonical_frames = []
    player_trajectories = defaultdict(list)
    ball_trajectory = []

    frame_idx = 0
    process_limit = min(total_video_frames, max_frames)
    start_time = time.time()

    while frame_idx < process_limit:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        time_sec = round(frame_idx / fps, 3)

        # 1. Scene Cut & Replay Detection
        is_cut, scene_id, is_replay = scene_detector.process_frame(frame, frame_idx)
        if is_cut:
            tracker.reset()

        # 2. Pitch Masked Object Detection
        player_dets, raw_ball_det, pitch_mask = detector.detect(frame)

        # 3. Pitch Homography Calibration & Error Checking
        H, reproj_err, is_calib_valid = calibrator.estimate_frame_homography(frame, pitch_mask)

        # 4. Persistent ByteTrack Player Tracking
        tracked_players = tracker.update(player_dets, frame_idx)

        # 5. Map Player Anchor Points -> Pitch Metric Coordinates (x_m, y_m)
        for tp in tracked_players:
            tp["pitch_xy"] = calibrator.pixel_to_pitch(tp["pixel_xy"], H) if is_calib_valid else None
            team_classifier.add_sample(tp["track_id"], frame, tp["bbox"])
            player_trajectories[tp["track_id"]].append({
                "frame": frame_idx,
                "time": time_sec,
                "pixel_xy": tp["pixel_xy"],
                "pitch_xy": tp["pitch_xy"],
                "confidence": tp["confidence"]
            })

        # 6. Dedicated Ball Kalman Tracking & Short-Gap Interpolation
        tracked_ball = ball_tracker.process_frame(raw_ball_det, frame_idx)
        if tracked_ball is not None:
            tracked_ball["pitch_xy"] = calibrator.pixel_to_pitch(tracked_ball["pixel_xy"], H) if is_calib_valid else None
            ball_trajectory.append({
                "frame": frame_idx,
                "time": time_sec,
                "pixel_xy": tracked_ball["pixel_xy"],
                "pitch_xy": tracked_ball["pitch_xy"],
                "is_interpolated": tracked_ball.get("is_interpolated", False)
            })

        # 7. Render Debug Overlay Frame with Top-Down Minimap
        debug_frame = renderer.render_frame(
            frame=frame,
            players=tracked_players,
            ball=tracked_ball,
            ball_trail=ball_tracker.trail,
            pitch_mask=pitch_mask if PITCH_MASK_ENABLED else None,
            reproj_error=reproj_err,
            frame_idx=frame_idx,
            fps=fps,
            scene_id=scene_id,
            is_replay=is_replay
        )
        out_writer.write(debug_frame)

        # 8. Construct Canonical Track Frame
        frame_player_rows = [
            CanonicalTrackRow(
                frame=frame_idx,
                time=time_sec,
                track_id=tp["track_id"],
                player_id=str(tp["track_id"]),
                team="unknown",
                role=tp.get("role", "player"),
                bbox=tp["bbox"],
                pixel_xy=tp["pixel_xy"],
                pitch_xy=tp.get("pitch_xy"),
                confidence=tp["confidence"] if is_calib_valid else round(tp["confidence"] * 0.7, 2),
                is_interpolated=False,
                is_replay=is_replay,
                scene_id=scene_id
            )
            for tp in tracked_players
        ]

        frame_ball_row = (
            CanonicalTrackRow(
                frame=frame_idx,
                time=time_sec,
                track_id=9999,
                player_id=None,
                team="ball",
                role="ball",
                bbox=tracked_ball["bbox"],
                pixel_xy=tracked_ball["pixel_xy"],
                pitch_xy=tracked_ball.get("pitch_xy"),
                confidence=tracked_ball["confidence"],
                is_interpolated=tracked_ball.get("is_interpolated", False),
                is_replay=is_replay,
                scene_id=scene_id
            )
            if tracked_ball is not None else None
        )

        canonical_frames.append({
            "frame": frame_idx,
            "time": time_sec,
            "scene_id": scene_id,
            "is_replay": is_replay,
            "reproj_error_meters": round(reproj_err, 3),
            "calibration_valid": is_calib_valid,
            "players": [p.dict() for p in frame_player_rows],
            "ball": frame_ball_row.dict() if frame_ball_row else None
        })

    cap.release()
    out_writer.release()

    # 9. Team Clustering & Roster Identity Link
    team_assignments, role_assignments = team_classifier.fit_and_classify()
    linked_identities = identity_linker.link_tracks(team_assignments)

    for f_data in canonical_frames:
        for p in f_data["players"]:
            tid = p["track_id"]
            p_info = linked_identities.get(tid, {})
            p["team"] = p_info.get("team", "Team A")
            p["player_id"] = p_info.get("player_id", str(tid))
            p["role"] = role_assignments.get(tid, "player")

    # Export Canonical Tracks File
    canonical_output = {
        "video": video_path,
        "width": width,
        "height": height,
        "fps": fps,
        "total_frames": len(canonical_frames),
        "calibration_stats": calibrator.get_calibration_stats(),
        "roster_linked_players": linked_identities,
        "frames": canonical_frames
    }
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(canonical_output, f, indent=2)

    # 10. Run Analytics Engines Reading ONLY from Canonical Trajectories (Rule 4)
    speed_results = {}
    distance_results = {}
    speed_zone_results = {}
    tackle_results = {}
    performance_scores = {}
    ai_insights = {}
    nutrition_recommendations = {}
    all_match_events = []

    opp_trajectories_list = [player_trajectories[tid] for tid in player_trajectories.keys()]

    for tid, traj in player_trajectories.items():
        str_pid = linked_identities.get(tid, {}).get("player_id", str(tid))

        # Kinematics
        kin, k_badge = kinematics_engine.analyze_player_trajectory(str_pid, traj)
        # Positional
        pos, p_badge = positional_engine.analyze_positional(str_pid, traj)
        # Defensive
        defen, d_badge = defensive_engine.analyze_defensive(str_pid, traj, opp_trajectories_list)
        # Technical
        tech, t_badge = technical_engine.analyze_technical(str_pid, traj, ball_trajectory)
        # Events
        evts, e_badge = events_engine.analyze_events(str_pid, kin, pos)
        # Composite Score
        comp, c_badge = scoring_engine.compute_composite_score(str_pid, kin, pos, defen, tech)
        # Insights
        ins, i_badge = insights_engine.generate_insights(str_pid, kin, pos, defen, comp)
        # Nutrition
        nut, n_badge = nutrition_engine.calculate_nutrition_guidance(str_pid, kin)

        speed_results[str_pid] = {
            "average_speed": kin.get("average_speed_kmh", 0.0),
            "maximum_speed": kin.get("top_speed_kmh", 0.0),
            "unit": "km/h"
        }
        distance_results[str_pid] = kin.get("total_distance_meters", 0.0)
        speed_zone_results[str_pid] = kin.get("speed_zones", {})
        tackle_results[str_pid] = defen
        performance_scores[str_pid] = comp
        ai_insights[str_pid] = ins
        nutrition_recommendations[str_pid] = nut
        all_match_events.extend(evts)

    # Export Legacy Analytics JSON Files for API compatibility
    for fname, data in [
        ("speed_results.json", speed_results),
        ("distance_analysis.json", distance_results),
        ("speed_zone_results.json", speed_zone_results),
        ("tackle_results.json", tackle_results),
        ("performance_scores.json", performance_scores),
        ("ai_insights.json", ai_insights),
        ("nutrition_recommendations.json", nutrition_recommendations),
        ("event_detection.json", {"events": all_match_events}),
    ]:
        with open(os.path.join(RESULTS_DIR, fname), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # 11. Run Benchmark Evaluation
    eval_report = evaluate_phase1_metrics(output_json_path)
    eval_report["calibration_stats"] = calibrator.get_calibration_stats()
    eval_report["team_crop_evaluation"] = evaluate_team_classification_50_crops()

    elapsed = round(time.time() - start_time, 2)
    print(f"[SUCCESS] End-to-End Pipeline Completed in {elapsed}s.")
    return eval_report


if __name__ == "__main__":
    run_full_pipeline("videos/WhatsApp Video 2026-09-28 at 9.35.08 PM.mp4", max_frames=300)
