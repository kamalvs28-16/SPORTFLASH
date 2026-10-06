import cv2
import json
import math
from collections import defaultdict
from ultralytics import YOLO


# ==============================
# CONFIGURATION
# ==============================

VIDEO_PATH = r"E:\SPORTFLASH\videos\football.mp4"
MODEL_PATH = "yolo11n.pt"
OUTPUT_PATH = r"E:\SPORTFLASH\results\acceleration_results.json"

CONFIDENCE = 0.5

# Ignore very small position jumps caused by tracking noise
MAX_POSITION_JUMP = 100

# Minimum acceleration/deceleration magnitude
MIN_ACCELERATION = 0.5


# ==============================
# LOAD MODEL
# ==============================

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("Model loaded successfully.")


# ==============================
# OPEN VIDEO
# ==============================

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("ERROR: Could not open video.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30

print(f"Video FPS: {fps}")


# ==============================
# PLAYER DATA
# ==============================

# Stores previous position of every player
previous_positions = {}

# Stores previous speed of every player
previous_speeds = {}

# Acceleration samples
acceleration_data = defaultdict(list)

# Deceleration samples
deceleration_data = defaultdict(list)


frame_number = 0


# ==============================
# PROCESS VIDEO
# ==============================

print("Starting acceleration analysis...")

while True:

    success, frame = cap.read()

    if not success:
        break

    frame_number += 1

    # YOLO tracking
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
    track_ids = result.boxes.id.int().cpu().tolist()

    current_positions = {}

    # ==============================
    # GET PLAYER POSITIONS
    # ==============================

    for box, player_id in zip(boxes, track_ids):

        x1, y1, x2, y2 = box

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        current_positions[player_id] = (
            center_x,
            center_y
        )

    # ==============================
    # CALCULATE SPEED
    # ==============================

    for player_id, current_position in current_positions.items():

        if player_id not in previous_positions:
            previous_positions[player_id] = current_position
            continue

        previous_position = previous_positions[player_id]

        dx = current_position[0] - previous_position[0]
        dy = current_position[1] - previous_position[1]

        distance = math.sqrt(
            dx ** 2 + dy ** 2
        )

        # Ignore tracking jumps
        if distance > MAX_POSITION_JUMP:
            previous_positions[player_id] = current_position
            continue

        # Speed in pixels/second
        current_speed = distance * fps

        # ==============================
        # CALCULATE ACCELERATION
        # ==============================

        if player_id in previous_speeds:

            previous_speed = previous_speeds[player_id]

            acceleration = (
                current_speed - previous_speed
            ) * fps

            # Positive = acceleration
            if acceleration >= MIN_ACCELERATION:

                acceleration_data[player_id].append(
                    acceleration
                )

            # Negative = deceleration
            elif acceleration <= -MIN_ACCELERATION:

                deceleration_data[player_id].append(
                    abs(acceleration)
                )

        previous_speeds[player_id] = current_speed

        previous_positions[player_id] = current_position


# ==============================
# CLOSE VIDEO
# ==============================

cap.release()

print("Video processing completed.")


# ==============================
# CREATE FINAL RESULTS
# ==============================

final_results = {}

all_players = set(
    acceleration_data.keys()
).union(
    deceleration_data.keys()
)

for player_id in sorted(all_players):

    accelerations = acceleration_data[player_id]
    decelerations = deceleration_data[player_id]

    # Avoid empty lists
    if accelerations:
        average_acceleration = (
            sum(accelerations) / len(accelerations)
        )

        maximum_acceleration = max(
            accelerations
        )

    else:
        average_acceleration = 0
        maximum_acceleration = 0

    if decelerations:
        average_deceleration = (
            sum(decelerations) / len(decelerations)
        )

        maximum_deceleration = max(
            decelerations
        )

    else:
        average_deceleration = 0
        maximum_deceleration = 0

    final_results[str(player_id)] = {

        "average_acceleration_pixels_per_second_squared":
            round(average_acceleration, 2),

        "maximum_acceleration_pixels_per_second_squared":
            round(maximum_acceleration, 2),

        "average_deceleration_pixels_per_second_squared":
            round(average_deceleration, 2),

        "maximum_deceleration_pixels_per_second_squared":
            round(maximum_deceleration, 2),

        "acceleration_events":
            len(accelerations),

        "deceleration_events":
            len(decelerations)
    }


# ==============================
# SAVE JSON
# ==============================

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


print()
print("====================================")
print("ACCELERATION ANALYSIS COMPLETED")
print("====================================")
print(f"Players analyzed: {len(final_results)}")
print(f"Output: {OUTPUT_PATH}")
print("====================================")