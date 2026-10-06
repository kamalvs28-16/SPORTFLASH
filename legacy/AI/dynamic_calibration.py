import json
import math
import os
import numpy as np

CAMERA_FILE = "results/camera_motion.json"
HOMOGRAPHY_FILE = "results/homography_positions.json"
OUTPUT_FILE = "results/dynamic_calibration.json"

# Camera motion was calculated every 5 frames.
FRAME_STEP = 5

# Ignore extremely unreliable optical-flow estimates.
MIN_INLIERS = 30

print("=" * 60)
print("SPORTFLASH DYNAMIC CALIBRATION")
print("=" * 60)

# ---------------------------------------------------------
# 1. Load camera motion
# ---------------------------------------------------------

print("\nLoading camera motion data...")

with open(CAMERA_FILE, "r") as f:
    camera_data = json.load(f)

camera_frames = camera_data.get("frames", [])

if not camera_frames:
    raise ValueError("No camera motion frames found.")

print(f"Camera motion records: {len(camera_frames)}")

# ---------------------------------------------------------
# 2. Build camera-motion lookup
# ---------------------------------------------------------

camera_lookup = {}

for item in camera_frames:

    frame = int(item["frame"])

    inliers = int(item.get("inlier_points", 0))

    # Mark low-quality optical-flow estimates.
    reliable = inliers >= MIN_INLIERS

    camera_lookup[frame] = {
        "movement_x_pixels": float(item.get("movement_x_pixels", 0.0)),
        "movement_y_pixels": float(item.get("movement_y_pixels", 0.0)),
        "translation_magnitude_pixels": float(
            item.get("translation_magnitude_pixels", 0.0)
        ),
        "rotation_degrees": float(item.get("rotation_degrees", 0.0)),
        "scale_change": float(item.get("scale_change", 0.0)),
        "inlier_points": inliers,
        "motion_type": item.get("motion_type", "unknown"),
        "reliable": reliable
    }

# ---------------------------------------------------------
# 3. Find nearest camera-motion record
# ---------------------------------------------------------

camera_frame_numbers = sorted(camera_lookup.keys())


def nearest_camera_frame(frame_number):

    # Camera motion exists approximately every 5 frames.
    nearest = min(
        camera_frame_numbers,
        key=lambda x: abs(x - frame_number)
    )

    return nearest


# ---------------------------------------------------------
# 4. Load homography positions
# ---------------------------------------------------------

print("\nLoading homography positions...")

with open(HOMOGRAPHY_FILE, "r") as f:
    homography_data = json.load(f)

homography_frames = homography_data.get("frames", [])

if not homography_frames:
    raise ValueError("No homography frames found.")

print(f"Homography frames: {len(homography_frames)}")

# ---------------------------------------------------------
# 5. Calculate cumulative camera motion
# ---------------------------------------------------------

print("\nCalculating cumulative camera movement...")

cumulative_x = 0.0
cumulative_y = 0.0
cumulative_rotation = 0.0

cumulative_motion = {}

for camera_frame in camera_frame_numbers:

    motion = camera_lookup[camera_frame]

    # Only accumulate reliable optical-flow estimates.
    if motion["reliable"]:

        cumulative_x += motion["movement_x_pixels"]
        cumulative_y += motion["movement_y_pixels"]
        cumulative_rotation += motion["rotation_degrees"]

    cumulative_motion[camera_frame] = {
        "cumulative_x_pixels": cumulative_x,
        "cumulative_y_pixels": cumulative_y,
        "cumulative_rotation_degrees": cumulative_rotation
    }

# ---------------------------------------------------------
# 6. Dynamic calibration
# ---------------------------------------------------------

print("\nApplying dynamic calibration...")

output_frames = []

total_players = 0
reliable_camera_matches = 0
unreliable_camera_matches = 0

