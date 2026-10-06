from ultralytics import YOLO
import cv2
import math
import json
import os

print("======================================")
print(" SPORTFLASH PLAYER SPEED ANALYSIS")
print("======================================")

# --------------------------------------
# Load YOLO model
# --------------------------------------

print("Loading YOLO model...")

model = YOLO("yolo11n.pt")

print("YOLO model loaded successfully.")

# --------------------------------------
# Video path
# --------------------------------------

video_path = r"E:\SPORTFLASH\videos\football.mp4"

# --------------------------------------
# Get video FPS
# --------------------------------------

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("ERROR: Could not open football video.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)

cap.release()

print(f"Video FPS: {fps}")

if fps <= 0:
    print("ERROR: Could not determine video FPS.")
    exit()

# --------------------------------------
# Store previous player positions
# --------------------------------------

previous_positions = {}

# Store speed values for each player
player_speeds = {}

# --------------------------------------
# YOLO tracking
# --------------------------------------

print("\nAnalyzing player speed...")

results = model.track(
    source=video_path,
    stream=True,
    persist=True,
    conf=0.5,
    classes=[0]
)

# --------------------------------------
# Process every frame
# --------------------------------------

for frame_number, result in enumerate(results):

    # No tracking IDs
    if result.boxes.id is None:
        continue

    boxes = result.boxes.xyxy.cpu().numpy()

    track_ids = (
        result.boxes.id
        .int()
        .cpu()
        .tolist()
    )

    # ----------------------------------
    # Process every detected player
    # ----------------------------------

    for box, player_id in zip(boxes, track_ids):

        x1, y1, x2, y2 = box

        # Center of player
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        current_position = (
            center_x,
            center_y
        )

        # ----------------------------------
        # First time player appears
        # ----------------------------------

        if player_id not in previous_positions:

            previous_positions[player_id] = (
                current_position,
                frame_number
            )

            player_speeds[player_id] = []

            continue

        # ----------------------------------
        # Previous position
        # ----------------------------------

        previous_position, previous_frame = (
            previous_positions[player_id]
        )

        previous_x, previous_y = previous_position

        # ----------------------------------
        # Distance moved in pixels
        # ----------------------------------

        distance = math.sqrt(
            (center_x - previous_x) ** 2
            +
            (center_y - previous_y) ** 2
        )

        # ----------------------------------
        # Number of frames between positions
        # ----------------------------------

        frame_difference = (
            frame_number - previous_frame
        )

        if frame_difference <= 0:
            continue

        # ----------------------------------
        # Time between frames
        # ----------------------------------

        time_seconds = frame_difference / fps

        # ----------------------------------
        # Speed in pixels/sec
        # ----------------------------------

        speed = distance / time_seconds

        # ----------------------------------
        # Store speed
        # ----------------------------------

        player_speeds[player_id].append(speed)

        # ----------------------------------
        # Update position
        # ----------------------------------

        previous_positions[player_id] = (
            current_position,
            frame_number
        )


# ======================================
# Calculate final results
# ======================================

print("\n======================================")
print(" PLAYER SPEED RESULTS")
print("======================================")

speed_results = {}

for player_id, speeds in player_speeds.items():

    if len(speeds) == 0:
        continue

    # Average speed
    average_speed = sum(speeds) / len(speeds)

    # Maximum speed
    maximum_speed = max(speeds)

    # ----------------------------------
    # Display result
    # ----------------------------------

    print(f"\nPlayer {player_id}")

    print(
        f"Average Speed: "
        f"{average_speed:.2f} pixels/sec"
    )

    print(
        f"Maximum Speed: "
        f"{maximum_speed:.2f} pixels/sec"
    )

    # ----------------------------------
    # Store JSON data
    # ----------------------------------

    speed_results[str(player_id)] = {

        "average_speed": round(
            average_speed,
            2
        ),

        "maximum_speed": round(
            maximum_speed,
            2
        )
    }


# ======================================
# Create results folder
# ======================================

os.makedirs(
    "results",
    exist_ok=True
)


# ======================================
# Save JSON
# ======================================

output_file = (
    "results/speed_results.json"
)

with open(
    output_file,
    "w"
) as file:

    json.dump(
        speed_results,
        file,
        indent=4
    )


# ======================================
# Completed
# ======================================

print("\n======================================")
print(" SPEED ANALYSIS COMPLETED")
print("======================================")

print(
    f"Speed results saved to:\n"
    f"{output_file}"
)

print("======================================")