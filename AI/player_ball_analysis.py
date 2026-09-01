from ultralytics import YOLO
import cv2
import math
from collections import defaultdict

print("======================================")
print(" SPORTFLASH PLAYER-BALL ANALYSIS")
print("======================================")

# ---------------------------------------
# SETTINGS
# ---------------------------------------

MODEL_PATH = "yolo11n.pt"
VIDEO_PATH = "E:\\SPORTFLASH\\videos\\football.mp4"
# Maximum distance between player and ball
# for considering a possible interaction.
#
# This is in pixels because your video does
# not have precise field calibration.
MAX_INTERACTION_DISTANCE = 100

# Minimum consecutive frames required
# before counting an interaction.
MIN_INTERACTION_FRAMES = 5

# ---------------------------------------
# LOAD MODEL
# ---------------------------------------

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("YOLO model loaded successfully.")

# ---------------------------------------
# OPEN VIDEO
# ---------------------------------------

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("ERROR: Could not open football video.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30

print(f"Video FPS: {fps}")

# ---------------------------------------
# DATA STORAGE
# ---------------------------------------

# Total frames where player was close to ball
interaction_frames = defaultdict(int)

# Current consecutive interaction frames
current_interaction = defaultdict(int)

# Total estimated possession time
possession_time = defaultdict(float)

# Store previous ball position
previous_ball_position = None

frame_number = 0

# ---------------------------------------
# PROCESS VIDEO
# ---------------------------------------

while True:

    success, frame = cap.read()

    if not success:
        break

    frame_number += 1

    results = model.track(
        frame,
        persist=True,
        conf=0.25,
        verbose=False
    )

    if results[0].boxes is None:
        continue

    boxes = results[0].boxes.xyxy.cpu().numpy()
    classes = results[0].boxes.cls.cpu().numpy()

    track_ids = None

    if results[0].boxes.id is not None:
        track_ids = (
            results[0]
            .boxes
            .id
            .int()
            .cpu()
            .tolist()
        )

    if track_ids is None:
        continue

    # ---------------------------------------
    # FIND PLAYERS AND BALL
    # ---------------------------------------

    players = []
    ball_position = None

    for box, class_id, track_id in zip(
        boxes,
        classes,
        track_ids
    ):

        class_name = model.names[int(class_id)]

        x1, y1, x2, y2 = box

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        if class_name == "person":

            players.append(
                (
                    track_id,
                    center_x,
                    center_y
                )
            )

        elif class_name == "sports ball":

            ball_position = (
                center_x,
                center_y
            )

    # ---------------------------------------
    # PLAYER-BALL ANALYSIS
    # ---------------------------------------

    if ball_position is not None and len(players) > 0:

        ball_x, ball_y = ball_position

        closest_player = None
        closest_distance = float("inf")

        for player_id, player_x, player_y in players:

            distance = math.sqrt(
                (player_x - ball_x) ** 2 +
                (player_y - ball_y) ** 2
            )

            if distance < closest_distance:

                closest_distance = distance
                closest_player = player_id

        # -----------------------------------
        # POSSIBLE INTERACTION
        # -----------------------------------

        if (
            closest_player is not None
            and closest_distance <= MAX_INTERACTION_DISTANCE
        ):

            current_interaction[closest_player] += 1

            interaction_frames[closest_player] += 1

        else:

            # Reset interaction counters
            for player_id in current_interaction:

                current_interaction[player_id] = 0

# ---------------------------------------
# CLOSE VIDEO
# ---------------------------------------

cap.release()

# ---------------------------------------
# CALCULATE POSSESSION TIME
# ---------------------------------------

for player_id, frames in interaction_frames.items():

    if frames < MIN_INTERACTION_FRAMES:
        continue

    possession_time[player_id] = frames / fps

# ---------------------------------------
# RESULTS
# ---------------------------------------

print("\n")
print("======================================")
print(" PLAYER-BALL INTERACTION RESULTS")
print("======================================")

if len(possession_time) == 0:

    print("No significant player-ball interactions found.")

else:

    for player_id, time in sorted(
        possession_time.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        print(f"\nPlayer {player_id}")
        print("---------------------------")

        print(
            f"Estimated Ball Interaction: "
            f"{time:.2f} seconds"
        )

        print(
            f"Interaction Frames: "
            f"{interaction_frames[player_id]}"
        )

print("\n======================================")
print("Player-ball analysis completed!")
print("======================================")