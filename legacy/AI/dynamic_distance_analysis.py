import json
import math
import os
from collections import defaultdict, deque

INPUT_FILE = "results/dynamic_calibration.json"
OUTPUT_FILE = "results/dynamic_distance_analysis.json"

# Physical plausibility limits
MAX_SPEED_KMH = 40.0
MAX_MOVEMENT_M = 2.0

# Smoothing window
SMOOTHING_WINDOW = 3

print("=" * 60)
print("SPORTFLASH DYNAMIC DISTANCE & SPEED ANALYSIS")
print("=" * 60)

# ---------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------

print("\nLoading dynamic calibration data...")

with open(INPUT_FILE, "r") as f:
    data = json.load(f)

fps = float(data["video_information"]["fps"])
frames = data["frames"]

print(f"FPS: {fps:.2f}")
print(f"Frames: {len(frames)}")

# ---------------------------------------------------------
# 2. Collect player positions
# ---------------------------------------------------------

print("\nCollecting player trajectories...")

players = defaultdict(list)

for frame_data in frames:

    frame_number = int(frame_data["frame"])

    for player in frame_data.get("players", []):

        if not player.get("camera_adjustment", {}).get("reliable", False):
            continue

        player_id = int(player["player_id"])

        x = float(player["original_pitch_x_m"])
        y = float(player["original_pitch_y_m"])

        players[player_id].append({
            "frame": frame_number,
            "x": x,
            "y": y
        })

print(f"Unique players: {len(players)}")

# ---------------------------------------------------------
# 3. Distance calculation
# ---------------------------------------------------------

results = []

for player_id, trajectory in players.items():

    trajectory.sort(key=lambda p: p["frame"])

    if len(trajectory) < 3:
        continue

    total_distance = 0.0
    valid_movements = 0
    rejected_movements = 0

    speeds = []

    # Store recent positions for simple median smoothing
    history = deque(maxlen=SMOOTHING_WINDOW)

    previous = None

    for point in trajectory:

        history.append(point)

        if previous is None:
            previous = point
            continue

        frame_gap = point["frame"] - previous["frame"]

        if frame_gap <= 0:
            continue

        elapsed_seconds = frame_gap / fps

        # ---------------------------------------------
        # Basic smoothing
        # ---------------------------------------------

        xs = [p["x"] for p in history]
        ys = [p["y"] for p in history]

        smooth_x = sorted(xs)[len(xs) // 2]
        smooth_y = sorted(ys)[len(ys) // 2]

        dx = smooth_x - previous["x"]
        dy = smooth_y - previous["y"]

        distance = math.sqrt(dx * dx + dy * dy)

        speed_mps = distance / elapsed_seconds
        speed_kmh = speed_mps * 3.6

        # ---------------------------------------------
        # Reject unrealistic movements
        # ---------------------------------------------

        if distance > MAX_MOVEMENT_M:
            rejected_movements += 1
            previous = point
            continue

        if speed_kmh > MAX_SPEED_KMH:
            rejected_movements += 1
            previous = point
            continue

        total_distance += distance
        speeds.append(speed_kmh)

        valid_movements += 1

        previous = point

    # -------------------------------------------------
    # Player statistics
    # -------------------------------------------------

    if valid_movements == 0:
        continue

    active_time = valid_movements / fps

    average_speed = (
        sum(speeds) / len(speeds)
        if speeds
        else 0.0
    )

    maximum_speed = (
        max(speeds)
        if speeds
        else 0.0
    )

    results.append({
        "player_id": player_id,
        "total_distance_m": round(total_distance, 2),
        "total_distance_km": round(total_distance / 1000, 4),
        "average_speed_kmh": round(average_speed, 2),
        "maximum_speed_kmh": round(maximum_speed, 2),
        "valid_movements": valid_movements,
        "rejected_movements": rejected_movements,
        "tracked_positions": len(trajectory),
        "active_time_seconds": round(active_time, 2)
    })

# ---------------------------------------------------------
# 4. Sort by distance
# ---------------------------------------------------------

results.sort(
    key=lambda x: x["total_distance_m"],
    reverse=True
)

# ---------------------------------------------------------
# 5. Save
# ---------------------------------------------------------

output = {
    "video": data.get(
        "video",
        "videos/football.mp4"
    ),

    "analysis": {
        "method": (
            "Dynamic calibration + "
            "trajectory smoothing + "
            "physical movement filtering"
        ),
        "fps": fps,
        "max_speed_kmh": MAX_SPEED_KMH,
        "max_movement_m": MAX_MOVEMENT_M,
        "smoothing_window": SMOOTHING_WINDOW
    },

    "summary": {
        "players_analysed": len(results),
        "total_players_detected": len(players)
    },

    "players": results
}

os.makedirs("results", exist_ok=True)

with open(OUTPUT_FILE, "w") as f:
    json.dump(output, f, indent=2)

# ---------------------------------------------------------
# 6. Display results
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("DYNAMIC DISTANCE ANALYSIS")
print("=" * 60)

for index, player in enumerate(results[:10], start=1):

    print(f"\n{index}. Player {player['player_id']}")

    print(
        f"   Distance: "
        f"{player['total_distance_m']:.2f} m"
    )

    print(
        f"   Average speed: "
        f"{player['average_speed_kmh']:.2f} km/h"
    )

    print(
        f"   Maximum speed: "
        f"{player['maximum_speed_kmh']:.2f} km/h"
    )

    print(
        f"   Valid movements: "
        f"{player['valid_movements']}"
    )

    print(
        f"   Rejected movements: "
        f"{player['rejected_movements']}"
    )

print("\n" + "=" * 60)
print("DYNAMIC DISTANCE ANALYSIS COMPLETED")
print("=" * 60)

print(f"\nPlayers analysed: {len(results)}")
print(f"Output file: ✓ {OUTPUT_FILE}")

print("\nIMPORTANT:")
print(
    "These measurements remain estimates because "
    "the camera-motion model does not directly "
    "recompute the homography for every frame."
)