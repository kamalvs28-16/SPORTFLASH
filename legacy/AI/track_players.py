import os
import json
import cv2
from ultralytics import YOLO

print("======================================")
print("SPORTFLASH PLAYER TRACKING")
print("======================================")

# --------------------------------------------------
# PATHS
# --------------------------------------------------

VIDEO_PATH = r"E:\SPORTFLASH\videos\football.mp4"
MODEL_PATH = r"E:\SPORTFLASH\yolo11n.pt"
OUTPUT_FILE = r"E:\SPORTFLASH\results\tracking_results.json"

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("YOLO MODEL LOADED!")
print("Starting player tracking...")

# --------------------------------------------------
# VIDEO INFORMATION
# --------------------------------------------------

cap = cv2.VideoCapture(VIDEO_PATH)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)

cap.release()

print(f"Total frames: {total_frames}")
print(f"FPS: {fps:.2f}")

# --------------------------------------------------
# TRACK PLAYERS
# --------------------------------------------------

tracking_data = []

results = model.track(
    source=VIDEO_PATH,
    conf=0.5,
    persist=True,
    stream=True,
    verbose=False
)

frame_number = 0

for result in results:

    frame_number += 1

    if result.boxes is None:
        continue

    boxes = result.boxes

    # Track IDs
    if boxes.id is None:
        continue

    ids = boxes.id.cpu().numpy().astype(int)

    # Bounding boxes
    xyxy = boxes.xyxy.cpu().numpy()

    # Class IDs
    classes = boxes.cls.cpu().numpy().astype(int)

    frame_players = []

    for i in range(len(ids)):

        class_id = classes[i]

        # COCO class 0 = person
        if class_id != 0:
            continue

        player_id = int(ids[i])

        x1, y1, x2, y2 = xyxy[i]

        # Bottom-center point of player
        center_x = int((x1 + x2) / 2)
        bottom_y = int(y2)

        player_data = {
            "player_id": player_id,
            "x1": float(x1),
            "y1": float(y1),
            "x2": float(x2),
            "y2": float(y2),
            "center_x": center_x,
            "bottom_y": bottom_y
        }

        frame_players.append(player_data)

    tracking_data.append({
        "frame": frame_number,
        "players": frame_players
    })

    if frame_number % 100 == 0:
        print(f"Processed frame {frame_number}/{total_frames}")

# --------------------------------------------------
# SAVE TRACKING DATA
# --------------------------------------------------

output = {
    "video": VIDEO_PATH,
    "total_frames": total_frames,
    "fps": fps,
    "frames": tracking_data
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(output, f, indent=2)

print()
print("======================================")
print("PLAYER TRACKING COMPLETED")
print("======================================")

print(f"Tracking file saved:")
print(OUTPUT_FILE)

print(f"Frames processed: {frame_number}")

# Count unique players
unique_players = set()

for frame in tracking_data:
    for player in frame["players"]:
        unique_players.add(player["player_id"])

print(f"Unique player IDs detected: {len(unique_players)}")

print()
print("Tracking IDs:")

for player_id in sorted(unique_players):
    print(f"Player {player_id}")

print("======================================")