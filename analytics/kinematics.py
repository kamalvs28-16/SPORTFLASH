import math
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

from pipeline.schemas import DataQualityBadge


class KinematicsAnalyzer:
    """
    Physical & Kinematic Analytics Engine.
    Consumes canonical tracks data to compute:
    - Total distance (meters) & Work rate (m/min)
    - Distance per speed zone (walking, jogging, running, high-speed, sprinting)
    - Average speed & Top speed (percentile 95)
    - Acceleration / Deceleration events
    - Fatigue trend (first vs last period physical output ratio)
    """

    SPEED_ZONES = {
        "walking":    (0.0, 7.0),     # km/h
        "jogging":    (7.0, 14.0),
        "running":    (14.0, 21.0),
        "high_speed": (21.0, 25.0),
        "sprinting":  (25.0, 36.0),
    }

    def __init__(self, fps: float = 30.0):
        self.fps = fps
        self.modified_values_log: List[str] = []
        self.modified_count = 0

    def analyze_player_trajectory(
        self, player_id: str, trajectory: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], DataQualityBadge]:
        """
        Analyzes pitch position trajectory [(frame, time, pitch_xy, confidence), ...]
        Returns kinematic metrics dictionary and DataQualityBadge.
        """
        # Filter out frames missing pitch_xy coordinates
        valid_pts = [
            pt for pt in trajectory
            if pt.get("pitch_xy") is not None and len(pt["pitch_xy"]) == 2
        ]

        if len(valid_pts) < 10:
            badge = DataQualityBadge(
                overall_confidence=0.0,
                data_quality="LOW",
                track_stability_ratio=0.0,
                modified_frame_count=0,
                modification_logs=["Insufficient valid pitch positions (<10 frames)"],
                has_sufficient_data=False
            )
            return {
                "player_id": player_id,
                "total_distance_meters": None,
                "average_speed_kmh": None,
                "top_speed_kmh": None,
                "sprint_count": None,
                "accelerations_count": None,
                "decelerations_count": None,
                "fatigue_trend_ratio": None,
                "speed_zones": None,
                "status": "insufficient_data"
            }, badge

        total_dist = 0.0
        speeds_kmh = []
        accels_mps2 = []
        confidence_scores = [pt.get("confidence", 0.8) for pt in valid_pts]

        zone_distances = {k: 0.0 for k in self.SPEED_ZONES.keys()}
        zone_counts = {k: 0 for k in self.SPEED_ZONES.keys()}

        for i in range(1, len(valid_pts)):
            prev = valid_pts[i - 1]
            curr = valid_pts[i]

            dt = max(0.02, curr["time"] - prev["time"])
            dx = curr["pitch_xy"][0] - prev["pitch_xy"][0]
            dy = curr["pitch_xy"][1] - prev["pitch_xy"][1]
            step_dist = math.sqrt(dx * dx + dy * dy)

            # Physics Filter: Usain Bolt peak ~12 m/s -> max step dist check
            v_mps = step_dist / dt
            v_kmh = v_mps * 3.6

            if v_kmh > 36.0:  # Physical ceiling
                self.modified_count += 1
                self.modified_values_log.append(f"Frame {curr['frame']}: Speed {v_kmh:.1f} km/h capped to 36.0")
                v_kmh = 36.0
                v_mps = 36.0 / 3.6
                step_dist = v_mps * dt

            total_dist += step_dist
            speeds_kmh.append(v_kmh)

            # Zone breakdown
            for zone_name, (low, high) in self.SPEED_ZONES.items():
                if low <= v_kmh < high:
                    zone_distances[zone_name] += step_dist
                    zone_counts[zone_name] += 1
                    break

            # Acceleration calculation
            if len(speeds_kmh) > 1:
                prev_v_mps = (speeds_kmh[-2]) / 3.6
                accel = (v_mps - prev_v_mps) / dt
                accels_mps2.append(accel)

        if not speeds_kmh:
            avg_speed = 0.0
            top_speed = 0.0
        else:
            avg_speed = float(np.mean(speeds_kmh))
            top_speed = float(np.percentile(speeds_kmh, 95))

        # Acceleration / Deceleration threshold count (>2.0 m/s^2)
        accel_count = sum(1 for a in accels_mps2 if a >= 2.0)
        decel_count = sum(1 for a in accels_mps2 if a <= -2.0)
        sprint_count = zone_counts["sprinting"]

        # Fatigue Trend: Work output ratio in first half vs second half of trajectory
        mid_idx = len(speeds_kmh) // 2
        first_half_avg = float(np.mean(speeds_kmh[:mid_idx])) if mid_idx > 0 else avg_speed
        second_half_avg = float(np.mean(speeds_kmh[mid_idx:])) if mid_idx > 0 else avg_speed
        fatigue_trend = round(second_half_avg / max(0.1, first_half_avg), 2)

        mean_conf = float(np.mean(confidence_scores))
        quality_label = "HIGH" if mean_conf >= 0.80 else "MEDIUM" if mean_conf >= 0.60 else "LOW"

        badge = DataQualityBadge(
            overall_confidence=round(mean_conf, 3),
            data_quality=quality_label,
            track_stability_ratio=round(len(valid_pts) / len(trajectory), 3),
            modified_frame_count=self.modified_count,
            modification_logs=self.modified_values_log[:10],
            has_sufficient_data=True
        )

        output = {
            "player_id": player_id,
            "total_distance_meters": round(total_dist, 1),
            "average_speed_kmh": round(avg_speed, 1),
            "top_speed_kmh": round(top_speed, 1),
            "sprint_count": sprint_count,
            "accelerations_count": accel_count,
            "decelerations_count": decel_count,
            "fatigue_trend_ratio": fatigue_trend,
            "speed_zones": {
                k: {
                    "distance_meters": round(zone_distances[k], 1),
                    "pct_time": round(100.0 * zone_counts[k] / max(1, len(speeds_kmh)), 1)
                }
                for k in self.SPEED_ZONES.keys()
            },
            "status": "valid"
        }

        return output, badge
