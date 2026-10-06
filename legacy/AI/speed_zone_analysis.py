import cv2
import json
import math
from collections import defaultdict
from ultralytics import YOLO


# ============================================================
# SPORTFLASH - SPEED ZONE ANALYSIS
# ============================================================

VIDEO_PATH = r"E:\SPORTFLASH\videos\football.mp4"
MODEL_PATH = "yolo11n.pt"
OUTPUT_PATH = r"E:\SPORTFLASH\results\speed_zone_results.json"

CONFIDENCE = 0.5

# Ignore unrealistic tracking jumps
MAX_POSITION_JUMP = 100


# ============================================================
# SPEED ZONE DEFINITIONS
# ============================================================
#
# IMPORTANT:
# These are IMAGE-SPEED thresholds in pixels/second.
# They are suitable for the current prototype.
#
# Later, after field calibration/homography,
# these can be changed to real-world speed thresholds.
#
# ============================================================

SPEED_ZONES = {
    "walking": (0, 100),
    "jogging": (100, 250),
    "running": (250, 500),
    "high_speed": (500, 750),
    "sprint": (750, float("inf"))
}


# ============================================================
# LOAD YOLO MODEL
# ============================================================

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("YOLO model loaded successfully.")


# ============================================================
# OPEN VIDEO
# ============================================================

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():

    print("ERROR: Could not open football video.")

    exit()


fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30


print(f"Video FPS: {fps}")


# ============================================================
# DATA STORAGE
# ============================================================

previous_positions = {}

zone_counts = defaultdict(
    lambda: {
        "walking": 0,
        "jogging": 0,
        "running": 0,
        "high_speed": 0,
        "sprint": 0
    }
)

total_speed_samples = defaultdict(int)

speed_values = defaultdict(list)


frame_number = 0


# ============================================================
# FUNCTION: CLASSIFY SPEED
# ============================================================

def get_speed_zone(speed):

    for zone_name, (minimum, maximum) in SPEED_ZONES.items():

        if minimum <= speed < maximum:

            return zone_name

    return "walking"


# ============================================================
# PROCESS VIDEO
# ============================================================

print()
print("Starting speed zone analysis...")
print("Please wait while the video is processed.")
print()


while True:

    success, frame = cap.read()

    if not success:
        break

    frame_number += 1


    # --------------------------------------------------------
    # YOLO TRACKING
    # --------------------------------------------------------

    results = model.track(
        frame,
        persist=True,
        classes=[0],
        conf=CONFIDENCE,
        verbose=False
    )


    if not results:
        continue


    result = results[0]


    if result.boxes is None:
        continue


    if result.boxes.id is None:
        continue


    boxes = result.boxes.xyxy.cpu().numpy()

    track_ids = (
        result.boxes.id
        .int()
        .cpu()
        .tolist()
    )


    current_positions = {}


    # --------------------------------------------------------
    # GET PLAYER CENTERS
    # --------------------------------------------------------

    for box, player_id in zip(
        boxes,
        track_ids
    ):

        x1, y1, x2, y2 = box

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        current_positions[player_id] = (
            center_x,
            center_y
        )


    # --------------------------------------------------------
    # CALCULATE SPEED
    # --------------------------------------------------------

    for player_id, current_position in current_positions.items():

        if player_id not in previous_positions:

            previous_positions[player_id] = current_position

            continue


        previous_position = previous_positions[player_id]


        dx = (
            current_position[0]
            - previous_position[0]
        )

        dy = (
            current_position[1]
            - previous_position[1]
        )


        distance = math.sqrt(
            dx ** 2 + dy ** 2
        )


        # ----------------------------------------------------
        # REMOVE TRACKING JUMPS
        # ----------------------------------------------------

        if distance > MAX_POSITION_JUMP:

            previous_positions[player_id] = (
                current_position
            )

            continue


        # ----------------------------------------------------
        # PIXELS / SECOND
        # ----------------------------------------------------

        speed = distance * fps


        # Store speed
        speed_values[player_id].append(speed)


        # ----------------------------------------------------
        # CLASSIFY SPEED ZONE
        # ----------------------------------------------------

        zone = get_speed_zone(speed)


        zone_counts[player_id][zone] += 1

        total_speed_samples[player_id] += 1


        # Update previous position
        previous_positions[player_id] = (
            current_position
        )


# ============================================================
# CLOSE VIDEO
# ============================================================

cap.release()


print()
print("Video processing completed.")
print()


# ============================================================
# CREATE FINAL RESULTS
# ============================================================

final_results = {}


for player_id in sorted(zone_counts.keys()):

    player_zones = zone_counts[player_id]

    total_samples = total_speed_samples[player_id]


    if total_samples == 0:
        continue


    # --------------------------------------------------------
    # CALCULATE PERCENTAGES
    # --------------------------------------------------------

    walking_percentage = (
        player_zones["walking"]
        / total_samples
    ) * 100


    jogging_percentage = (
        player_zones["jogging"]
        / total_samples
    ) * 100


    running_percentage = (
        player_zones["running"]
        / total_samples
    ) * 100


    high_speed_percentage = (
        player_zones["high_speed"]
        / total_samples
    ) * 100


    sprint_percentage = (
        player_zones["sprint"]
        / total_samples
    ) * 100


    # --------------------------------------------------------
    # AVERAGE SPEED
    # --------------------------------------------------------

    player_speed_values = speed_values[player_id]


    if player_speed_values:

        average_speed = (
            sum(player_speed_values)
            / len(player_speed_values)
        )

        maximum_speed = max(
            player_speed_values
        )

    else:

        average_speed = 0

        maximum_speed = 0


    # --------------------------------------------------------
    # FIND DOMINANT ZONE
    # --------------------------------------------------------

    dominant_zone = max(
        player_zones,
        key=player_zones.get
    )


    # --------------------------------------------------------
    # SAVE PLAYER RESULT
    # --------------------------------------------------------

    final_results[str(player_id)] = {

        "average_speed_pixels_per_second":
            round(
                average_speed,
                2
            ),

        "maximum_speed_pixels_per_second":
            round(
                maximum_speed,
                2
            ),

        "dominant_speed_zone":
            dominant_zone,

        "total_speed_samples":
            total_samples,

        "zones": {

            "walking": {
                "samples":
                    player_zones["walking"],

                "percentage":
                    round(
                        walking_percentage,
                        2
                    )
            },

            "jogging": {
                "samples":
                    player_zones["jogging"],

                "percentage":
                    round(
                        jogging_percentage,
                        2
                    )
            },

            "running": {
                "samples":
                    player_zones["running"],

                "percentage":
                    round(
                        running_percentage,
                        2
                    )
            },

            "high_speed": {
                "samples":
                    player_zones["high_speed"],

                "percentage":
                    round(
                        high_speed_percentage,
                        2
                    )
            },

            "sprint": {
                "samples":
                    player_zones["sprint"],

                "percentage":
                    round(
                        sprint_percentage,
                        2
                    )
            }
        }
    }


# ============================================================
# SAVE JSON
# ============================================================

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        final_results,
        file,
        indent=4
    )


# ============================================================
# FINAL MESSAGE
# ============================================================

print("==============================================")
print("       SPEED ZONE ANALYSIS COMPLETED")
print("==============================================")

print(
    f"Players analyzed: "
    f"{len(final_results)}"
)

print(
    f"Output file: "
    f"{OUTPUT_PATH}"
)

print("==============================================")