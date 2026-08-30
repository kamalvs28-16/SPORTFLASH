from ultralytics import YOLO
import cv2
import math
from collections import defaultdict

print("======================================")
print(" SPORTFLASH CALIBRATED SPEED ANALYSIS")
print("======================================")

# ------------------------------------------------
# SETTINGS
# ------------------------------------------------

MODEL_PATH = "yolo11n.pt"
VIDEO_PATH = "E:\\SPORTFLASH\\videos\\football.mp4"

# Approximate player height.
# Change this if you know the actual average height
# of the players in your video.
PLAYER_HEIGHT_M = 1.75

# Ignore extremely large tracking jumps.
MAX_SPEED_KMH = 40.0

# Minimum player bounding-box height
MIN_PLAYER_HEIGHT_PIXELS = 30

# ------------------------------------------------
# LOAD MODEL
# ------------------------------------------------

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("YOLO model loaded.")

# ------------------------------------------------
# OPEN VIDEO
# ------------------------------------------------

cap = cv2.VideoCapture(VIDEO_PATH)

fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30

print(f"Video FPS: {fps}")

# ------------------------------------------------
# DATA STORAGE
# ------------------------------------------------

previous_positions = {}
previous_heights = {}

player_speeds = defaultdict(list)
player_distances = defaultdict(float)

frame_number = 0

# ------------------------------------------------
# PROCESS VIDEO
# ------------------------------------------------

while True:

    success, frame = cap.read()

    if not success:
        break

    frame_number += 1

    results = model.track(
        frame,
        persist=True,
        conf=0.5,
        verbose=False
    )

    if results[0].boxes.id is None:
        continue

    boxes = results[0].boxes.xyxy.cpu().numpy()

    track_ids = (
        results[0]
        .boxes
        .id
        .int()
        .cpu()
        .tolist()
    )

    for box, player_id in zip(boxes, track_ids):

        x1, y1, x2, y2 = box

        # ------------------------------------------------
        # PLAYER FOOT POSITION
        # ------------------------------------------------

        foot_x = (x1 + x2) / 2
        foot_y = y2

        current_position = (
            foot_x,
            foot_y
        )

        # ------------------------------------------------
        # PLAYER HEIGHT IN PIXELS
        # ------------------------------------------------

        pixel_height = y2 - y1

        if pixel_height < MIN_PLAYER_HEIGHT_PIXELS:
            continue

        # ------------------------------------------------
        # CALCULATE MOVEMENT
        # ------------------------------------------------

        if player_id in previous_positions:

            previous_x, previous_y = (
                previous_positions[player_id]
            )

            pixel_distance = math.sqrt(
                (foot_x - previous_x) ** 2 +
                (foot_y - previous_y) ** 2
            )

            # ------------------------------------------------
            # ESTIMATE METERS PER PIXEL
            # ------------------------------------------------

            meters_per_pixel = (
                PLAYER_HEIGHT_M / pixel_height
            )

            # Estimated real-world distance
            distance_m = (
                pixel_distance *
                meters_per_pixel
            )

            # Time between frames
            time_seconds = 1 / fps

            # Speed in m/s
            speed_mps = (
                distance_m /
                time_seconds
            )

            # Convert to km/h
            speed_kmh = (
                speed_mps * 3.6
            )

            # ------------------------------------------------
            # REMOVE UNREALISTIC TRACKING JUMPS
            # ------------------------------------------------

            if speed_kmh <= MAX_SPEED_KMH:

                player_speeds[player_id].append(
                    speed_kmh
                )

                player_distances[player_id] += (
                    distance_m
                )

        previous_positions[player_id] = (
            current_position
        )

        previous_heights[player_id] = (
            pixel_height
        )

cap.release()

# ------------------------------------------------
# RESULTS
# ------------------------------------------------

print("\n")
print("======================================")
print(" SPORTFLASH PLAYER SPEED RESULTS")
print("======================================")

for player_id, speeds in player_speeds.items():

    if len(speeds) == 0:
        continue

    average_speed = (
        sum(speeds) /
        len(speeds)
    )

    maximum_speed = max(speeds)

    total_distance = player_distances[player_id]

    # Activity classification
    if average_speed < 5:
        activity = "LOW"

    elif average_speed < 10:
        activity = "MEDIUM"

    elif average_speed < 18:
        activity = "HIGH"

    else:
        activity = "VERY HIGH"

    print(f"\nPlayer {player_id}")
    print("---------------------------")

    print(
        f"Distance: "
        f"{total_distance:.2f} m"
    )

    print(
        f"Average Speed: "
        f"{average_speed:.2f} km/h"
    )

    print(
        f"Maximum Speed: "
        f"{maximum_speed:.2f} km/h"
    )

    print(
        f"Activity Level: "
        f"{activity}"
    )

print("\n======================================")
print("Speed calibration completed!")
print("======================================")