for frame_data in homography_frames:

    frame_number = int(frame_data["frame"])

    nearest_frame = nearest_camera_frame(frame_number)

    motion = camera_lookup[nearest_frame]
    cumulative = cumulative_motion[nearest_frame]

    if motion["reliable"]:
        reliable_camera_matches += 1
    else:
        unreliable_camera_matches += 1

    calibrated_players = []

    for player in frame_data.get("players", []):

        total_players += 1

        image_x = float(player["image_x"])
        image_y = float(player["image_y"])

        original_x = float(player["pitch_x_m"])
        original_y = float(player["pitch_y_m"])

        # -------------------------------------------------
        # IMPORTANT:
        # We do NOT pretend pixel movement can directly
        # be converted into metres.
        #
        # Instead, this module records camera-motion
        # information alongside the existing homography
        # position.
        # -------------------------------------------------

        calibrated_players.append({
            "player_id": int(player["player_id"]),

            "image_x": round(image_x, 3),
            "image_y": round(image_y, 3),

            "original_pitch_x_m": round(original_x, 3),
            "original_pitch_y_m": round(original_y, 3),

            "camera_adjustment": {
                "nearest_camera_frame": nearest_frame,

                "movement_x_pixels": round(
                    motion["movement_x_pixels"], 3
                ),

                "movement_y_pixels": round(
                    motion["movement_y_pixels"], 3
                ),

                "translation_magnitude_pixels": round(
                    motion["translation_magnitude_pixels"], 3
                ),

                "rotation_degrees": round(
                    motion["rotation_degrees"], 4
                ),

                "scale_change": round(
                    motion["scale_change"], 6
                ),

                "motion_type": motion["motion_type"],

                "inlier_points": motion["inlier_points"],

                "reliable": motion["reliable"]
            },

            "cumulative_camera_motion": {
                "x_pixels": round(
                    cumulative["cumulative_x_pixels"], 3
                ),

                "y_pixels": round(
                    cumulative["cumulative_y_pixels"], 3
                ),

                "rotation_degrees": round(
                    cumulative["cumulative_rotation_degrees"], 4
                )
            }
        })

    output_frames.append({
        "frame": frame_number,
        "camera_reference_frame": nearest_frame,
        "camera_motion_reliable": motion["reliable"],
        "players": calibrated_players
    })

# ---------------------------------------------------------
# 7. Save results
# ---------------------------------------------------------

output = {
    "video": camera_data.get("video", "videos/football.mp4"),

    "video_information": camera_data.get(
        "video_information",
        {}
    ),

    "method": {
        "camera_motion": (
            "Lucas-Kanade optical flow + "
            "RANSAC affine estimation"
        ),
        "homography": "four-point planar homography",
        "frame_alignment": "nearest camera-motion frame",
        "minimum_camera_inliers": MIN_INLIERS,
        "purpose": (
            "Align camera motion information with "
            "player homography positions"
        )
    },

    "summary": {
        "homography_frames": len(homography_frames),
        "camera_motion_frames": len(camera_frames),
        "total_player_positions": total_players,
        "reliable_camera_matches": reliable_camera_matches,
        "unreliable_camera_matches": unreliable_camera_matches
    },

    "camera_motion_summary": camera_data.get(
        "summary",
        {}
    ),

    "frames": output_frames
}

os.makedirs("results", exist_ok=True)

with open(OUTPUT_FILE, "w") as f:
    json.dump(output, f, indent=2)

# ---------------------------------------------------------
# 8. Final summary
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("DYNAMIC CALIBRATION SUMMARY")
print("=" * 60)

print(f"\nHomography frames          : {len(homography_frames)}")
print(f"Camera motion frames      : {len(camera_frames)}")
print(f"Player positions          : {total_players}")

print(
    f"Reliable camera matches   : "
    f"{reliable_camera_matches}"
)

print(
    f"Unreliable camera matches : "
    f"{unreliable_camera_matches}"
)

print(f"\nOutput file:")
print(f"✓ {OUTPUT_FILE}")

print("\nDynamic calibration completed.")
print("\nIMPORTANT:")
print(
    "This module aligns camera motion with homography "
    "data. It does not directly convert camera pixels "
    "into metres."
)

print("\nNext step:")
print("Verify results/dynamic_calibration.json")